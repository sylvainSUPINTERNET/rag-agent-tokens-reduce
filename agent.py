"""Standalone RAG agent — Supabase vector search + Gemini."""

from __future__ import annotations

import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langgraph.graph import END, START, StateGraph
from langgraph.graph import MessagesState
from supabase import Client, create_client

load_dotenv()

# ── Clients ───────────────────────────────────────────────────────────────────

supabase: Client = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_KEY"],
)

embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-2")

# ── Tools ─────────────────────────────────────────────────────────────────────

@tool
def search_docs(query: str) -> str:
    """Search relevant documents from the vector database for the given query."""
    vector = embeddings.embed_query(query)
    response = supabase.rpc(
        "match_documents_2",
        {"query_embedding": vector, "match_count": 1},
    ).execute()
    return str(response.data)


# ── Graph ─────────────────────────────────────────────────────────────────────

def build_graph():
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        streaming=True,
    )

    agent = create_agent(
        model=llm,
        tools=[search_docs],
        system_prompt="Tu es un assistant qui répond aux questions en cherchant dans la base documentaire.",
        name="rag_agent",
    )

    graph = StateGraph(MessagesState)
    graph.add_node("agent", agent)
    graph.add_edge(START, "agent")
    graph.add_edge("agent", END)

    return graph.compile()


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    app = build_graph()
    q = "Combien coûte le pipe 25mm ?"
    inputs = {"messages": [{"role": "user", "content": q}]}

    for chunk in app.stream(inputs, stream_mode="updates"): # type: ignore
        print(chunk)


if __name__ == "__main__":
    main()
