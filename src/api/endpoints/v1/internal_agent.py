from fastapi import APIRouter, status

from src.agents.agent_manager.agent import internal_agent
from src.config.logs_config import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/internal_agent", status_code=status.HTTP_200_OK)
async def internal_agent_endpoint(query: str = ""):
    """Internal_agent endpoint for v1 API"""
    logger.debug("Internal agent requested")
    result = internal_agent.invoke({"messages": [{"role": "user", "content": query}]})
    return result["messages"]
