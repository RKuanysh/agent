import json
from agent_core import AgentFactory
from agent_core.conversation_manager import ConversationManager

def main():
    """
    Main function to set up and run the customer service agent.
    This function orchestrates the interaction between the user, the router, and the tools.
    """
    try:
        factory = AgentFactory()
        router_agent = factory.create_router_agent()
        response_agent = factory.create_gpt4o_agent()

        # The ConversationManager handles all the logic for tool use and session state.
        manager = ConversationManager(response_agent)

        print("Hello! Welcome to Sierra Outfitters' customer service. Adventure awaits!")
        print("🏔️ How can I help you on your journey today?")
        print("Type 'quit', 'exit', or press Ctrl+C to end the conversation.")

        try:
            while True:
                user_input = input("\nYou: ")
                if user_input.lower() in ["quit", "exit"]:
                    print("Happy trails! 🌲")
                    break
                
                # 1. Use the router to determine intent
                router_response_str = router_agent.get_response(user_input)
                print(f"Router: {router_response_str}")
                
                try:
                    router_decision = json.loads(router_response_str)
                except json.JSONDecodeError:
                    print("Agent: Looks like we've hit a patch of fog! Could you rephrase that for me?")
                    continue

                # 2. The manager handles the logic and returns the final response.
                final_response = manager.handle_router_decision(router_decision, user_input)
                print(f"Agent: {final_response}")
        except KeyboardInterrupt:
            print("\nHappy trails! Thanks for chatting. 🌲")

    except ValueError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
