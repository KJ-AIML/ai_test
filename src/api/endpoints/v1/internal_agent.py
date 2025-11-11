# src/api/endpoints/v1/internal_agent.py
import time
import json
from typing import Dict, Any, List, Union
from fastapi import APIRouter, HTTPException, status

from src.agents.agent_manager.agent import internal_agent
from src.api.schemas.internal_agent import (
    AgentQueryRequest,
    AgentQueryResponse,
    ErrorResponse
)
from src.config.logs_config import get_logger

router = APIRouter()
logger = get_logger(__name__)


def message_to_dict(msg: Any) -> Dict[str, Any]:
    """Convert LangChain message object to dict"""
    if isinstance(msg, dict):
        return msg
    
    # LangChain message objects have these methods/properties
    result = {
        "type": getattr(msg, "type", "unknown"),
        "content": getattr(msg, "content", ""),
    }
    
    # Add optional fields
    if hasattr(msg, "name"):
        result["name"] = msg.name
    if hasattr(msg, "tool_calls"):
        result["tool_calls"] = msg.tool_calls
    if hasattr(msg, "tool_call_id"):
        result["tool_call_id"] = msg.tool_call_id
    if hasattr(msg, "usage_metadata"):
        result["usage_metadata"] = msg.usage_metadata
    
    return result


def parse_tool_result(tool_message: Dict[str, Any]) -> Dict[str, Any]:
    """Parse tool result message into structured format"""
    try:
        content = tool_message.get("content", "{}")
        result = json.loads(content) if isinstance(content, str) else content
        
        tool_name = tool_message.get("name", "unknown")
        tool_type = result.get("tool", "unknown")
        
        parsed = {
            "tool_name": tool_name,
            "tool_type": tool_type
        }
        
        # For search tool (internal_qna)
        if tool_type == "internal_qna":
            parsed["answer"] = result.get("answer")
            parsed["hits"] = result.get("hits", [])
        
        # For summary tool (issue_summary)
        elif tool_type == "issue_summary":
            summary = result.get("summary", {})
            parsed["summary"] = summary
            parsed["reported_issues"] = summary.get("reported_issues", [])
            parsed["affected_features"] = summary.get("affected_features", [])
            parsed["severity"] = summary.get("severity")
        
        return parsed
        
    except Exception as e:
        logger.error(f"Failed to parse tool result: {e}")
        return {
            "tool_name": tool_message.get("name", "unknown"),
            "tool_type": "unknown",
            "raw_content": tool_message.get("content", "")
        }


def extract_structured_response(messages: List[Any]) -> AgentQueryResponse:
    """Extract structured response from LangChain messages"""
    
    # Convert all messages to dicts
    msg_dicts = [message_to_dict(msg) for msg in messages]
    
    # Extract query
    query = ""
    for msg in msg_dicts:
        if msg.get("type") == "human":
            query = msg.get("content", "")
            break
    
    # Extract final answer
    final_answer = ""
    for msg in reversed(msg_dicts):
        if msg.get("type") == "ai" and not msg.get("tool_calls"):
            final_answer = msg.get("content", "")
            break
    
    # Extract tool executions
    tool_executions = []
    tools_used = []
    step = 1
    
    i = 0
    while i < len(msg_dicts):
        msg = msg_dicts[i]
        
        # Find AI message with tool calls
        if msg.get("type") == "ai" and msg.get("tool_calls"):
            for tool_call in msg["tool_calls"]:
                tool_name = tool_call.get("name")
                if tool_name:
                    tools_used.append(tool_name)
                
                # Find corresponding tool result
                tool_result = None
                for j in range(i + 1, len(msg_dicts)):
                    if msg_dicts[j].get("type") == "tool" and msg_dicts[j].get("name") == tool_name:
                        tool_result = parse_tool_result(msg_dicts[j])
                        break
                
                execution = {
                    "step": step,
                    "tool_call": {
                        "tool_name": tool_name,
                        "arguments": tool_call.get("args", {})
                    }
                }
                
                if tool_result:
                    execution["tool_result"] = tool_result
                
                tool_executions.append(execution)
                step += 1
        
        i += 1
    
    # Extract metadata
    metadata = {}
    for msg in reversed(msg_dicts):
        if msg.get("type") == "ai" and msg.get("usage_metadata"):
            usage = msg["usage_metadata"]
            metadata["total_tokens"] = usage.get("total_tokens")
            metadata["input_tokens"] = usage.get("input_tokens")
            metadata["output_tokens"] = usage.get("output_tokens")
            break
    
    return AgentQueryResponse(
        query=query,
        tools_used=list(set(tools_used)),
        tool_executions=tool_executions,
        final_answer=final_answer,
        metadata=metadata
    )


@router.post(
    "/query",
    response_model=AgentQueryResponse,
    status_code=status.HTTP_200_OK,
    summary="Query Internal AI Agent",
    description="""
    Query the internal AI agent to get insights from bug reports and user feedback.
    
    The agent will:
    1. Search internal documents for relevant information
    2. Analyze and summarize findings
    3. Return structured insights with references
    
    **Example queries:**
    - "What did users say about the search bar?"
    - "What are the issues reported on email notification?"
    - "Show me bugs related to file upload"
    """,
    responses={
        200: {
            "description": "Successful response with structured insights",
            "content": {
                "application/json": {
                    "example": {
                        "query": "What did users say about the search bar?",
                        "tools_used": ["search_internal_qa_tool"],
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
                                    "answer": "Found search-related feedback",
                                    "hits": [{"text": "Feedback #48: ...", "score": 0.89}]
                                }
                            }
                        ],
                        "final_answer": "**Summary:**\nFound 2 issues...\n\n**References:**\n- Feedback #48: ...",
                        "metadata": {"total_tokens": 1500}
                    }
                }
            }
        },
        500: {
            "model": ErrorResponse,
            "description": "Internal server error"
        }
    }
)
async def query_agent(request: AgentQueryRequest) -> AgentQueryResponse:
    """
    Query the internal AI agent with a question about bugs or user feedback.
    """
    start_time = time.time()
    
    logger.info(f"Agent query: {request.query[:50]}...")
    
    try:
        # Invoke agent
        result = internal_agent.invoke({
            "messages": [{"role": "user", "content": request.query}]
        })
        
        messages = result.get("messages", [])
        
        # Extract structured response
        response = extract_structured_response(messages)
        
        # Add execution time
        execution_time = (time.time() - start_time) * 1000
        response.metadata["execution_time_ms"] = round(execution_time, 2)
        
        logger.info(f"Agent query completed in {execution_time:.2f}ms")
        return response
        
    except Exception as e:
        logger.error(f"Agent error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error="Agent execution failed",
                detail=str(e)
            ).model_dump()
        )


@router.get(
    "/internal_agent",
    summary="Legacy Agent Endpoint",
    description="This endpoint is deprecated. Use POST /query instead.",
)
async def internal_agent_endpoint(query: str = ""):
    """Internal_agent endpoint for v1 API"""
    logger.debug("Internal agent requested")
    result = internal_agent.invoke({"messages": [{"role": "user", "content": query}]})
    return result["messages"]