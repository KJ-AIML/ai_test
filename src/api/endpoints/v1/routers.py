from fastapi import APIRouter

# Import v1 endpoints
from src.api.endpoints.v1 import health, internal_agent

# Create v1 router
v1_router = APIRouter()

# Include v1 endpoints
v1_router.include_router(health.router, prefix="/health")
v1_router.include_router(internal_agent.router, prefix="/internal_agent")
