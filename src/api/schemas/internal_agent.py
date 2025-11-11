from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field


class ToolCall(BaseModel):
    """Information about a tool that was called"""
    tool_name: str = Field(..., description="Name of the tool called")
    arguments: Dict[str, Any] = Field(..., description="Arguments passed to the tool")
    
    class Config:
        json_schema_extra = {
            "example": {
                "tool_name": "search_internal_qa_tool",
                "arguments": {"query": "search bar"}
            }
        }


class ToolResult(BaseModel):
    """Result returned from a tool execution"""
    tool_name: str = Field(..., description="Name of the tool that returned this result")
    tool_type: Literal["internal_qna", "issue_summary"] = Field(..., description="Type of tool")
    
    # For search tool
    answer: Optional[str] = Field(None, description="Summary answer from search tool")
    hits: Optional[List[Dict[str, Any]]] = Field(None, description="Search results with scores and metadata")
    
    # For summary tool
    summary: Optional[Dict[str, Any]] = Field(None, description="Structured issue summary")
    reported_issues: Optional[List[str]] = Field(None, description="List of reported issues")
    affected_features: Optional[List[str]] = Field(None, description="Affected features/components")
    severity: Optional[str] = Field(None, description="Severity level (Low/Medium/High/Critical)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "tool_name": "search_internal_qa_tool",
                "tool_type": "internal_qna",
                "answer": "Key findings for 'search bar': Users blocked after few searches (Feedback #48)...",
                "hits": [
                    {
                        "text": "Feedback #48: I got blocked from searching...",
                        "score": 0.89,
                        "metadata": {"source": "ai_test_user_feedback.txt"}
                    }
                ]
            }
        }


class AgentQueryRequest(BaseModel):
    """Request to query the internal AI agent"""
    query: str = Field(
        ..., 
        description="Question to ask the agent about bugs or user feedback",
        min_length=1,
        examples=["What did users say about the search bar?"]
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What did users say about the search bar?"
            }
        }


class AgentQueryResponse(BaseModel):
    """Structured response from the internal AI agent"""
    
    query: str = Field(..., description="Original user query")
    
    tools_used: List[str] = Field(
        default=[],
        description="List of tools called during execution"
    )
    
    tool_executions: List[Dict[str, Any]] = Field(
        default=[],
        description="Detailed information about each tool call and its result"
    )
    
    final_answer: str = Field(
        ..., 
        description="Agent's final answer in readable format with references"
    )
    
    metadata: Dict[str, Any] = Field(
        default={},
        description="Additional metadata (tokens used, execution time, etc.)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "What did users say about the search bar?",
                "tools_used": ["search_internal_qa_tool", "summarize_issues_tool"],
                "tool_executions": [
                    {
                        "step": 1,
                        "tool_call": {
                            "tool_name": "search_internal_qa_tool",
                            "arguments": {"query": "search bar"}
                        },
                        "tool_result": {
                            "tool_name": "search_internal_qa_tool",
                            "tool_type": "internal_qna",
                            "answer": "Found 3 search-related issues from user feedback",
                            "hits": [
                                {
                                    "text": "Feedback #48: I got blocked from searching...",
                                    "score": 0.89
                                }
                            ]
                        }
                    },
                    {
                        "step": 2,
                        "tool_call": {
                            "tool_name": "summarize_issues_tool",
                            "arguments": {"issue_text": "Feedback #48: ..."}
                        },
                        "tool_result": {
                            "tool_name": "summarize_issues_tool",
                            "tool_type": "issue_summary",
                            "summary": {
                                "reported_issues": ["Users blocked after few searches", "Unhelpful error messages"],
                                "affected_features": ["Search rate limiter", "Error messaging"],
                                "severity": "High"
                            }
                        }
                    }
                ],
                "final_answer": "**Summary:**\nFound 2 search-related issues...\n\n**Key Issues:**\n- Users blocked after few searches (High) [Feedback #48]\n\n**References:**\n- Feedback #48: 'I got blocked from searching...'",
                "metadata": {
                    "total_tokens": 1500,
                    "execution_time_ms": 2345.67
                }
            }
        }


class ErrorResponse(BaseModel):
    """Error response when agent execution fails"""
    error: str = Field(..., description="Error type")
    detail: str = Field(..., description="Detailed error message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Agent execution failed",
                "detail": "Vector store connection timeout"
            }
        }