# openai_agent_executor.py

import asyncio
from loguru import logger

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.types import (
    Task,
    TaskArtifactUpdateEvent,
    TaskState,
    TaskStatus,
    TaskStatusUpdateEvent,
)
from a2a.utils import new_task, new_agent_text_message, new_text_artifact

from test_agent_cli import tavily_agent, Runner

class OpenAIAgentExecutor(AgentExecutor):
    def __init__(self) -> None:
        pass

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        query: str = context.get_user_input()
        task: Task | None = context.current_task

        if not context.message:
            raise Exception("No message in context")

        if not task:
            task = new_task(context.message)

        conversation_history = [{"role": "user", "content": query}]
        
        try:
            logger.info("Starting agent execution...")
            run_result = await Runner.run(tavily_agent, conversation_history)

            if run_result and run_result.final_output:
                logger.info("Agent execution finished, creating artifact.")
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
        logger.warning(f"Cancel operation was called for task {context.current_task.id}, but is not implemented.")
        pass