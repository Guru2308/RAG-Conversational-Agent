from fastapi import FastAPI
from app.routes import chat
from app.core.llm_client import LLM_GATEWAY_URL, API_KEY
import os

app = FastAPI(
    title="AI Conversational Agent",
    description="Chatbot service with semantic search integration",
    version="1.0.0",
)

# Include routers
app.include_router(chat.router, prefix="/chat", tags=["Chat"])


@app.get("/")
def root():
    return {
        "message": "AI Conversational Agent is running",
        "search_service_connected": True,
        "llm_gateway_configured": bool(LLM_GATEWAY_URL and API_KEY),
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "chatbot",
        "search_service_url": "http://localhost:8000",
    }
