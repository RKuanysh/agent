import json
from .customer_tools import GetOrderStatusTool, GetProductRecommendationTool, GetEarlyRiserPromotionTool

class ConversationManager:
    """
    Manages the conversation state, including multi-turn argument collection
    and tool execution.
    """
    def __init__(self, response_agent):
        self.response_agent = response_agent
        self.session_context = {
            "tool_name": None,
            "arguments": {}
        }
        self.tools = {
            "get_order_status": GetOrderStatusTool(),
            "get_product_recommendation": GetProductRecommendationTool(),
            "get_early_riser_promotion": GetEarlyRiserPromotionTool(),
        }

    def handle_router_decision(self, router_decision: dict, user_input: str) -> str:
        """
        Processes the router's decision, collects arguments if necessary,
        executes tools, and returns a user-facing response.
        """
        try:
            current_tool_name = router_decision.get("tool")
            current_arguments = router_decision.get("arguments", {})
        except (json.JSONDecodeError, AttributeError):
            self.reset_session()
            return "I'm having a little trouble understanding. Could you rephrase?"

        # Merge new arguments with session context if it's the same tool
        if current_tool_name == self.session_context["tool_name"]:
            for key, value in current_arguments.items():
                if value is not None:
                    self.session_context["arguments"][key] = value
        else: # It's a new tool, so reset the session context
            self.reset_session()
            self.session_context["tool_name"] = current_tool_name
            self.session_context["arguments"] = current_arguments

        # --- Argument Collection and Execution ---
        tool_name_to_execute = self.session_context["tool_name"]
        arguments_to_execute = self.session_context["arguments"]

        tool_instance = self.tools.get(tool_name_to_execute)

        if tool_instance:
            missing_arg_prompt = tool_instance.get_missing_argument_prompt(arguments_to_execute)
            if missing_arg_prompt:
                return missing_arg_prompt
        
        # Handle single-turn tools or general conversation
        if tool_name_to_execute == "general_conversation":
            self.reset_session()
            return self.response_agent.get_response(user_input)
        
        if tool_name_to_execute == "off_topic":
            self.reset_session()
            return "I'm sorry, I can only help with questions about orders, products, and promotions. How can I assist you with those topics?"

        # Execute the tool if it exists and all args are gathered
        if tool_instance:
            tool_result = tool_instance.execute(**arguments_to_execute)
            # Get specific formatting instructions from the tool, if any.
            response_instructions = tool_instance.get_response_instructions()
            final_prompt = f"{response_instructions}\nThe user asked: '{user_input}'. The result from the tool is: {tool_result}. Please formulate a friendly, natural language response to the user based on this information."
            final_response = self.response_agent.get_response(final_prompt)
            self.reset_session() # Clear context after successful execution
            return final_response

        self.reset_session()
        return "I'm sorry, I can't do that."

    def reset_session(self):
        """Resets the session context."""
        self.session_context = {
            "tool_name": None,
            "arguments": {}
        }