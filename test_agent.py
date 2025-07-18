# FILE: test_agent.py

import json
from agents.run import Runner
from agent import tavily_agent
# This is the correct, evidence-based import path.
# from a2a.types import Message

if __name__ == "__main__":
    # A query that will force the agent to use the search tool
    test_query = "What is the latest transfer news for Chelsea FC in 2025?"
    
    print(f"--- Running a single test with query: '{test_query}' ---")

    # Pass the query string directly to Runner.run_sync
    result = Runner.run_sync(tavily_agent, test_query)
    
    # This is the crucial part: Get the full history and print it
    full_history = result.to_input_list()

    print("\n--- AGENT EXECUTION HISTORY (The data we need to inspect) ---")
    # Pretty-print the JSON so we can easily see the structure
    print(json.dumps(full_history, indent=2))
    print("-----------------------------------------------------------\n")

    print(f"Final Output: {result.final_output}")