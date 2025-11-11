from langchain.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage

from src.agents.prompts.summarize_issues_prompt import get_prompt_summarize_issues
from src.agents.types.types import (
    InternalQnAResponse,
    IssueSummary,
    IssueSummaryResponse,
    QnaHit,
)
from src.data.rag.vector_store import get_vector_store
from src.models.langchain_model_loader import LangchainModelLoader

loader = LangchainModelLoader()
openai_basic_model = loader.init_model_openai_basic()
summarize_issues_prompt = get_prompt_summarize_issues()


# ----------------------------
# Tool 1: Internal Q&A Tool
# ----------------------------
@tool("search_internal_qa_tool")
def search_internal_qa_tool(query: str) -> dict:
    """Search internal documents (bug reports & user feedback) and return structured hits."""
    vector_store = get_vector_store()

    try:
        hits = vector_store.similarity_search_with_relevance_scores(query, k=5)
        results = [
            QnaHit(
                text=doc.page_content,
                score=float(score) if score is not None else 0.0,
                metadata=dict(doc.metadata or {}),
            ).model_dump()
            for doc, score in hits
        ]
    except Exception:
        docs = vector_store.similarity_search(query, k=3)
        results = [
            QnaHit(
                text=d.page_content,
                score=0.0,
                metadata=dict(d.metadata or {}),
            ).model_dump()
            for d in docs
        ]

    if results:
        key_points = "\n".join(f"- {h['text']}" for h in results[:3])
        answer = f"Key findings for '{query}':\n{key_points}"
    else:
        answer = "No relevant information found in internal docs."

    payload = InternalQnAResponse(
        rationale="User asked a retrieval-style question; returning top matches.",
        answer=answer,
        hits=[QnaHit(**h) for h in results],
    ).model_dump()

    return payload


# ----------------------------
# Tool 2: Issue Summary Tool
# ----------------------------
@tool("summarize_issues_tool")
def summarize_issues_tool(issue_text: str) -> dict:
    """Summarize reported issues with structured JSON (reported_issues, affected_features, severity)."""
    structured_model = openai_basic_model.with_structured_output(IssueSummary)

    messages = [
        SystemMessage(content=summarize_issues_prompt),
        HumanMessage(content=f"Analyze and summarize these issues:\n\n{issue_text}"),
    ]
    result: IssueSummary = structured_model.invoke(messages)

    response = IssueSummaryResponse(
        rationale="User provided raw issue text; summarized into structured fields.",
        summary=result,
        evidence=None,
        suggested_fixes=None,
        confidence=None,
    ).model_dump()

    return response
