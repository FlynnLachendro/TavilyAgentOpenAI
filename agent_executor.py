# FILE: agent_executor.py

import json
from loguru import logger
from typing import cast, Any

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.types import (
    Message,
    Part,
    Role,
    Task,
    TaskArtifactUpdateEvent,
    TaskState,
    TaskStatus,
    TaskStatusUpdateEvent,
    DataPart,
)
from a2a.utils import new_task, new_agent_text_message, new_text_artifact

from agent import tavily_agent
from agents.run import Runner

class OpenAIAgentExecutor(AgentExecutor):
    def __init__(self) -> None:
        pass

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        """
        Executes the agent logic and streams events back to the A2A UI.
        This is the final, correct, and type-safe implementation.
        """
        query: str = context.get_user_input()
        task: Task | None = context.current_task
        
        if not context.message:
            raise Exception("No message in context")

        if not task:
            task = new_task(context.message)
        if not task:
            raise Exception("Task could not be created from context.message")

        try:
            logger.info("Starting agent execution...")
            run_result = await Runner.run(tavily_agent, query)
            
            full_history = run_result.to_input_list()
            tool_call_info = {} 

            for turn in full_history:
                turn_type = turn.get("type")

                if turn_type == "function_call":
                    tool_name = turn.get("name")
                    tool_call_id = turn.get("call_id")
                    
                    if not all([tool_name, tool_call_id]):
                        continue

                    tool_call_info[tool_call_id] = tool_name
                    logger.info(f"Streaming tool call to A2AUI: {tool_name}")
                    
                    # --- Robustly handle tool arguments ---
                    tool_args = turn.get("arguments")
                    tool_args_dict = {}
                    if isinstance(tool_args, str):
                        try:
                            tool_args_dict = json.loads(tool_args)
                        except json.JSONDecodeError:
                            tool_args_dict = {"args": tool_args}
                    elif isinstance(tool_args, dict):
                        tool_args_dict = tool_args

                    tool_call_message = Message(
                        messageId=f"msg-{task.id}-{tool_call_id}-call",
                        taskId=task.id,
                        contextId=task.contextId,
                        role=Role.agent,
                        metadata={"type": "tool-call", "toolCallId": tool_call_id, "toolCallName": tool_name},
                        parts=[Part(root=DataPart(data=tool_args_dict))]
                    )
                    
                    await event_queue.enqueue_event(TaskStatusUpdateEvent(
                        status=TaskStatus(state=TaskState.working, message=tool_call_message),
                        final=False, contextId=task.contextId, taskId=task.id
                    ))

                elif turn_type == "function_call_output":
                    tool_call_id = turn.get("call_id")
                    tool_name = tool_call_info.get(tool_call_id, "unknown_tool")

                    if not tool_call_id:
                        continue

                    logger.info(f"Streaming tool call result to A2AUI for: {tool_name}")

                    # --- Type-safe handling of tool output ---
                    tool_output = turn.get("output")
                    tool_output_dict = {}
                    if isinstance(tool_output, dict) and all(isinstance(k, str) for k in tool_output.keys()):
                        tool_output_dict = tool_output
                    else:
                        tool_output_dict = {"output": str(tool_output)}

                    tool_result_message = Message(
                        messageId=f"msg-{task.id}-{tool_call_id}-result",
                        taskId=task.id,
                        contextId=task.contextId,
                        role=Role.agent,
                        metadata={"type": "tool-call-result", "toolCallId": tool_call_id, "toolCallName": tool_name},
                        parts=[Part(root=DataPart(data=cast(dict[str, Any], tool_output_dict)))]
                    )

                    await event_queue.enqueue_event(TaskStatusUpdateEvent(
                        status=TaskStatus(state=TaskState.working, message=tool_result_message),
                        final=False, contextId=task.contextId, taskId=task.id
                    ))

            if run_result and run_result.final_output:
                logger.info("Agent execution finished, sending final response.")
                final_output_text = str(run_result.final_output)

                final_artifact = new_text_artifact(
                    name="OpenAI Agent Result",
                    description=f"Result for query: {query}",
                    text=final_output_text,
                )
                await event_queue.enqueue_event(TaskArtifactUpdateEvent(artifact=final_artifact, contextId=task.contextId, taskId=task.id))
                
                final_assistant_message = new_agent_text_message(final_output_text, task.contextId, task.id)
                
                await event_queue.enqueue_event(TaskStatusUpdateEvent(
                    status=TaskStatus(state=TaskState.completed, message=final_assistant_message),
                    final=True, contextId=task.contextId, taskId=task.id
                ))
            else:
                raise Exception("Agent did not produce a final result.")

        except Exception as e:
            logger.error(f"Error during agent execution: {e}", exc_info=True)
            error_message = new_agent_text_message(f"An error occurred: {e}", task.contextId, task.id)
            await event_queue.enqueue_event(TaskStatusUpdateEvent(
                status=TaskStatus(state=TaskState.failed, message=error_message), 
                final=True, contextId=task.contextId, taskId=task.id
            ))
        finally:
            await event_queue.close()

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        if not context.current_task:
            logger.warning("Cancel operation was called but there is no current task in context.")
            return
        logger.warning(f"Cancel operation was called for task {context.current_task.id}, but is not implemented.")
        pass