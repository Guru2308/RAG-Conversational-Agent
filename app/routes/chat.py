from fastapi import APIRouter, HTTPException
from app.schemas.chat import ChatRequest, ChatResponse
from app.core.search_client import fetch_context, fetch_document_embeddings
from app.core.llm_client import generate_response

router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest):
    try:
        # Fetch relevant context from search service
        context = await fetch_context(payload.query, top_k=5)

        # Generate response using LLM with the context
        answer = await generate_response(payload.query, context)

        return ChatResponse(reply=answer, context=context)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/document/{document_id}")
async def get_document_embeddings(document_id: str, page: int | None = None):
    """Proxy endpoint to get document embeddings from search service"""
    try:
        document_data = await fetch_document_embeddings(document_id, page)
        return document_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
