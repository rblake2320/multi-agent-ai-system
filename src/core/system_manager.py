"""
Core System Manager for Multi-Agent AI System
Orchestrates all zones and manages the overall system workflow
"""
import asyncio
import logging
from typing import Dict, Optional, Any
from datetime import datetime

from core.database import SessionLocal, Project
from zone1_hive_collective.hive_manager import HiveCollectiveManager
from zone2_orchestration.orchestration_manager import OrchestrationManager
from zone3_execution_agents.agent_manager_real import ExecutionAgentManager
from zone4_output_assembly.assembly_manager import OutputAssemblyManager
from utils.metrics import MetricsCollector

logger = logging.getLogger(__name__)


class SystemManager:
    """
    Main system manager that coordinates all zones and manages the overall workflow
    """
    
    def __init__(self):
        self.hive_manager: Optional[HiveCollectiveManager] = None
        self.orchestration_manager: Optional[OrchestrationManager] = None
        self.execution_manager: Optional[ExecutionAgentManager] = None
        self.assembly_manager: Optional[OutputAssemblyManager] = None
        self.metrics_collector: Optional[MetricsCollector] = None
        
        self.active_projects: Dict[str, Dict] = {}
        self.system_status = "initializing"
        self.initialized = False
    
    async def initialize(self):
        """Initialize all system components"""
        try:
            logger.info("Initializing system components...")
            
            # Initialize metrics collector
            self.metrics_collector = MetricsCollector()
            await self.metrics_collector.initialize()
            
            # Initialize Zone 1: Hive Collective Intelligence
            self.hive_manager = HiveCollectiveManager()
            await self.hive_manager.initialize()
            logger.info("Zone 1 (Hive Collective) initialized")
            
            # Initialize Zone 2: Orchestration and Routing
            self.orchestration_manager = OrchestrationManager()
            await self.orchestration_manager.initialize()
            logger.info("Zone 2 (Orchestration) initialized")
            
            # Initialize Zone 3: Execution Agents
            self.execution_manager = ExecutionAgentManager()
            await self.execution_manager.initialize()
            logger.info("Zone 3 (Execution Agents) initialized")
            
            # Initialize Zone 4: Output Assembly
            self.assembly_manager = OutputAssemblyManager()
            await self.assembly_manager.initialize()
            logger.info("Zone 4 (Output Assembly) initialized")
            
            # Connect zones
            await self._connect_zones()
            
            self.system_status = "ready"
            self.initialized = True
            logger.info("System initialization complete")
            
        except Exception as e:
            logger.error(f"System initialization failed: {e}")
            self.system_status = "error"
            raise
    
    async def _connect_zones(self):
        """Connect zones for communication"""
        # Set up inter-zone communication channels
        self.orchestration_manager.set_hive_manager(self.hive_manager)
        self.orchestration_manager.set_execution_manager(self.execution_manager)
        self.orchestration_manager.set_assembly_manager(self.assembly_manager)
        
        self.execution_manager.set_orchestration_manager(self.orchestration_manager)
        self.assembly_manager.set_orchestration_manager(self.orchestration_manager)
    
    async def shutdown(self):
        """Shutdown all system components"""
        logger.info("Shutting down system components...")
        
        if self.assembly_manager:
            await self.assembly_manager.shutdown()
        
        if self.execution_manager:
            await self.execution_manager.shutdown()
        
        if self.orchestration_manager:
            await self.orchestration_manager.shutdown()
        
        if self.hive_manager:
            await self.hive_manager.shutdown()
        
        if self.metrics_collector:
            await self.metrics_collector.shutdown()
        
        self.system_status = "shutdown"
        logger.info("System shutdown complete")
    
    async def create_project(self, project_data: Dict[str, Any]) -> str:
        """
        Create a new project and initiate the multi-agent workflow
        
        Args:
            project_data: Project requirements and configuration
            
        Returns:
            Project UUID
        """
        if not self.initialized:
            raise RuntimeError("System not initialized")
        
        try:
            # Create project in database
            db = SessionLocal()
            project = Project(
                name=project_data.get("name", "Untitled Project"),
                description=project_data.get("description", ""),
                requirements=project_data.get("requirements", ""),
                config=project_data.get("config", {}),
                status="created"
            )
            db.add(project)
            db.commit()
            db.refresh(project)
            
            project_uuid = project.uuid
            logger.info(f"Created project {project_uuid}: {project.name}")
            
            # Add to active projects
            self.active_projects[project_uuid] = {
                "project": project,
                "status": "created",
                "created_at": datetime.utcnow(),
                "current_phase": "requirements_analysis"
            }
            
            # Start project workflow
            asyncio.create_task(self._process_project(project_uuid))
            
            db.close()
            return project_uuid
            
        except Exception as e:
            logger.error(f"Failed to create project: {e}")
            raise
    
    async def _process_project(self, project_uuid: str):
        """
        Process a project through the complete multi-agent workflow
        
        Args:
            project_uuid: Project UUID to process
        """
        try:
            logger.info(f"Starting project workflow for {project_uuid}")
            
            # Phase 1: Requirements Analysis (Zone 1 - Hive Collective)
            await self._phase_requirements_analysis(project_uuid)
            
            # Phase 2: Architecture Design (Zone 1 - Hive Collective)
            await self._phase_architecture_design(project_uuid)
            
            # Phase 3: Task Decomposition (Zone 2 - Orchestration)
            await self._phase_task_decomposition(project_uuid)
            
            # Phase 4: Implementation (Zone 3 - Execution Agents)
            await self._phase_implementation(project_uuid)
            
            # Phase 5: Quality Assurance (Zone 3 - Execution Agents)
            await self._phase_quality_assurance(project_uuid)
            
            # Phase 6: Output Assembly (Zone 4 - Output Assembly)
            await self._phase_output_assembly(project_uuid)
            
            # Phase 7: Final Validation (Zone 4 - Output Assembly)
            await self._phase_final_validation(project_uuid)
            
            # Mark project as completed
            await self._complete_project(project_uuid)
            
        except Exception as e:
            logger.error(f"Project workflow failed for {project_uuid}: {e}")
            await self._fail_project(project_uuid, str(e))
    
    async def _phase_requirements_analysis(self, project_uuid: str):
        """Phase 1: Requirements Analysis using Hive Collective Intelligence"""
        logger.info(f"Phase 1: Requirements Analysis for {project_uuid}")
        
        project_data = self.active_projects[project_uuid]
        project_data["status"] = "analyzing_requirements"
        project_data["current_phase"] = "requirements_analysis"
        
        # Get project from database
        db = SessionLocal()
        project = db.query(Project).filter(Project.uuid == project_uuid).first()
        
        # Create debate session for requirements analysis
        debate_result = await self.hive_manager.create_debate_session(
            project_id=project.id,
            topic="Requirements Analysis and Clarification",
            debate_type="requirements_analysis",
            input_data={
                "requirements": project.requirements,
                "description": project.description,
                "config": project.config
            }
        )
        
        # Store results
        project_data["requirements_analysis"] = debate_result
        
        # Update project status
        project.status = "requirements_analyzed"
        db.commit()
        db.close()
        
        logger.info(f"Requirements analysis completed for {project_uuid}")
    
    async def _phase_architecture_design(self, project_uuid: str):
        """Phase 2: Architecture Design using Hive Collective Intelligence"""
        logger.info(f"Phase 2: Architecture Design for {project_uuid}")
        
        project_data = self.active_projects[project_uuid]
        project_data["status"] = "designing_architecture"
        project_data["current_phase"] = "architecture_design"
        
        # Get project from database
        db = SessionLocal()
        project = db.query(Project).filter(Project.uuid == project_uuid).first()
        
        # Create debate session for architecture design
        debate_result = await self.hive_manager.create_debate_session(
            project_id=project.id,
            topic="System Architecture Design",
            debate_type="architecture_design",
            input_data={
                "requirements_analysis": project_data["requirements_analysis"],
                "project_config": project.config
            }
        )
        
        # Store results
        project_data["architecture_design"] = debate_result
        
        # Update project status
        project.status = "architecture_designed"
        db.commit()
        db.close()
        
        logger.info(f"Architecture design completed for {project_uuid}")
    
    async def _phase_task_decomposition(self, project_uuid: str):
        """Phase 3: Task Decomposition using Orchestration Manager"""
        logger.info(f"Phase 3: Task Decomposition for {project_uuid}")
        
        project_data = self.active_projects[project_uuid]
        project_data["status"] = "decomposing_tasks"
        project_data["current_phase"] = "task_decomposition"
        
        # Decompose project into tasks
        tasks = await self.orchestration_manager.decompose_project(
            project_uuid=project_uuid,
            requirements_analysis=project_data["requirements_analysis"],
            architecture_design=project_data["architecture_design"]
        )
        
        project_data["tasks"] = tasks
        
        logger.info(f"Task decomposition completed for {project_uuid}: {len(tasks)} tasks created")
    
    async def _phase_implementation(self, project_uuid: str):
        """Phase 4: Implementation using Execution Agents"""
        logger.info(f"Phase 4: Implementation for {project_uuid}")
        
        project_data = self.active_projects[project_uuid]
        project_data["status"] = "implementing"
        project_data["current_phase"] = "implementation"
        
        # Execute tasks using specialized agents
        implementation_results = await self.orchestration_manager.execute_tasks(
            project_uuid=project_uuid,
            tasks=project_data["tasks"]
        )
        
        project_data["implementation_results"] = implementation_results
        
        logger.info(f"Implementation completed for {project_uuid}")
    
    async def _phase_quality_assurance(self, project_uuid: str):
        """Phase 5: Quality Assurance using Testing Agents"""
        logger.info(f"Phase 5: Quality Assurance for {project_uuid}")
        
        project_data = self.active_projects[project_uuid]
        project_data["status"] = "testing"
        project_data["current_phase"] = "quality_assurance"
        
        # Run comprehensive testing
        qa_results = await self.execution_manager.run_quality_assurance(
            project_uuid=project_uuid,
            implementation_results=project_data["implementation_results"]
        )
        
        project_data["qa_results"] = qa_results
        
        logger.info(f"Quality assurance completed for {project_uuid}")
    
    async def _phase_output_assembly(self, project_uuid: str):
        """Phase 6: Output Assembly using Assembly Manager"""
        logger.info(f"Phase 6: Output Assembly for {project_uuid}")
        
        project_data = self.active_projects[project_uuid]
        project_data["status"] = "assembling"
        project_data["current_phase"] = "output_assembly"
        
        # Assemble final output
        assembly_results = await self.assembly_manager.assemble_project(
            project_uuid=project_uuid,
            implementation_results=project_data["implementation_results"],
            qa_results=project_data["qa_results"]
        )
        
        project_data["assembly_results"] = assembly_results
        
        logger.info(f"Output assembly completed for {project_uuid}")
    
    async def _phase_final_validation(self, project_uuid: str):
        """Phase 7: Final Validation using Assembly Manager"""
        logger.info(f"Phase 7: Final Validation for {project_uuid}")
        
        project_data = self.active_projects[project_uuid]
        project_data["status"] = "validating"
        project_data["current_phase"] = "final_validation"
        
        # Final validation
        validation_results = await self.assembly_manager.validate_project(
            project_uuid=project_uuid,
            assembly_results=project_data["assembly_results"]
        )
        
        project_data["validation_results"] = validation_results
        
        logger.info(f"Final validation completed for {project_uuid}")
    
    async def _complete_project(self, project_uuid: str):
        """Mark project as completed"""
        logger.info(f"Completing project {project_uuid}")
        
        project_data = self.active_projects[project_uuid]
        project_data["status"] = "completed"
        project_data["completed_at"] = datetime.utcnow()
        
        # Update database
        db = SessionLocal()
        project = db.query(Project).filter(Project.uuid == project_uuid).first()
        project.status = "completed"
        project.completed_at = datetime.utcnow()
        db.commit()
        db.close()
        
        logger.info(f"Project {project_uuid} completed successfully")
    
    async def _fail_project(self, project_uuid: str, error_message: str):
        """Mark project as failed"""
        logger.error(f"Failing project {project_uuid}: {error_message}")
        
        project_data = self.active_projects[project_uuid]
        project_data["status"] = "failed"
        project_data["error_message"] = error_message
        project_data["failed_at"] = datetime.utcnow()
        
        # Update database
        db = SessionLocal()
        project = db.query(Project).filter(Project.uuid == project_uuid).first()
        project.status = "failed"
        db.commit()
        db.close()
    
    async def get_project_status(self, project_uuid: str) -> Dict[str, Any]:
        """Get current status of a project"""
        if project_uuid not in self.active_projects:
            # Check database for completed/failed projects
            db = SessionLocal()
            project = db.query(Project).filter(Project.uuid == project_uuid).first()
            db.close()
            
            if not project:
                raise ValueError(f"Project {project_uuid} not found")
            
            return {
                "project_uuid": project_uuid,
                "status": project.status,
                "created_at": project.created_at,
                "completed_at": project.completed_at
            }
        
        project_data = self.active_projects[project_uuid]
        return {
            "project_uuid": project_uuid,
            "status": project_data["status"],
            "current_phase": project_data["current_phase"],
            "created_at": project_data["created_at"],
            "progress": self._calculate_progress(project_data)
        }
    
    def _calculate_progress(self, project_data: Dict) -> float:
        """Calculate project progress percentage"""
        phases = [
            "requirements_analysis",
            "architecture_design", 
            "task_decomposition",
            "implementation",
            "quality_assurance",
            "output_assembly",
            "final_validation"
        ]
        
        current_phase = project_data.get("current_phase", "requirements_analysis")
        
        if project_data["status"] == "completed":
            return 100.0
        elif project_data["status"] == "failed":
            return 0.0
        
        try:
            phase_index = phases.index(current_phase)
            return (phase_index / len(phases)) * 100
        except ValueError:
            return 0.0
    
    async def get_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        return {
            "system_status": self.system_status,
            "initialized": self.initialized,
            "active_projects": len(self.active_projects),
            "zones": {
                "hive_collective": self.hive_manager.get_status() if self.hive_manager else "not_initialized",
                "orchestration": self.orchestration_manager.get_status() if self.orchestration_manager else "not_initialized",
                "execution": self.execution_manager.get_status() if self.execution_manager else "not_initialized",
                "assembly": self.assembly_manager.get_status() if self.assembly_manager else "not_initialized"
            }
        }

