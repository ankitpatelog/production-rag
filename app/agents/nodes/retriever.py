import logfire
from app.agents.state import AgentState
from app.services.retrieval.qdrant_service import search_enterprise_knowledge
from app.services.retrieval.ranking_service import rerank_documents

def retrieve_node(state: AgentState):
    """
    Performs vector search and semantic reranking for technical queries.
    """
    query = state["current_query"]
    
    
    # Standard Retrieval Logic
    with logfire.span("🔍 Knowledge Retrieval"):
        logfire.info(f"Searching Qdrant for: {query}")

        # this def will retrieve the 15 candidate chunks from the vector db
        raw_results = search_enterprise_knowledge(query, limit=15)
        logfire.info(f"Retrieved {len(raw_results)} candidates from Vector DB")
        
        # this is the actual content of the chunks
        doc_contents = [doc['content'] for doc in raw_results]
        
        with logfire.span("⚖️ Semantic Reranking"):
            reranked_contents = rerank_documents(query, doc_contents, top_n=5)
            logfire.info("Reranking complete. Kept top 5 most relevant chunks.")
            
        formatted_docs = [f"CONTENT: {doc}" for doc in reranked_contents]
    
    return {
        "documents": formatted_docs,
        "status": f"Found technical context.",
        "plan": state["plan"] + ["Context Retrieved"]
    }


# User
#  ↓
# Planner
#  ↓
# retrieve_node
#  ↓
# Qdrant
#  ↓
# 15 candidate chunks
#  ↓
# Reranker
#  ↓
# 5 best chunks
#  ↓
# generate_node
#  ↓
# Portkey
#  ↓
# LLM
#  ↓
# # Final Answer



                    # final data flow diagrma form user qur=ery to llm final answer

#                          👤 USER
#                            │
#                            │
#                            │ "How does Kubernetes
#                            │  networking work?"
#                            ▼
#                   ┌─────────────────────┐
#                   │      AgentState     │
#                   │                     │
#                   │  messages           │
#                   │  current_query      │
#                   │  documents          │
#                   │  plan               │
#                   │  status             │
#                   │  final_answer       │
#                   └──────────┬──────────┘
#                              │
#                              ▼
#                   ┌─────────────────────┐
#                   │       PLANNER       │
#                   │      (LLM)          │
#                   │                     │
#                   │ Reads:              │
#                   │ • conversation      │
#                   │ • latest question   │
#                   └──────────┬──────────┘
#                              │
#                              │ Decision
#                              ▼
#                   ┌─────────────────────┐
#                   │  What should happen │
#                   │       next?         │
#                   └──────────┬──────────┘
#                              │
#                   ┌──────────┴──────────┐
#                   │                     │
#                   ▼                     ▼
#           CONVERSATIONAL            TECHNICAL
#                   │                     │
#                   │                     ▼
#                   │            ┌──────────────────┐
#                   │            │    RETRIEVER     │
#                   │            └────────┬─────────┘
#                   │                     │
#                   │                     │ query
#                   │                     ▼
#                   │            ┌──────────────────┐
#                   │            │      QDRANT      │
#                   │            │  Vector Database │
#                   │            └────────┬─────────┘
#                   │                     │
#                   │                     │ 15 candidates
#                   │                     ▼
#                   │            ┌──────────────────┐
#                   │            │     RERANKER     │
#                   │            │                  │
#                   │            │ Semantic ranking │
#                   │            └────────┬─────────┘
#                   │                     │
#                   │                     │ TOP 5
#                   │                     ▼
#                   │            ┌──────────────────┐
#                   │            │     documents    │
#                   │            │   stored in      │
#                   │            │    AgentState    │
#                   │            └────────┬─────────┘
#                   │                     │
#                   └──────────┬──────────┘
#                              │
#                              ▼
#                   ┌─────────────────────┐
#                   │      GENERATOR      │
#                   │                     │
#                   │ Builds final prompt │
#                   │                     │
#                   │ • User question     │
#                   │ • Conversation      │
#                   │ • Retrieved docs    │
#                   │ • Context limit     │
#                   └──────────┬──────────┘
#                              │
#                              │ prompt
#                              ▼
#                   ┌─────────────────────┐
#                   │       PORTKEY       │
#                   │                     │
#                   │ • Cache             │
#                   │ • Retry             │
#                   │ • Fallback          │
#                   │ • Gateway           │
#                   └──────────┬──────────┘
#                              │
#                              ▼
#                   ┌─────────────────────┐
#                   │        LLM          │
#                   │                     │
#                   │ Reason + synthesize │
#                   │ answer from context │
#                   └──────────┬──────────┘
#                              │
#                              │ generated text
#                              ▼
#                   ┌─────────────────────┐
#                   │    final_answer     │
#                   │                     │
#                   │ "Kubernetes         │
#                   │ networking works   │
#                   │ by..."              │
#                   └──────────┬──────────┘
#                              │
#                              ▼
#                          👤 USER