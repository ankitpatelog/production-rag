from app.agents.state import AgentState
from app.gateway import get_langchain_llm
import logfire

# Portkey-backed LLM: fallback + cache + retry — same .invoke() interface as ChatGroq
llm = get_langchain_llm(feature="planner")

def planner_node(state: AgentState):
    """
    The Planner determines if a search is needed based on the ENTIRE conversation.
    """
    # Get the conversation history (excluding the latest message)


    history = ""
    # Example of a message in state["messages"]:
    #state = {
#     "messages": [
#         {"role": "user", "content": "What is Kubernetes?"},
#         {"role": "assistant", "content": "..."},
#         {"role": "user", "content": "What about networking?"}
#     ]
# }


    for msg in state["messages"][:-1]:
        if "role" in msg:
            if msg["role"].lower() == "user":
                role = "User"
            elif msg["role"].lower() == "assistant":
                role = "Assistant"
            else:
                role = msg["role"].capitalize()
        else:
            role = "Unknown"
     

        # Some messages might be missing 'content'; handle this gracefully
        content = msg.get("content", "<no content>")

        history += f"{role}: {content}\n"
 
    
    user_message = state["messages"][-1]["content"] if state["messages"] else ""
    
    prompt = f"""
    You are an intelligent Assistant Planner. 
    Analyze the conversation history and the latest user message.
    
    CONVERSATION HISTORY:
    {history}
    
    LATEST MESSAGE:
    "{user_message}"
    
    Task:
    1. If the latest message is a greeting (hi, hello) or a question that can be answered using ONLY the conversation history above (e.g., "what is my name"), respond with 'CONVERSATIONAL'.
    2. If it is a technical question about Kubernetes, Intel, or Networking that requires fresh documentation, output a refined search query.
    
    Output ONLY 'CONVERSATIONAL' or the search query.
    """
    
    with logfire.span("🧠🔍 Planner Decision"):
        decision = llm.invoke(prompt).content.strip()
        logfire.info(f"Intent identified: {decision}")
    
    if decision == "CONVERSATIONAL":
        return {
            "current_query": "CONVERSATIONAL",
            "status": "Handling conversationally (using memory)...",
            "plan": ["Intent: Conversational/Memory", "Retrieval: Skipped"]
        }
    
    return {
        "current_query": decision,
        "status": f"Technical research needed. Searching for: {decision}",
        "plan": ["Intent: Technical", f"Search Term: {decision}"]
    }




# User message
#      ↓
#    Planner
#      ↓
#  ┌───────────────┐
#  │ Need search?  │
#  └───────────────┘
#     ↓          ↓
#    NO         YES
#     ↓          ↓
# Conversation   Search/RAG