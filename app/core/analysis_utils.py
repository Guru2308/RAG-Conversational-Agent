from typing import Any


def analyze_search_results(query: str, results: list[dict[str, Any]]) -> dict[str, Any]:
    """Analyze search results to provide insights"""
    if not results:
        return {
            "total_results": 0,
            "average_similarity": 0,
            "unique_documents": 0,
            "pages_covered": 0,
        }

    similarities = [
        r.get("similarity_score", 0)
        for r in results
        if r.get("similarity_score") is not None
    ]
    document_ids = set(
        r.get("document_id") for r in results if r.get("document_id") is not None
    )
    pages = set(
        f"{r.get('document_id')}-{r.get('document_page')}"
        for r in results
        if r.get("document_id") is not None and r.get("document_page") is not None
    )

    return {
        "total_results": len(results),
        "average_similarity": sum(similarities) / len(similarities)
        if similarities
        else 0,
        "max_similarity": max(similarities) if similarities else 0,
        "min_similarity": min(similarities) if similarities else 0,
        "unique_documents": len(document_ids),
        "pages_covered": len(pages),
        "query": query,
    }
