from .clients import AbstractClient

class Agent:
    """
    A concrete agent that uses a client and a model to respond to user input.
    It is agnostic of the underlying LLM provider.
    """
    def __init__(self, client: AbstractClient, model: str, system_prompt: str = None, stateful: bool = False):
        self.client = client
        self.model = model
        self.stateful = stateful
        self.messages = []
        if system_prompt:
            self.messages.append({"role": "system", "content": system_prompt})

    def get_response(self, user_input: str) -> str:
        """Gets a response from the configured client and model."""
        if self.stateful:
            # Stateful mode: build up conversation history.
            self.messages.append({"role": "user", "content": user_input})
            
            response_content = self.client.get_completion(self.model, self.messages)
            
            # Add the AI's response to the history to be used in the next turn.
            self.messages.append({"role": "assistant", "content": response_content})
            
            return response_content
        else:
            # Stateless mode: only use system prompt (if any) and current user input.
            messages_to_send = []
            if self.messages and self.messages[0]["role"] == "system":
                messages_to_send.append(self.messages[0])
            messages_to_send.append({"role": "user", "content": user_input})
            return self.client.get_completion(self.model, messages_to_send)
            
