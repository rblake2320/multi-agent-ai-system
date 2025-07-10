"""
Agents API routes for the Multi-Agent AI System
"""
import logging
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.database import get_db, AgentInstance

logger = logging.getLogger(__name__)

router = APIRouter()


class AgentResponse(BaseModel):
    """Response model for agent data"""
    uuid: str
    agent_type: str
    status: str
    tasks_completed: int
    success_rate: float
    created_at: str
    last_active: str


@router.get("/", response_model=List[AgentResponse])
async def list_agents(
    skip: int = 0,
    limit: int = 100,
    agent_type: str = None,
    status: str = None,
    db: Session = Depends(get_db)
):
    """
    List all active agents with optional filtering
    """
    try:
        logger.info(f"Listing agents (skip={skip}, limit={limit}, type={agent_type}, status={status})")
        
        query = db.query(AgentInstance)
        
        if agent_type:
            query = query.filter(AgentInstance.agent_type == agent_type)
        
        if status:
            query = query.filter(AgentInstance.status == status)
        
        agents = query.offset(skip).limit(limit).all()
        
        return [
            AgentResponse(
                uuid=agent.uuid,
                agent_type=agent.agent_type,
                status=agent.status,
                tasks_completed=agent.tasks_completed,
                success_rate=agent.success_rate,
                created_at=agent.created_at.isoformat(),
                last_active=agent.last_active.isoformat()
            )
            for agent in agents
        ]
        
    except Exception as e:
        logger.error(f"Failed to list agents: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list agents: {str(e)}")


@router.get("/{agent_uuid}", response_model=AgentResponse)
async def get_agent(
    agent_uuid: str,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific agent
    """
    try:
        logger.info(f"Getting agent details: {agent_uuid}")
        
        agent = db.query(AgentInstance).filter(AgentInstance.uuid == agent_uuid).first()
        
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        return AgentResponse(
            uuid=agent.uuid,
            agent_type=agent.agent_type,
            status=agent.status,
            tasks_completed=agent.tasks_completed,
            success_rate=agent.success_rate,
            created_at=agent.created_at.isoformat(),
            last_active=agent.last_active.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get agent: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get agent: {str(e)}")


@router.get("/types/available")
async def get_available_agent_types():
    """
    Get list of available agent types
    """
    return {
        "agent_types": [
            "hive_collective",
            "code_generation", 
            "testing_qa",
            "documentation",
            "devops_deployment",
            "security_agent",
            "integration"
        ]
    }

