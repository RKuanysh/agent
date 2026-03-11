from abc import ABC, abstractmethod
from typing import Dict, Optional

class BaseTool(ABC):
    """
    Abstract base class for a tool that the agent can use.
    """

    @abstractmethod
    def get_missing_argument_prompt(self, arguments: Dict) -> Optional[str]:
        """
        Checks if any required arguments are missing and returns a prompt
        to ask the user for the missing information.
        Returns None if all required arguments are present.
        """
        pass

    @abstractmethod
    def execute(self, **kwargs) -> str:
        """Executes the tool with the given arguments."""
        pass

    def get_response_instructions(self) -> str:
        """
        Returns specific instructions for the response agent on how to format this tool's output.
        """
        return "" # Default implementation provides no special instructions.