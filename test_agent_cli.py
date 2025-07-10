# --- Imports and Setup ---
import os
import json
from dotenv import load_dotenv

# Import the key classes and the tool decorator from the new SDK
from agents import Agent, Runner, function_tool as tool

# Import the Tavily client
from tavily import TavilyClient

print("Loading API keys from .env file...")
load_dotenv()

# Initialize the Tavily client.
# The Agents SDK will automatically find and use the OPENAI_API_KEY from the environment.
try:
    tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
    print("Tavily client initialized.")
except KeyError:
    print("FATAL ERROR: Could not find TAVILY_API_KEY in your .env file.")
    print("Please make sure your .env file is set up correctly.")
    exit()

# --- Defining the Search Tool ---

@tool
def tavily_search(query: str):
    """
    Searches the web using the Tavily API for a given query.
    Use this tool for any questions about recent events, facts, or information that requires up-to-date knowledge.

    Args:
        query (str): The search query to find information about.
    """
    print(f"--- AGENT ACTION: Calling Tavily Search with query: '{query}' ---")
    
    try:
        response = tavily_client.search(query=query, search_depth="advanced", max_results=5)
        return response['results']
    except Exception as e:
        return f"Error occurred during Tavily search: {e}"
    
# --- Creating the Agent ---

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

# --- The Main Conversational Loop ---

def run_chat_session():
    """
    Runs a continuous chat loop in the terminal with the Tavily agent.
    """
    print("\nAgent is ready! You can now start the conversation.")
    print("Type 'exit' or 'quit' to end the chat.")
    print("-" * 50)

    conversation_history = []

    while True:
        user_query = input("You: ")
        if user_query.lower() in ['exit', 'quit']:
            print("Ending chat. Goodbye!")
            break

        conversation_history.append({"role": "user", "content": user_query})

        print("Assistant is thinking...")
        result = Runner.run_sync(tavily_agent, conversation_history)
        
        assistant_response = str(result.final_output)
        print(f"\nAssistant: {assistant_response}\n")
        print("-" * 50)

        conversation_history = result.to_input_list()

# This makes the script runnable
if __name__ == "__main__":
    run_chat_session()