"""
Tasks API routes for the Multi-Agent AI System
"""
import logging
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.database import get_db, Task

logger = logging.getLogger(__name__)

router = APIRouter()


class TaskResponse(BaseModel):
    """Response model for task data"""
    uuid: str
    name: str
    description: str
    task_type: str
    status: str
    priority: int
    created_at: str
    started_at: str = None
    completed_at: str = None


@router.get("/", response_model=List[TaskResponse])
async def list_tasks(
    skip: int = 0,
    limit: int = 100,
    task_type: str = None,
    status: str = None,
    project_uuid: str = None,
    db: Session = Depends(get_db)
):
    """
    List all tasks with optional filtering
    """
    try:
        logger.info(f"Listing tasks (skip={skip}, limit={limit}, type={task_type}, status={status})")
        
        query = db.query(Task)
        
        if task_type:
            query = query.filter(Task.task_type == task_type)
        
        if status:
            query = query.filter(Task.status == status)
        
        if project_uuid:
            from core.database import Project
            project = db.query(Project).filter(Project.uuid == project_uuid).first()
            if project:
                query = query.filter(Task.project_id == project.id)
        
        tasks = query.offset(skip).limit(limit).all()
        
        return [
            TaskResponse(
                uuid=task.uuid,
                name=task.name,
                description=task.description,
                task_type=task.task_type,
                status=task.status,
                priority=task.priority,
                created_at=task.created_at.isoformat(),
                started_at=task.started_at.isoformat() if task.started_at else None,
                completed_at=task.completed_at.isoformat() if task.completed_at else None
            )
            for task in tasks
        ]
        
    except Exception as e:
        logger.error(f"Failed to list tasks: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list tasks: {str(e)}")


@router.get("/{task_uuid}", response_model=TaskResponse)
async def get_task(
    task_uuid: str,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific task
    """
    try:
        logger.info(f"Getting task details: {task_uuid}")
        
        task = db.query(Task).filter(Task.uuid == task_uuid).first()
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return TaskResponse(
            uuid=task.uuid,
            name=task.name,
            description=task.description,
            task_type=task.task_type,
            status=task.status,
            priority=task.priority,
            created_at=task.created_at.isoformat(),
            started_at=task.started_at.isoformat() if task.started_at else None,
            completed_at=task.completed_at.isoformat() if task.completed_at else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get task: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get task: {str(e)}")

