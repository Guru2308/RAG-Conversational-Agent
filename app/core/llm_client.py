import httpx
import os

LLM_GATEWAY_URL = os.getenv("LLM_GATEWAY_URL")
API_KEY = os.getenv("LLM_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "default-model")


async def generate_response(query: str, context: list[str]):
    """Generate response using LLM with context from search results"""

    # Build a more informative prompt with the context
    if context:
        context_text = "\n".join([f"- {ctx}" for ctx in context])
        prompt = f"""Based on the following document context, please answer the user's question.

Relevant Documents:
{context_text}

User Question: {query}

Please provide a helpful answer based on the document context provided. If the context doesn't contain enough information to fully answer the question, please state what information is available and what might be missing.

Answer:"""
    else:
        prompt = f"""User Question: {query}

Answer the user's question to the best of your ability. If you don't have enough information, please be honest about the limitations.

Answer:"""

    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "max_tokens": 500,
        "temperature": 0.7,
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{LLM_GATEWAY_URL}/completions", json=payload, headers=headers
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("choices", [{}])[0].get("text", "").strip()

    except httpx.HTTPError as e:
        raise Exception(f"LLM service error: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to generate response: {str(e)}")
