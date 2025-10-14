from fastapi import APIRouter, HTTPException
from app.schemas.chat import ChatRequest, ChatResponse, AnalysisResponse
from app.core.search_client import fetch_search_results, fetch_document_embeddings
from app.core.llm_client import generate_response
from app.core.analysis_utils import analyze_search_results
import logging
from typing import Any

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest):
    try:
        logger.info(f"Received chat request: {payload.query}")

        # Fetch both context and raw results in a single search call
        context, raw_results = await fetch_search_results(payload.query, payload.top_k)
        logger.info(f"Fetched {len(context)} context items in single search")

        # Generate response using LLM with the context and raw results
        answer = await generate_response(payload.query, context, raw_results)
        logger.info("Successfully generated response")

        return ChatResponse(reply=answer, context=context)

    except Exception as e:
        logger.error(f"Chat endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/document/{document_id}")
async def get_document_embeddings(
    document_id: str, page: int | None = None
) -> dict[str, Any]:
    """Proxy endpoint to get document embeddings from search service"""
    try:
        logger.info(f"Fetching embeddings for document: {document_id}, page: {page}")
        document_data = await fetch_document_embeddings(document_id, page)
        return document_data
    except Exception as e:
        logger.error(f"Document embeddings error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze")
async def analyze_search(payload: ChatRequest):
    """Endpoint specifically for search analysis"""
    try:
        logger.info(f"Analysis request: {payload.query}")

        # Fetch results for analysis
        _, raw_results = await fetch_search_results(payload.query, payload.top_k)
        analysis = analyze_search_results(payload.query, raw_results)

        return AnalysisResponse(
            analysis=analysis,
            raw_results=raw_results[:10],
            query=payload.query,
        )

    except Exception as e:
        logger.error(f"Analysis endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
