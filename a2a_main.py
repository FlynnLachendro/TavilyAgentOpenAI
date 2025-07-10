import os
import uvicorn
from dotenv import load_dotenv

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill

from openai_agent_executor import OpenAIAgentExecutor

load_dotenv()

# Agent skill definition
skill = AgentSkill(
    id="openai-search-web",
    name="OpenAI Search Web",
    description="Search the web with Tavily, powered by OpenAI's agent framework.",
    tags=["search", "web", "tavily", "openai"],
    examples=["Who is the CEO of Microsoft?"],
)

port: int = int(os.getenv("PORT", "9998"))
service_url: str = os.getenv("SERVICE_URL", f"http://localhost:{port}")

agent_card = AgentCard(
    name="OpenAI Tavily Agent",
    description="An agent that uses Tavily Search, built with the OpenAI Agents SDK.",
    url=service_url,
    version="1.0.0",
    defaultInputModes=["text", "text/plain"],
    defaultOutputModes=["text", "text/plain"],
    capabilities=AgentCapabilities(),
    skills=[skill],
)

request_handler = DefaultRequestHandler(
    agent_executor=OpenAIAgentExecutor(), 
    task_store=InMemoryTaskStore()
)

server = A2AStarletteApplication(
    agent_card=agent_card, 
    http_handler=request_handler
)

app = server.build()

if __name__ == "__main__":
    print(f"Starting OpenAI Tavily A2A Agent on http://0.0.0.0:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)