# Renamed from openai_agent_executor.py to agent_executor.py
import json
from loguru import logger

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.types import (
    Message,
    Task,
    TaskArtifactUpdateEvent,
    TaskState,
    TaskStatus,
    TaskStatusUpdateEvent,
    TextPart,
    DataPart, # <-- Add this
    Part,     # <-- Add this
    Role,     # <-- Add this
)
from a2a.utils import new_task, new_agent_text_message, new_text_artifact

# Renamed import from agent_logic to agent
from agent import tavily_agent
from agents.run import Runner

class OpenAIAgentExecutor(AgentExecutor):
    # CORRECTED: The constructor method must be __init__ with double underscores.
    def __init__(self) -> None:
        pass

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        query: str = context.get_user_input()
        task: Task | None = context.current_task

        if not context.message:
            raise Exception("No message in context")

        if not task:
            task = new_task(context.message)
        if not task:
            raise Exception("Task could not be created from context.message")

        # Pass the query string directly to Runner.run (not a list of dicts)
        try:
            logger.info("Starting agent execution...")
            run_result = await Runner.run(tavily_agent, query)
            
            # --- Stream Tool Calls to the A2A UI (Using DataPart) ---
            full_history = run_result.to_input_list()
            for turn in full_history:
                if turn.get("type") == "function_call":
                    
                    tool_name = turn.get("name")
                    tool_call_id = turn.get("call_id")
                    tool_arguments = json.loads(turn.get("arguments", "{}"))

                    logger.info(f"Streaming tool call to A2AUI: {tool_name}({tool_arguments})")
                    
                    tool_call_message = Message(
                        messageId=f"msg-{task.id}-{tool_call_id}",
                        taskId=task.id,
                        contextId=task.contextId,
                        role=Role.agent,
                        metadata={
                            "type": "tool-call",
                            "toolCallName": tool_name,
                            "toolCallId": tool_call_id
                        },
                        # The UI wants structured data. We now pass the dictionary
                        # directly into a DataPart, without converting it to a string.
                        parts=[Part(DataPart(data=tool_arguments))]
                    )
                    
                    status_update = TaskStatus(
                        state=TaskState.working, 
                        message=tool_call_message
                    )
                    await event_queue.enqueue_event(
                        TaskStatusUpdateEvent(
                            status=status_update, 
                            final=False, 
                            contextId=task.contextId, 
                            taskId=task.id
                        )
                    )
            
            # --- Send Final Artifact ---
            if run_result and run_result.final_output:
                logger.info("Agent execution finished, creating final artifact.")
                final_output = str(run_result.final_output)

                final_artifact = new_text_artifact(
                    name="OpenAI Agent Result",
                    description=f"Result for query: {query}",
                    text=final_output,
                )
                await event_queue.enqueue_event(TaskArtifactUpdateEvent(artifact=final_artifact, contextId=task.contextId, taskId=task.id))
                await event_queue.enqueue_event(TaskStatusUpdateEvent(status=TaskStatus(state=TaskState.completed), final=True, contextId=task.contextId, taskId=task.id))
            else:
                raise Exception("Agent did not produce a final result.")

        except Exception as e:
            logger.error(f"Error during agent execution: {e}")
            error_message = new_agent_text_message(f"An error occurred: {e}", task.contextId, task.id)
            await event_queue.enqueue_event(TaskStatusUpdateEvent(
                status=TaskStatus(state=TaskState.failed, message=error_message), 
                final=True,
                contextId=task.contextId,
                taskId=task.id
            ))
        finally:
            await event_queue.close()

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        if not context.current_task:
            logger.warning("Cancel operation was called but there is no current task in context.")
            return
        logger.warning(f"Cancel operation was called for task {context.current_task.id}, but is not implemented.")
        pass
