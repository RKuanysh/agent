from abc import ABC, abstractmethod
from typing import List, Dict
from openai import OpenAI

class AbstractClient(ABC):
    """
    Abstract base class for a client that interacts with an LLM provider.
    """
    @abstractmethod
    def get_completion(self, model: str, messages: List[Dict[str, str]]) -> str:
        """
        Gets a completion from the underlying language model.
        This must be implemented by subclasses.
        """
        pass

class OpenAIClient(AbstractClient):
    """A client for interacting with the OpenAI API."""
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def get_completion(self, model: str, messages: List[Dict[str, str]]) -> str:
        completion = self.client.chat.completions.create(
            model=model,
            messages=messages,
        )
        return completion.choices[0].message.content
