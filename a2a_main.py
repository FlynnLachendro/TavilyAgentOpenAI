# a2a_main.py
import os
import uvicorn
from dotenv import load_dotenv

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill

# Import our new OpenAI executor
from openai_agent_executor import OpenAIAgentExecutor

load_dotenv()

# Define the agent's "business card" for the A2A protocol
skill = AgentSkill(
    id="openai-search-web",
    name="OpenAI Search Web",
    description="Search the web with Tavily, powered by OpenAI's agent framework.",
    tags=["search", "web", "tavily", "openai"],
    examples=["Who is the CEO of Microsoft?"],
)

# Use environment variables for port and service URL, just like the deployed version
port: int = int(os.getenv("PORT", "9998")) # We use a different default port (9998)
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

# Create the request handler, this time using our new executor
request_handler = DefaultRequestHandler(
    agent_executor=OpenAIAgentExecutor(), 
    task_store=InMemoryTaskStore()
)

# Create the A2A server application
server = A2AStarletteApplication(
    agent_card=agent_card, 
    http_handler=request_handler
)

app = server.build()

# This part runs the server
if __name__ == "__main__":
    print(f"Starting OpenAI Tavily A2A Agent on http://0.0.0.0:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)