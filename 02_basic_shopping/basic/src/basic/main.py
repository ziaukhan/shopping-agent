import asyncio
import os
from dotenv import load_dotenv
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.teams import RoundRobinGroupChat
from typing import Optional, TypedDict

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

# Why did we use TypedDict here, please read the readme.md file in project
class Product(TypedDict):
    """
    Product model for representing product data.

    Attributes:
        name (str): The name of the product.
        quantity (int): The quantity of the product.
        price (str): The price per unit of the product.
    """
    name: str
    quantity: int
    price: float
    

product_inventory: list[Product] = [Product(name="shoes", quantity=6, price=5), Product(name="shirts", quantity=2, price=10)]
shopping_cart: list[Product] = []


async def get_products_in_inventory()-> list[Product]:
    """Get all the products in the inventory.

       Returns:list[Product] List of Products
    """
    return product_inventory


async def search_product_in_inventory(product_name: str) -> Optional[Product]:
    """Searches the product in product catalog/inventory and return if it is in the inventory.
    
    Parameters:
    product_name (str): the name of the product to search

    Returns:
    Product:Product value if found or None
    """
    for p in product_inventory:
        if(p["name"].lower() == product_name.lower()):
            if(p["quantity"] >= 1):
                return p
    return None
    

async def add_to_shopping_cart(product: Product):
    """Add an object of type product to the shopping cart.

    Parameters:
    product (Product): the product type to add in shopping cart
    
    """
    shopping_cart.append(product)
    for p in product_inventory:
        if(p["name"].lower() == product["name"].lower()):
            p["quantity"] = p["quantity"] - product["quantity"]
    
async def get_shopping_cart() -> list[Product]:
    """Get all the products and items in the shopping cart.
    Returns:
    list[Product]:A list of Products contained in the shopping cart 
    """
    return shopping_cart


# Define an AssistantAgent with the model, tool, system message, and reflection enabled.
# The system message instructs the agent via natural language.
agent: AssistantAgent = AssistantAgent(
    name="shopping_agent",
    model_client=model_client,
    tools=[get_products_in_inventory, search_product_in_inventory, add_to_shopping_cart, get_shopping_cart],
    system_message="You are a helpful shopping assistant.",
    reflect_on_tool_use=True,
    model_client_stream=True,  # Enable streaming tokens from the model client.
)

# Create the team setting a maximum number of turns to 1.
team = RoundRobinGroupChat([agent], max_turns=1)

async def conversation_loop():
    print("Shopping Chat session started! First find out our latest inventory. Type 'exit' or 'quit' to end the conversation.\n")
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
