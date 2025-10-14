from fastapi import FastAPI
from app.routes import chat
from app.config import SEARCH_SERVICE_URL, LLM_GATEWAY_URL, LLM_API_KEY

app = FastAPI(
    title="AI Conversational Agent",
    description="Chatbot service with semantic search integration",
    version="1.0.0",
)

# Include routers
app.include_router(chat.router, prefix="/chat", tags=["Chat"])


@app.get("/")
def root():
    llm_configured = bool(LLM_GATEWAY_URL and LLM_API_KEY)
    return {
        "message": "AI Conversational Agent is running",
        "search_service_connected": True,
        "search_service_url": SEARCH_SERVICE_URL,
        "llm_gateway_configured": llm_configured,
        "note": "LLM responses will show search results even when not configured"
        if not llm_configured
        else "Full AI functionality available",
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    llm_configured = bool(LLM_GATEWAY_URL and LLM_API_KEY)
    return {
        "status": "healthy",
        "service": "chatbot",
        "search_service_url": SEARCH_SERVICE_URL,
        "llm_gateway_configured": llm_configured,
        "capabilities": {
            "semantic_search": True,
            "ai_responses": llm_configured,
            "fallback_responses": True,
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
