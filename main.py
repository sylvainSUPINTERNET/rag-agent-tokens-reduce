"""FastAPI server with SSE streaming for RAG agent."""

from __future__ import annotations

import asyncio
import json
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="RAG Agent Streaming")

# Enable CORS for testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


async def fake_rag_search(query: str):
    """Simulate RAG search - replace with real Supabase search."""
    await asyncio.sleep(0.5)  # Simulate DB latency
    
    # Mock results based on query
    results = {
        "pipe 25mm": "Prix: 15€/m (acier galvanisé)",
        "pipe 32mm": "Prix: 22€/m (acier galvanisé)",
        "coude 90": "Prix: 8,50€ (acier galvanisé)",
    }
    
    for key, value in results.items():
        if key.lower() in query.lower():
            return value
    
    return "Document trouvé: Catalogue tubes aciers 2024 - Page 25"


async def stream_agent_response(query: str, org_id: str):
    """Stream agent response token by token."""
    
    # 1. Search RAG
    docs = await fake_rag_search(query)
    
    # 2. Simulate LLM streaming response
    response_text = f"Voici ce que j'ai trouvé dans vos documents:\n\n{docs}\n\nPrix estimé basé sur votre catalogue."
    
    # 3. Stream each "token"
    for i in range(0, len(response_text), 3):
        chunk = response_text[i:i+3]
        yield f"data: {json.dumps({'type': 'token', 'content': chunk})}\n\n"
        await asyncio.sleep(0.02)  # Simulate token generation delay
    
    # 4. Send metadata
    yield f"data: {json.dumps({'type': 'metadata', 'query': query, 'org_id': org_id})}\n\n"
    
    # 5. Done
    yield f"data: {json.dumps({'type': 'done'})}\n\n"


@app.post("/chat")
async def chat(request: Request):
    """SSE endpoint for chat."""
    body = await request.json()
    query = body.get("query", "")
    org_id = body.get("org_id", "default")
    
    return StreamingResponse(
        stream_agent_response(query, org_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@app.get("/health")
async def health():
    """Health check."""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)