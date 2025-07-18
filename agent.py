# Renamed from agent_logic.py to agent.py
import os
import json
from agents import Agent, function_tool as tool
from tavily import TavilyClient

print("Loading API keys and initializing clients...")

try:
    tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
    print("Tavily client initialized.")
except KeyError:
    print("FATAL ERROR: TAVILY_API_KEY not found in environment. Ensure it's in your .env file or set directly.")
    exit()

@tool
def tavily_search(query: str):
    """
    Searches the web using the Tavily API for a given query.
    Use this for any questions about recent events, facts, or information.
    Args:
        query (str): The search query to find information about.
    """
    print(f"--- AGENT ACTION: Calling Tavily Search with query: '{query}' ---")
    try:
        response = tavily_client.search(query=query, search_depth="advanced", max_results=5)
        # The openai-agents SDK expects the tool to return a string, so we serialize the JSON
        return json.dumps(response['results'])
    except Exception as e:
        return f"Error occurred during Tavily search: {e}"

print("Configuring the agent...")
tavily_agent = Agent(
    name="TavilySearchAssistant",
    instructions=(
        "You are a helpful assistant that can search the web with the Tavily API "
        "and answer questions about the results. If the search tool returns insufficient "
        "results or an error, explain that to the user and ask them to try again "
        "with a more specific query. Format your answers clearly using markdown."
    ),
    model="gpt-4o",
    tools=[tavily_search],
)
print("Agent configured successfully.") 