"""
Zone 1: Hive Collective Intelligence Manager
Manages the strategic decision-making through structured debate and consensus
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

from core.database import SessionLocal, DebateSession, DebateMessage
from zone1_hive_collective.personas.architect import ArchitectPersona
from zone1_hive_collective.personas.innovator import InnovatorPersona
from zone1_hive_collective.personas.pragmatist import PragmatistPersona
from zone1_hive_collective.personas.quality_advocate import QualityAdvocatePersona
from zone1_hive_collective.personas.user_champion import UserChampionPersona
from zone1_hive_collective.debate_engine.debate_coordinator import DebateCoordinator
from zone1_hive_collective.consensus_builder.consensus_engine import ConsensusEngine
from config.settings import settings

logger = logging.getLogger(__name__)


class HiveCollectiveManager:
    """
    Manager for the Hive Collective Intelligence system
    Coordinates strategic decision-making through structured debate
    """
    
    def __init__(self):
        self.personas: Dict[str, Any] = {}
        self.debate_coordinator: Optional[DebateCoordinator] = None
        self.consensus_engine: Optional[ConsensusEngine] = None
        self.active_debates: Dict[str, Dict] = {}
        self.status = "initializing"
    
    async def initialize(self):
        """Initialize the hive collective intelligence system"""
        try:
            logger.info("Initializing Hive Collective Intelligence system...")
            
            # Initialize personas
            self.personas = {
                "architect": ArchitectPersona(),
                "innovator": InnovatorPersona(),
                "pragmatist": PragmatistPersona(),
                "quality_advocate": QualityAdvocatePersona(),
                "user_champion": UserChampionPersona()
            }
            
            # Initialize each persona
            for name, persona in self.personas.items():
                await persona.initialize()
                logger.info(f"Initialized {name} persona")
            
            # Initialize debate coordinator
            self.debate_coordinator = DebateCoordinator(self.personas)
            await self.debate_coordinator.initialize()
            
            # Initialize consensus engine
            self.consensus_engine = ConsensusEngine(self.personas)
            await self.consensus_engine.initialize()
            
            self.status = "ready"
            logger.info("Hive Collective Intelligence system initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Hive Collective Intelligence: {e}")
            self.status = "error"
            raise
    
    async def shutdown(self):
        """Shutdown the hive collective intelligence system"""
        logger.info("Shutting down Hive Collective Intelligence system...")
        
        # Shutdown personas
        for persona in self.personas.values():
            await persona.shutdown()
        
        if self.debate_coordinator:
            await self.debate_coordinator.shutdown()
        
        if self.consensus_engine:
            await self.consensus_engine.shutdown()
        
        self.status = "shutdown"
        logger.info("Hive Collective Intelligence system shutdown complete")
    
    async def create_debate_session(
        self,
        project_id: Optional[int],
        topic: str,
        debate_type: str,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create and execute a debate session
        
        Args:
            project_id: Project ID (None for test sessions)
            topic: Debate topic
            debate_type: Type of debate (requirements_analysis, architecture_design, etc.)
            input_data: Input data for the debate
            
        Returns:
            Debate results and consensus
        """
        try:
            logger.info(f"Creating debate session: {topic}")
            
            # Create debate session in database
            db = SessionLocal()
            debate_session = DebateSession(
                project_id=project_id,
                topic=topic,
                debate_type=debate_type,
                participants=list(self.personas.keys()),
                status="created"
            )
            db.add(debate_session)
            db.commit()
            db.refresh(debate_session)
            
            session_uuid = debate_session.uuid
            logger.info(f"Created debate session {session_uuid}")
            
            # Add to active debates
            self.active_debates[session_uuid] = {
                "session": debate_session,
                "status": "created",
                "created_at": datetime.utcnow(),
                "input_data": input_data
            }
            
            # Start debate process
            debate_result = await self._execute_debate(session_uuid, topic, debate_type, input_data)
            
            # Update session status
            debate_session.status = "completed"
            debate_session.completed_at = datetime.utcnow()
            debate_session.consensus_reached = debate_result.get("consensus_reached", False)
            debate_session.final_decision = debate_result.get("final_decision", {})
            debate_session.confidence_score = debate_result.get("confidence_score", 0.0)
            
            db.commit()
            db.close()
            
            # Remove from active debates
            del self.active_debates[session_uuid]
            
            logger.info(f"Debate session {session_uuid} completed")
            return debate_result
            
        except Exception as e:
            logger.error(f"Failed to create debate session: {e}")
            
            # Mark session as failed
            if 'debate_session' in locals():
                debate_session.status = "failed"
                db.commit()
                db.close()
            
            raise
    
    async def _execute_debate(
        self,
        session_uuid: str,
        topic: str,
        debate_type: str,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute the complete debate process
        
        Args:
            session_uuid: Debate session UUID
            topic: Debate topic
            debate_type: Type of debate
            input_data: Input data for the debate
            
        Returns:
            Debate results and consensus
        """
        try:
            logger.info(f"Executing debate for session {session_uuid}")
            
            # Phase 1: Problem Presentation
            problem_context = await self._present_problem(session_uuid, topic, debate_type, input_data)
            
            # Phase 2: Individual Analysis
            individual_analyses = await self._conduct_individual_analysis(session_uuid, problem_context)
            
            # Phase 3: Collaborative Discussion
            discussion_results = await self._conduct_collaborative_discussion(session_uuid, individual_analyses)
            
            # Phase 4: Synthesis and Integration
            synthesis_results = await self._conduct_synthesis(session_uuid, discussion_results)
            
            # Phase 5: Consensus Building
            consensus_results = await self._build_consensus(session_uuid, synthesis_results)
            
            # Compile final results
            final_results = {
                "session_uuid": session_uuid,
                "topic": topic,
                "debate_type": debate_type,
                "consensus_reached": consensus_results.get("consensus_reached", False),
                "confidence_score": consensus_results.get("confidence_score", 0.0),
                "final_decision": consensus_results.get("final_decision", {}),
                "reasoning": consensus_results.get("reasoning", ""),
                "implementation_guidance": consensus_results.get("implementation_guidance", {}),
                "phases": {
                    "problem_presentation": problem_context,
                    "individual_analysis": individual_analyses,
                    "collaborative_discussion": discussion_results,
                    "synthesis": synthesis_results,
                    "consensus": consensus_results
                }
            }
            
            logger.info(f"Debate execution completed for session {session_uuid}")
            return final_results
            
        except Exception as e:
            logger.error(f"Failed to execute debate for session {session_uuid}: {e}")
            raise
    
    async def _present_problem(
        self,
        session_uuid: str,
        topic: str,
        debate_type: str,
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Phase 1: Present the problem to all personas"""
        logger.info(f"Phase 1: Problem presentation for session {session_uuid}")
        
        problem_context = {
            "topic": topic,
            "debate_type": debate_type,
            "input_data": input_data,
            "context_summary": await self._generate_context_summary(topic, debate_type, input_data),
            "key_considerations": await self._identify_key_considerations(debate_type, input_data),
            "success_criteria": await self._define_success_criteria(debate_type, input_data)
        }
        
        # Store problem presentation message
        await self._store_debate_message(
            session_uuid,
            "system",
            "problem_presentation",
            f"Problem Context: {problem_context['context_summary']}",
            metadata=problem_context
        )
        
        return problem_context
    
    async def _conduct_individual_analysis(
        self,
        session_uuid: str,
        problem_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Phase 2: Each persona analyzes the problem independently"""
        logger.info(f"Phase 2: Individual analysis for session {session_uuid}")
        
        individual_analyses = {}
        
        # Get analysis from each persona
        for persona_name, persona in self.personas.items():
            try:
                analysis = await persona.analyze_problem(problem_context)
                individual_analyses[persona_name] = analysis
                
                # Store analysis message
                await self._store_debate_message(
                    session_uuid,
                    persona_name,
                    "analysis",
                    analysis.get("summary", ""),
                    confidence=analysis.get("confidence", 0.0),
                    reasoning=analysis.get("reasoning", ""),
                    metadata=analysis
                )
                
                logger.info(f"Received analysis from {persona_name}")
                
            except Exception as e:
                logger.error(f"Failed to get analysis from {persona_name}: {e}")
                individual_analyses[persona_name] = {
                    "error": str(e),
                    "confidence": 0.0
                }
        
        return individual_analyses
    
    async def _conduct_collaborative_discussion(
        self,
        session_uuid: str,
        individual_analyses: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Phase 3: Collaborative discussion between personas"""
        logger.info(f"Phase 3: Collaborative discussion for session {session_uuid}")
        
        return await self.debate_coordinator.coordinate_discussion(
            session_uuid,
            individual_analyses
        )
    
    async def _conduct_synthesis(
        self,
        session_uuid: str,
        discussion_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Phase 4: Synthesis and integration of ideas"""
        logger.info(f"Phase 4: Synthesis for session {session_uuid}")
        
        return await self.debate_coordinator.synthesize_ideas(
            session_uuid,
            discussion_results
        )
    
    async def _build_consensus(
        self,
        session_uuid: str,
        synthesis_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Phase 5: Build consensus on final decision"""
        logger.info(f"Phase 5: Consensus building for session {session_uuid}")
        
        return await self.consensus_engine.build_consensus(
            session_uuid,
            synthesis_results
        )
    
    async def _generate_context_summary(
        self,
        topic: str,
        debate_type: str,
        input_data: Dict[str, Any]
    ) -> str:
        """Generate a comprehensive context summary"""
        # This would use an AI model to generate a summary
        # For now, return a structured summary
        return f"Debate Topic: {topic}\nType: {debate_type}\nKey Data: {str(input_data)[:200]}..."
    
    async def _identify_key_considerations(
        self,
        debate_type: str,
        input_data: Dict[str, Any]
    ) -> List[str]:
        """Identify key considerations based on debate type"""
        considerations_map = {
            "requirements_analysis": [
                "Functional requirements clarity",
                "Non-functional requirements",
                "Stakeholder needs",
                "Technical constraints",
                "Business objectives"
            ],
            "architecture_design": [
                "Scalability requirements",
                "Performance considerations",
                "Security requirements",
                "Maintainability",
                "Technology selection"
            ],
            "test": [
                "Evaluation criteria",
                "Comparison factors",
                "Trade-offs",
                "Implementation feasibility"
            ]
        }
        
        return considerations_map.get(debate_type, ["General considerations"])
    
    async def _define_success_criteria(
        self,
        debate_type: str,
        input_data: Dict[str, Any]
    ) -> List[str]:
        """Define success criteria for the debate"""
        criteria_map = {
            "requirements_analysis": [
                "Clear, unambiguous requirements",
                "Complete coverage of stakeholder needs",
                "Feasible implementation plan",
                "Risk mitigation strategies"
            ],
            "architecture_design": [
                "Scalable and maintainable design",
                "Appropriate technology choices",
                "Clear component interfaces",
                "Performance and security considerations"
            ],
            "test": [
                "Objective evaluation",
                "Comprehensive analysis",
                "Clear recommendation",
                "Implementation guidance"
            ]
        }
        
        return criteria_map.get(debate_type, ["Successful resolution"])
    
    async def _store_debate_message(
        self,
        session_uuid: str,
        persona_type: str,
        message_type: str,
        content: str,
        confidence: float = 0.0,
        reasoning: str = "",
        metadata: Dict[str, Any] = None
    ):
        """Store a debate message in the database"""
        try:
            db = SessionLocal()
            
            # Get session
            session = db.query(DebateSession).filter(DebateSession.uuid == session_uuid).first()
            if not session:
                logger.error(f"Session {session_uuid} not found")
                return
            
            # Create message
            message = DebateMessage(
                session_id=session.id,
                persona_type=persona_type,
                message_type=message_type,
                content=content,
                confidence=confidence,
                reasoning=reasoning,
                references=metadata or {}
            )
            
            db.add(message)
            db.commit()
            db.close()
            
        except Exception as e:
            logger.error(f"Failed to store debate message: {e}")
    
    def get_status(self) -> str:
        """Get current status of the hive collective system"""
        return self.status
    
    async def get_active_debates(self) -> Dict[str, Any]:
        """Get information about active debates"""
        return {
            "active_count": len(self.active_debates),
            "debates": {
                uuid: {
                    "topic": debate["session"].topic,
                    "status": debate["status"],
                    "created_at": debate["created_at"].isoformat()
                }
                for uuid, debate in self.active_debates.items()
            }
        }

