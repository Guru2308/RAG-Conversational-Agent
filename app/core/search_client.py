import httpx

SEARCH_SERVICE_URL = "http://localhost:8000"


async def fetch_context(query: str, top_k: int = 5):
    """Fetch relevant context from the search service"""
    async with httpx.AsyncClient() as client:
        # Call the search endpoint
        resp = await client.post(
            f"{SEARCH_SERVICE_URL}/search", json={"query": query, "top_k": top_k}
        )
        resp.raise_for_status()
        results = resp.json()

        # Extract content or metadata to use as context
        # Since the search results don't have actual content, we'll use the metadata
        context = []
        for result in results:
            # Create a descriptive string from available metadata
            context_str = f"Document ID: {result.get('document_id', '')}, Page: {result.get('document_page', '')}, Similarity: {result.get('similarity_score', 0):.4f}"
            context.append(context_str)

        return context


async def fetch_document_embeddings(document_id: str, page: int | None = None):
    """Fetch document details with embeddings"""
    async with httpx.AsyncClient() as client:
        url = f"{SEARCH_SERVICE_URL}/document/{document_id}"
        if page is not None:
            url += f"?page={page}"

        resp = await client.get(url)
        resp.raise_for_status()
        return resp.json()
