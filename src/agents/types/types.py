from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


# ---------- QnA ----------
class QnaHit(BaseModel):
    text: str
    score: float
    metadata: Dict[str, Any] = {}


class InternalQnAResponse(BaseModel):
    tool: Literal["internal_qna"] = "internal_qna"
    rationale: str
    answer: str
    hits: List[QnaHit]


# ---------- Issue Summary ----------
class IssueSummary(BaseModel):
    """Structured summary of reported issues"""

    reported_issues: List[str] = Field(description="List of reported issues")
    affected_features: List[str] = Field(description="Features/components affected")
    severity: Literal["Low", "Medium", "High", "Critical"] = Field(
        description="Severity level: Low, Medium, High, Critical"
    )


class Evidence(BaseModel):
    source: Literal["bug", "feedback", "other"] = "other"
    bug_id: Optional[int] = None
    feedback_id: Optional[int] = None
    section: Optional[
        Literal["title_desc", "steps", "environment", "severity", "fix"]
    ] = None
    snippet: Optional[str] = None
    score: Optional[float] = None


class IssueSummaryResponse(BaseModel):
    tool: Literal["issue_summary"] = "issue_summary"
    rationale: str
    summary: IssueSummary
    evidence: Optional[List[Evidence]] = None
    suggested_fixes: Optional[List[str]] = None
    confidence: Optional[float] = None
