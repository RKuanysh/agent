# Customer Service AI Agent

This project is a smart AI agent designed to help with common customer service questions. It can understand what a user is asking and use a set of tools to find information and provide helpful answers.

## Features

- **Check Order Status**: Look up an order by its number and the customer's email.
- **Get Product Recommendations**: Suggest products based on a category or a specific product name.
- **Share Promotions**: Inform users about special offers, like the "Early Riser" discount.

## Requirements

- Python 3.10 or higher
- Poetry (for managing project dependencies)
- OpenAI API Key

## Setup

1.  **Clone the Project**: Get a copy of the project on your local machine.

2.  **Updated OpenAI API Key**: Replace OpenAI API key in .env file with your own key.

3.  **Install Dependencies**: Navigate to the project folder in your terminal and run:
   ```bash
   poetry install
   ```
    This command will automatically create a dedicated environment for the project and install all the necessary libraries.

## Running the Project

To start the agent, you'll need a main script that imports and uses the `ConversationManager`. Once you have that script (e.g., `main.py`), you can run it with:

```bash
poetry run python main.py
```

## Project Structure

A brief overview of the key files and folders.

```
agent/
├── .venv/           # Virtual environment (created by Poetry)
├── main.py          # Main script
├── pyproject.toml   # Project configuration and dependencies
├── poetry.lock      # Lock file (committed for reproducibility)
├── README.md        # This file
├── agent_core/      # Contains the core logic for the agent and its tools.
├────── __init__.py              # Makes the directory a Python package.
├────── agent.py                 # Defines the agent class that interacts with the LLM.
├────── base_tools.py            # Contains the base class that all tools inherit from.
├────── clients.py               # Manages API clients for communicating with LLM services.
├────── conversation_manager.py  # Orchestrates the conversation, manages state, and executes tools.
├────── customer_tools.py        # Implements the specific tools for customer service tasks.
└────── factory.py               # A factory for creating and configuring different agent instances.
```

## For Others to Run Your Project

1. **Clone the repository**

2. **Install Poetry** (if not already installed):
   ```bash
   pipx install poetry
   # or
   curl -sSL https://install.python-poetry.org | python3 -
   ```

3. **Install dependencies**:
   ```bash
   poetry install
   ```

4. **Run the project**:
   ```bash
   poetry run python main.py
   ```