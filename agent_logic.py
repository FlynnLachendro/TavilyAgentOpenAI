import os
import json
from dotenv import load_dotenv
from agents import Agent, function_tool as tool
from tavily import TavilyClient

print("Loading API keys and initializing clients...")
load_dotenv()

try:
    tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
    print("Tavily client initialized.")
except KeyError:
    print("FATAL ERROR: Could not find TAVILY_API_KEY in your .env file.")
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
        return response['results']
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