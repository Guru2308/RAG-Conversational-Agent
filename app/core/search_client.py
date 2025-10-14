import httpx
import os
from typing import Any

SEARCH_SERVICE_URL = os.getenv("SEARCH_SERVICE_URL", "http://localhost:8000")


async def fetch_search_results(
    query: str, top_k: int | None = 5
) -> tuple[list[str], list[dict[str, Any]]]:
    """Fetch both context and raw results in a single search call"""
    try:
        async with httpx.AsyncClient(timeout=500.0) as client:
            # Call the search endpoint once
            resp = await client.post(
                f"{SEARCH_SERVICE_URL}/search", json={"query": query, "top_k": top_k}
            )
            resp.raise_for_status()
            raw_results: list[dict[str, Any]] = resp.json()

            # Build context from raw results
            context: list[str] = []
            for result in raw_results:
                context_str = (
                    f"Document ID: {result.get('document_id', 'N/A')}, "
                    f"Page: {result.get('document_page', 'N/A')}, "
                    f"Similarity Score: {result.get('similarity_score', 0):.4f}, "
                    f"Tokens: {result.get('tokens', 0)}, "
                    f"Billable Characters: {result.get('billable_characters', 0)}"
                )
                context.append(context_str)

            return context, raw_results

    except httpx.TimeoutException:
        raise Exception(
            "Search service timeout - service is taking too long to respond"
        )
    except httpx.HTTPError as e:
        raise Exception(f"Search service error: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to fetch search results: {str(e)}")


async def fetch_document_embeddings(
    document_id: str, page: int | None = None
) -> dict[str, Any]:
    """Fetch document details with embeddings"""
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            url = f"{SEARCH_SERVICE_URL}/document/{document_id}"
            params = {}
            if page is not None:
                params["page"] = page

            resp = await client.get(url, params=params)
            resp.raise_for_status()
            return resp.json()

    except httpx.HTTPError as e:
        raise Exception(f"Failed to fetch document embeddings: {str(e)}")
