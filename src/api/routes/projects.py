"""
Projects API routes for the Multi-Agent AI System
"""
import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from core.database import get_db, Project
from core.system_manager import SystemManager

logger = logging.getLogger(__name__)

router = APIRouter()


class ProjectCreateRequest(BaseModel):
    """Request model for creating a new project"""
    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    description: str = Field(default="", max_length=1000, description="Project description")
    requirements: str = Field(..., min_length=10, description="Project requirements")
    config: Dict[str, Any] = Field(default_factory=dict, description="Project configuration")


class ProjectResponse(BaseModel):
    """Response model for project data"""
    uuid: str
    name: str
    description: str
    status: str
    created_at: str
    updated_at: str = None
    completed_at: str = None


class ProjectStatusResponse(BaseModel):
    """Response model for project status"""
    project_uuid: str
    status: str
    current_phase: Optional[str] = None
    progress: float = 0.0
    created_at: str
    completed_at: Optional[str] = None
    error_message: Optional[str] = None


@router.post("/", response_model=Dict[str, str])
async def create_project(
    request: ProjectCreateRequest,
    app_request: Request,
    db: Session = Depends(get_db)
):
    """
    Create a new project and start the multi-agent workflow
    """
    try:
        logger.info(f"Creating new project: {request.name}")
        
        # Get system manager from app state
        system_manager: SystemManager = app_request.app.state.system_manager
        
        # Create project
        project_uuid = await system_manager.create_project({
            "name": request.name,
            "description": request.description,
            "requirements": request.requirements,
            "config": request.config
        })
        
        logger.info(f"Project created successfully: {project_uuid}")
        
        return {
            "project_uuid": project_uuid,
            "message": "Project created successfully",
            "status": "created"
        }
        
    except Exception as e:
        logger.error(f"Failed to create project: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create project: {str(e)}")


@router.get("/{project_uuid}/status", response_model=ProjectStatusResponse)
async def get_project_status(
    project_uuid: str,
    app_request: Request
):
    """
    Get the current status of a project
    """
    try:
        logger.info(f"Getting status for project: {project_uuid}")
        
        # Get system manager from app state
        system_manager: SystemManager = app_request.app.state.system_manager
        
        # Get project status
        status = await system_manager.get_project_status(project_uuid)
        
        return ProjectStatusResponse(
            project_uuid=status["project_uuid"],
            status=status["status"],
            current_phase=status.get("current_phase"),
            progress=status.get("progress", 0.0),
            created_at=status["created_at"].isoformat(),
            completed_at=status["completed_at"].isoformat() if status.get("completed_at") else None,
            error_message=status.get("error_message")
        )
        
    except ValueError as e:
        logger.error(f"Project not found: {project_uuid}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get project status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get project status: {str(e)}")


@router.get("/", response_model=List[ProjectResponse])
async def list_projects(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    db: Session = Depends(get_db)
):
    """
    List all projects with optional filtering
    """
    try:
        logger.info(f"Listing projects (skip={skip}, limit={limit}, status={status})")
        
        query = db.query(Project)
        
        if status:
            query = query.filter(Project.status == status)
        
        projects = query.offset(skip).limit(limit).all()
        
        return [
            ProjectResponse(
                uuid=project.uuid,
                name=project.name,
                description=project.description,
                status=project.status,
                created_at=project.created_at.isoformat(),
                updated_at=project.updated_at.isoformat() if project.updated_at else None,
                completed_at=project.completed_at.isoformat() if project.completed_at else None
            )
            for project in projects
        ]
        
    except Exception as e:
        logger.error(f"Failed to list projects: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list projects: {str(e)}")


@router.get("/{project_uuid}", response_model=ProjectResponse)
async def get_project(
    project_uuid: str,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific project
    """
    try:
        logger.info(f"Getting project details: {project_uuid}")
        
        project = db.query(Project).filter(Project.uuid == project_uuid).first()
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return ProjectResponse(
            uuid=project.uuid,
            name=project.name,
            description=project.description,
            status=project.status,
            created_at=project.created_at.isoformat(),
            updated_at=project.updated_at.isoformat() if project.updated_at else None,
            completed_at=project.completed_at.isoformat() if project.completed_at else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get project: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get project: {str(e)}")


@router.delete("/{project_uuid}")
async def delete_project(
    project_uuid: str,
    db: Session = Depends(get_db)
):
    """
    Delete a project (only if not in progress)
    """
    try:
        logger.info(f"Deleting project: {project_uuid}")
        
        project = db.query(Project).filter(Project.uuid == project_uuid).first()
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Check if project can be deleted
        if project.status in ["analyzing", "implementing", "testing"]:
            raise HTTPException(
                status_code=400, 
                detail="Cannot delete project while it's in progress"
            )
        
        db.delete(project)
        db.commit()
        
        logger.info(f"Project deleted successfully: {project_uuid}")
        
        return {"message": "Project deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete project: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete project: {str(e)}")


@router.get("/{project_uuid}/results")
async def get_project_results(
    project_uuid: str,
    app_request: Request
):
    """
    Get the final results of a completed project
    """
    try:
        logger.info(f"Getting results for project: {project_uuid}")
        
        # Get system manager from app state
        system_manager: SystemManager = app_request.app.state.system_manager
        
        # Check if project exists and is completed
        status = await system_manager.get_project_status(project_uuid)
        
        if status["status"] != "completed":
            raise HTTPException(
                status_code=400, 
                detail=f"Project is not completed. Current status: {status['status']}"
            )
        
        # Get project results from active projects or database
        if project_uuid in system_manager.active_projects:
            project_data = system_manager.active_projects[project_uuid]
            return {
                "project_uuid": project_uuid,
                "status": "completed",
                "results": {
                    "requirements_analysis": project_data.get("requirements_analysis"),
                    "architecture_design": project_data.get("architecture_design"),
                    "implementation_results": project_data.get("implementation_results"),
                    "qa_results": project_data.get("qa_results"),
                    "assembly_results": project_data.get("assembly_results"),
                    "validation_results": project_data.get("validation_results")
                }
            }
        else:
            # TODO: Implement retrieval from database/storage
            return {
                "project_uuid": project_uuid,
                "status": "completed",
                "message": "Results are archived. Contact administrator for access."
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get project results: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get project results: {str(e)}")

