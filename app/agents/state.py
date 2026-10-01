from typing import TypedDict, List, Annotated
import operator


class AgentState(TypedDict):
    # List of message dictionaries tracking the conversation history.
    # Using Annotated with operator.add ensures messages are appended rather than replaced.
    messages: Annotated[List[dict], operator.add]
    # The latest query to be answered or processed.
    current_query: str
    # List of document contents or references retrieved for context or answering.
    documents: List[str]
    # Step-by-step plan or actions to be executed in answering the user.
    plan: List[str]
    # Current processing status (e.g., "pending", "retrieving data", "answer ready").
    status: str
    # The generated final answer to the user's query.
    final_answer: str
