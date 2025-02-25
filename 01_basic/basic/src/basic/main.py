import asyncio
import os
from dotenv import load_dotenv
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.teams import RoundRobinGroupChat

# Doc Ref: https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/human-in-the-loop.html#using-max-turns

# Load the environment variables from the .env file
load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")

# Check if the API key is present; if not, raise an error
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set. Please ensure it is defined in your .env file.")


# Define a model client. You can use other model client that implements
# the `ChatCompletionClient` interface.
model_client: OpenAIChatCompletionClient = OpenAIChatCompletionClient(
    model="gemini-2.0-flash",
    api_key=gemini_api_key,
)


# Define a simple function tool that the agent can use.
# For this example, we use a fake weather tool for demonstration purposes.
async def get_weather(city: str) -> str:
    """Get the weather for a given city."""
    return f"The weather in {city} is 73 degrees and Sunny."


# Define an AssistantAgent with the model, tool, system message, and reflection enabled.
# The system message instructs the agent via natural language.
agent: AssistantAgent = AssistantAgent(
    name="weather_agent",
    model_client=model_client,
    tools=[get_weather],
    system_message="You are a helpful assistant.",
    reflect_on_tool_use=True,
    model_client_stream=True,  # Enable streaming tokens from the model client.
)

# Create the team setting a maximum number of turns to 1.
team = RoundRobinGroupChat([agent], max_turns=1)

async def conversation_loop():
    print("Weather Chat session started! Type 'exit' or 'quit' to end the conversation.\n")
    # Loop indefinitely to simulate back-and-forth conversation.
    while True:
        # Get user input from the command line.
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Ending conversation.")
            break

        # Run the conversation and stream to the console.
        stream = team.run_stream(task=user_input)
        
        await Console(stream)
    


# Run the agent and stream the messages to the console.
async def main() -> None:
    await conversation_loop()


def run_main():
    asyncio.run(main())

if __name__ == "__main__":
    run_main()
