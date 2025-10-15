import httpx
import os
from typing import Any
import logging
from app.core.analysis_utils import analyze_search_results

logger = logging.getLogger(__name__)

LLM_GATEWAY_URL = os.getenv("LLM_GATEWAY_URL", "https://llmgateway.qburst.build")
API_KEY = os.getenv("LLM_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o")


async def generate_response(
    query: str, context: list[str], raw_results: list[dict[str, Any]] | None = None
) -> str:
    """Generate response using LLM with context from search results"""

    # Analyze the search results for insights
    analysis = analyze_search_results(query, raw_results or [])

    # Check if LLM is configured
    if not API_KEY:
        logger.warning("LLM API key not configured - using enhanced fallback response")
        return await _generate_fallback_response(query, context, analysis)

    # Build the messages for chat completion
    messages = _build_messages(query, context, analysis)

    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

    payload: dict[str, Any] = {
        "model": MODEL_NAME,
        "messages": messages,
        "max_tokens": 800,
        "temperature": 0.7,
    }

    try:
        logger.info(f"Sending request to LLM gateway: {LLM_GATEWAY_URL}")
        async with httpx.AsyncClient(timeout=500.0) as client:
            resp = await client.post(
                f"{LLM_GATEWAY_URL}/v1/chat/completions", json=payload, headers=headers
            )
            resp.raise_for_status()
            data: dict[str, Any] = resp.json()

            # Extract response from chat completion format
            if "choices" in data and len(data["choices"]) > 0:
                choice = data["choices"][0]
                if "message" in choice and "content" in choice["message"]:
                    return choice["message"]["content"].strip()

            logger.error(f"Unexpected response format: {data}")
            return await _generate_fallback_response(query, context, analysis)

    except httpx.TimeoutException:
        logger.error("LLM service timeout")
        return await _generate_fallback_response(
            query,
            context,
            analysis,
            "The AI analysis service is taking too long to respond.",
        )
    except httpx.HTTPError as e:
        logger.error(f"LLM HTTP error: {str(e)}")
        return await _generate_fallback_response(
            query,
            context,
            analysis,
            "I'm having trouble connecting to the AI analysis service.",
        )
    except Exception as e:
        logger.error(f"LLM general error: {str(e)}")
        return await _generate_fallback_response(
            query, context, analysis, "An error occurred during AI analysis."
        )


def _build_messages(
    query: str, context: list[str], analysis: dict[str, Any]
) -> list[dict[str, str]]:
    """Build the messages array for chat completion"""

    if context:
        context_text = "\n".join([f"- {ctx}" for ctx in context])
        system_content = """You are a helpful AI assistant that analyzes document search results. 
Your task is to help users understand their search results and provide insights about the matching documents."""

        user_content = f"""Please analyze these search results and answer the user's question.

SEARCH QUERY: {query}

SEARCH RESULTS ANALYSIS:
- Total matches: {analysis["total_results"]}
- Best similarity score: {analysis["max_similarity"]:.4f}
- Average similarity: {analysis["average_similarity"]:.4f}
- Unique documents: {analysis["unique_documents"]}

DETAILED SEARCH RESULTS:
{context_text}

USER QUESTION: {query}

Please provide a comprehensive analysis:
1. Assess the relevance and quality of the search results
2. Identify patterns in the matching documents (pages, document types, etc.)
3. Provide insights about what these results might indicate
4. Suggest next steps or how to refine the search if needed

Be helpful, analytical, and focus on the information provided in the search results."""
    else:
        system_content = (
            """You are a helpful AI assistant that helps users with document search."""
        )
        user_content = f"""USER QUESTION: {query}

SEARCH RESULTS: No relevant documents were found.

Please provide helpful guidance on:
1. Why no results might have been found for this query
2. Suggestions for refining the search query
3. Alternative approaches to find the information they need

Be constructive and helpful."""

    return [
        {"role": "system", "content": system_content},
        {"role": "user", "content": user_content},
    ]


async def _generate_fallback_response(
    query: str,
    context: list[str],
    analysis: dict[str, Any],
    error_msg: str | None = None,
) -> str:
    """Generate a fallback response when LLM is not available"""

    if context:
        top_results = context[:3]
        results_text = "\n".join([f"• {ctx}" for ctx in top_results])

        response = f"""**Search Results Analysis**

**Query:** "{query}"

**Summary:**
- Found {analysis["total_results"]} relevant documents
- Best match similarity: {analysis["max_similarity"]:.1%}
- Average similarity: {analysis["average_similarity"]:.1%}
- Across {analysis["unique_documents"]} unique documents

**Top Matches:**
{results_text}"""

        if error_msg:
            response += f"\n\n**Note:** {error_msg} The search results above are still available."
        else:
            response += "\n\n**Note:** The AI analysis feature is currently not configured. To enable intelligent document analysis, please configure the LLM_API_KEY environment variable."

        response += """

**What you can do:**
- Use the document IDs to look up specific documents
- Request embeddings for detailed document analysis
- Refine your search query for better results"""

        return response
    else:
        base_response = f"""**Search Results**

**Query:** "{query}"

No relevant documents were found matching your search criteria.

**Suggestions:**
- Try using different keywords or phrases
- Broaden your search terms
- Check if the documents exist in the database"""

        if error_msg:
            base_response += f"\n\n**Note:** {error_msg}"
        else:
            base_response += (
                "\n\n**Note:** The AI analysis feature is not currently configured."
            )

        return base_response
