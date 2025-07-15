# Renamed from test_agent_cli.py to test_agent.py
import json
from agents.run import Runner
from agent import tavily_agent

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

if __name__ == "__main__":
    run_chat_session() 