"""
Debug API routes for the Multi-Agent AI System
"""
import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from core.system_manager import SystemManager

logger = logging.getLogger(__name__)

router = APIRouter()


class DebugResponse(BaseModel):
    """Response model for debug information"""
    system_status: str
    zones_status: Dict[str, Any]
    active_projects: int
    metrics: Dict[str, Any]


@router.get("/system", response_model=DebugResponse)
async def get_system_debug_info(app_request: Request):
    """
    Get comprehensive system debug information
    """
    try:
        logger.info("Getting system debug information")
        
        # Get system manager from app state
        system_manager: SystemManager = app_request.app.state.system_manager
        
        # Get system status
        status = await system_manager.get_status()
        
        # Get metrics if available
        metrics = {}
        if system_manager.metrics_collector:
            metrics = system_manager.metrics_collector.get_metrics_summary()
        
        return DebugResponse(
            system_status=status["system_status"],
            zones_status=status["zones"],
            active_projects=status["active_projects"],
            metrics=metrics
        )
        
    except Exception as e:
        logger.error(f"Failed to get debug information: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get debug information: {str(e)}")


@router.post("/test-hive")
async def test_hive_collective(app_request: Request):
    """
    Test the hive collective intelligence system
    """
    try:
        logger.info("Testing hive collective intelligence")
        
        # Get system manager from app state
        system_manager: SystemManager = app_request.app.state.system_manager
        
        if not system_manager.hive_manager:
            raise HTTPException(status_code=500, detail="Hive manager not initialized")
        
        # Create a test debate session
        test_result = await system_manager.hive_manager.create_debate_session(
            project_id=None,  # Test session
            topic="Test Debate: Best Programming Language for Web Development",
            debate_type="test",
            input_data={
                "context": "We need to choose a programming language for a new web application",
                "options": ["Python", "JavaScript", "Go", "Rust"],
                "criteria": ["Performance", "Developer Experience", "Ecosystem", "Scalability"]
            }
        )
        
        return {
            "status": "success",
            "message": "Hive collective test completed",
            "result": test_result
        }
        
    except Exception as e:
        logger.error(f"Hive collective test failed: {e}")
        raise HTTPException(status_code=500, detail=f"Hive collective test failed: {str(e)}")


@router.get("/logs/recent")
async def get_recent_logs():
    """
    Get recent system logs for debugging
    """
    try:
        import os
        from pathlib import Path
        
        logs_dir = Path("logs")
        if not logs_dir.exists():
            return {"logs": [], "message": "No logs directory found"}
        
        log_file = logs_dir / "system.log"
        if not log_file.exists():
            return {"logs": [], "message": "No system log file found"}
        
        # Read last 100 lines
        with open(log_file, 'r') as f:
            lines = f.readlines()
            recent_lines = lines[-100:] if len(lines) > 100 else lines
        
        return {
            "logs": [line.strip() for line in recent_lines],
            "total_lines": len(recent_lines),
            "message": f"Retrieved {len(recent_lines)} recent log entries"
        }
        
    except Exception as e:
        logger.error(f"Failed to get recent logs: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get recent logs: {str(e)}")


@router.get("/database/stats")
async def get_database_stats():
    """
    Get database statistics for debugging
    """
    try:
        from core.database import SessionLocal, Project, Task, AgentInstance, DebateSession
        
        db = SessionLocal()
        
        stats = {
            "projects": {
                "total": db.query(Project).count(),
                "by_status": {}
            },
            "tasks": {
                "total": db.query(Task).count(),
                "by_status": {},
                "by_type": {}
            },
            "agents": {
                "total": db.query(AgentInstance).count(),
                "by_status": {},
                "by_type": {}
            },
            "debates": {
                "total": db.query(DebateSession).count(),
                "by_status": {}
            }
        }
        
        # Get project stats by status
        project_statuses = db.query(Project.status, db.func.count(Project.id)).group_by(Project.status).all()
        for status, count in project_statuses:
            stats["projects"]["by_status"][status] = count
        
        # Get task stats
        task_statuses = db.query(Task.status, db.func.count(Task.id)).group_by(Task.status).all()
        for status, count in task_statuses:
            stats["tasks"]["by_status"][status] = count
        
        task_types = db.query(Task.task_type, db.func.count(Task.id)).group_by(Task.task_type).all()
        for task_type, count in task_types:
            if task_type:
                stats["tasks"]["by_type"][task_type] = count
        
        # Get agent stats
        agent_statuses = db.query(AgentInstance.status, db.func.count(AgentInstance.id)).group_by(AgentInstance.status).all()
        for status, count in agent_statuses:
            stats["agents"]["by_status"][status] = count
        
        agent_types = db.query(AgentInstance.agent_type, db.func.count(AgentInstance.id)).group_by(AgentInstance.agent_type).all()
        for agent_type, count in agent_types:
            stats["agents"]["by_type"][agent_type] = count
        
        # Get debate stats
        debate_statuses = db.query(DebateSession.status, db.func.count(DebateSession.id)).group_by(DebateSession.status).all()
        for status, count in debate_statuses:
            stats["debates"]["by_status"][status] = count
        
        db.close()
        
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get database stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get database stats: {str(e)}")

