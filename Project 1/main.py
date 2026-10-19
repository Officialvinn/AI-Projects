from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from dotenv import load_dotenv

load_dotenv()


@tool
def calculator(a: float, b: float) -> str:
    """Useful for adding two numbers together."""
    print("Tool has been called.")
    return f"The sum of {a} and {b} is {a + b}"


@tool
def say_hello(name: str) -> str:
    """Useful for greeting someone."""
    print("Tool has been called.")
    return f"Hello {name}, I hope you are well today!"


def main():
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    tools = [calculator, say_hello]
    agent_executor = create_agent(model, tools)

    print("Welcome! I'm your AI assistant. Type 'exit' to quit.")
    print("You can ask me anything or chat with me.")

    history = []

    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() == "exit":
            break
        if not user_input:
            continue

        history.append(HumanMessage(content=user_input))

        print("\nAssistant: ", end="")
        for chunk in agent_executor.stream({"messages": history}):
            if "model" in chunk and "messages" in chunk["model"]:
                for message in chunk["model"]["messages"]:
                    history.append(message)
                    print(message.content, end="")
            elif "tools" in chunk and "messages" in chunk["tools"]:
                history.extend(chunk["tools"]["messages"])
        print()


if __name__ == "__main__":
    main()
