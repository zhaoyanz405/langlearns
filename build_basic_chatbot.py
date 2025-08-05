import os

from langchain.chat_models import init_chat_model

from typing import Annotated

from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages


class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]


graph_builder = StateGraph(State)

llm = init_chat_model(
    model="deepseek-chat",
    api_key=os.environ["OPENAI_API_KEY"],
)

def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}


graph_builder.add_node(
    "chatbot",
    chatbot,
)


graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

graph = graph_builder.compile()


def steam_graph_updates(user_input: str):
    for event in graph.stream(
        {"messages": [{"role": "user", "content": user_input}]}
    ):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)
        
while True:
    try:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting the chatbot. Goodbye!")
            break

        steam_graph_updates(user_input)
    
    except:
        user_input = "What do you know about the LangGraph library?"
        print("User: ", user_input)

        steam_graph_updates(user_input)
        break
