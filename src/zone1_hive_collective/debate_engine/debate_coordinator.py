"""
Debate Coordinator for Hive Collective Intelligence
Manages structured discussions and collaborative problem-solving
"""
import asyncio
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class DebateCoordinator:
    """
    Coordinates structured debates between personas in the hive collective
    """
    
    def __init__(self, personas: Dict[str, Any]):
        self.personas = personas
        self.discussion_rounds = 3  # Number of discussion rounds
        self.initialized = False
    
    async def initialize(self):
        """Initialize the debate coordinator"""
        self.initialized = True
        logger.info("Debate coordinator initialized")
    
    async def shutdown(self):
        """Shutdown the debate coordinator"""
        self.initialized = False
        logger.info("Debate coordinator shutdown")
    
    async def coordinate_discussion(
        self,
        session_uuid: str,
        individual_analyses: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Coordinate collaborative discussion between personas
        
        Args:
            session_uuid: Debate session UUID
            individual_analyses: Individual analyses from each persona
            
        Returns:
            Discussion results and insights
        """
        try:
            logger.info(f"Coordinating discussion for session {session_uuid}")
            
            discussion_results = {
                "session_uuid": session_uuid,
                "rounds": [],
                "key_agreements": [],
                "key_disagreements": [],
                "emerging_insights": [],
                "areas_for_synthesis": []
            }
            
            # Conduct multiple rounds of discussion
            current_context = individual_analyses
            
            for round_num in range(self.discussion_rounds):
                logger.info(f"Starting discussion round {round_num + 1}")
                
                round_result = await self._conduct_discussion_round(
                    session_uuid,
                    round_num + 1,
                    current_context
                )
                
                discussion_results["rounds"].append(round_result)
                
                # Update context for next round
                current_context = {
                    "previous_analyses": individual_analyses,
                    "previous_rounds": discussion_results["rounds"]
                }
                
                # Check if consensus is emerging
                if await self._check_early_consensus(round_result):
                    logger.info(f"Early consensus detected after round {round_num + 1}")
                    break
            
            # Analyze discussion results
            discussion_results.update(await self._analyze_discussion_results(discussion_results))
            
            logger.info(f"Discussion coordination completed for session {session_uuid}")
            return discussion_results
            
        except Exception as e:
            logger.error(f"Failed to coordinate discussion for session {session_uuid}: {e}")
            raise
    
    async def _conduct_discussion_round(
        self,
        session_uuid: str,
        round_num: int,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Conduct a single round of discussion"""
        logger.info(f"Conducting discussion round {round_num} for session {session_uuid}")
        
        round_result = {
            "round_number": round_num,
            "contributions": {},
            "agreements": [],
            "disagreements": [],
            "challenges": [],
            "improvements": []
        }
        
        # Get contributions from each persona
        for persona_name, persona in self.personas.items():
            try:
                contribution = await persona.participate_in_discussion(
                    {"session_uuid": session_uuid, "round_number": round_num},
                    context
                )
                
                round_result["contributions"][persona_name] = contribution
                
                # Collect agreements, disagreements, etc.
                if "agreements" in contribution:
                    round_result["agreements"].extend(contribution["agreements"])
                if "disagreements" in contribution:
                    round_result["disagreements"].extend(contribution["disagreements"])
                if "challenges" in contribution:
                    round_result["challenges"].extend(contribution["challenges"])
                if "improvements" in contribution:
                    round_result["improvements"].extend(contribution["improvements"])
                
                logger.info(f"Received contribution from {persona_name} for round {round_num}")
                
            except Exception as e:
                logger.error(f"Failed to get contribution from {persona_name}: {e}")
                round_result["contributions"][persona_name] = {
                    "error": str(e),
                    "contribution": f"Failed to participate in round {round_num}"
                }
        
        return round_result
    
    async def _check_early_consensus(self, round_result: Dict[str, Any]) -> bool:
        """Check if early consensus is emerging"""
        # Simple heuristic: if there are significantly more agreements than disagreements
        agreements = len(round_result.get("agreements", []))
        disagreements = len(round_result.get("disagreements", []))
        
        return agreements > 0 and disagreements == 0 and agreements >= 3
    
    async def _analyze_discussion_results(self, discussion_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze overall discussion results"""
        all_agreements = []
        all_disagreements = []
        all_challenges = []
        all_improvements = []
        
        # Collect all items from all rounds
        for round_data in discussion_results["rounds"]:
            all_agreements.extend(round_data.get("agreements", []))
            all_disagreements.extend(round_data.get("disagreements", []))
            all_challenges.extend(round_data.get("challenges", []))
            all_improvements.extend(round_data.get("improvements", []))
        
        # Identify key themes
        key_agreements = await self._identify_key_themes(all_agreements)
        key_disagreements = await self._identify_key_themes(all_disagreements)
        emerging_insights = await self._extract_insights(all_improvements, all_challenges)
        areas_for_synthesis = await self._identify_synthesis_areas(
            key_agreements, key_disagreements, emerging_insights
        )
        
        return {
            "key_agreements": key_agreements,
            "key_disagreements": key_disagreements,
            "emerging_insights": emerging_insights,
            "areas_for_synthesis": areas_for_synthesis
        }
    
    async def _identify_key_themes(self, items: List[str]) -> List[str]:
        """Identify key themes from a list of items"""
        if not items:
            return []
        
        # Simple theme identification (in production, would use NLP)
        # For now, return unique items
        unique_items = list(set(items))
        return unique_items[:5]  # Return top 5 themes
    
    async def _extract_insights(self, improvements: List[str], challenges: List[str]) -> List[str]:
        """Extract key insights from improvements and challenges"""
        insights = []
        
        # Combine and analyze improvements and challenges
        all_items = improvements + challenges
        unique_items = list(set(all_items))
        
        # Return as insights (simplified)
        return unique_items[:3]  # Return top 3 insights
    
    async def _identify_synthesis_areas(
        self,
        agreements: List[str],
        disagreements: List[str],
        insights: List[str]
    ) -> List[str]:
        """Identify areas that need synthesis"""
        synthesis_areas = []
        
        # Areas where there are disagreements need synthesis
        if disagreements:
            synthesis_areas.append("Resolve conflicting viewpoints")
        
        # Areas with many insights need integration
        if len(insights) > 2:
            synthesis_areas.append("Integrate multiple insights")
        
        # If there are both agreements and disagreements
        if agreements and disagreements:
            synthesis_areas.append("Balance agreed principles with disputed details")
        
        return synthesis_areas
    
    async def synthesize_ideas(
        self,
        session_uuid: str,
        discussion_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Synthesize ideas from discussion results
        
        Args:
            session_uuid: Debate session UUID
            discussion_results: Results from collaborative discussion
            
        Returns:
            Synthesis results
        """
        try:
            logger.info(f"Synthesizing ideas for session {session_uuid}")
            
            synthesis_results = {
                "session_uuid": session_uuid,
                "synthesis_approach": "collaborative_integration",
                "integrated_solution": {},
                "resolved_conflicts": [],
                "remaining_tensions": [],
                "implementation_framework": {},
                "confidence_assessment": 0.0
            }
            
            # Extract key elements for synthesis
            key_agreements = discussion_results.get("key_agreements", [])
            key_disagreements = discussion_results.get("key_disagreements", [])
            emerging_insights = discussion_results.get("emerging_insights", [])
            
            # Build integrated solution
            integrated_solution = await self._build_integrated_solution(
                key_agreements, key_disagreements, emerging_insights
            )
            synthesis_results["integrated_solution"] = integrated_solution
            
            # Resolve conflicts
            resolved_conflicts = await self._resolve_conflicts(key_disagreements)
            synthesis_results["resolved_conflicts"] = resolved_conflicts
            
            # Identify remaining tensions
            remaining_tensions = await self._identify_remaining_tensions(
                key_disagreements, resolved_conflicts
            )
            synthesis_results["remaining_tensions"] = remaining_tensions
            
            # Create implementation framework
            implementation_framework = await self._create_implementation_framework(
                integrated_solution, resolved_conflicts
            )
            synthesis_results["implementation_framework"] = implementation_framework
            
            # Assess confidence
            confidence = await self._assess_synthesis_confidence(synthesis_results)
            synthesis_results["confidence_assessment"] = confidence
            
            logger.info(f"Idea synthesis completed for session {session_uuid}")
            return synthesis_results
            
        except Exception as e:
            logger.error(f"Failed to synthesize ideas for session {session_uuid}: {e}")
            raise
    
    async def _build_integrated_solution(
        self,
        agreements: List[str],
        disagreements: List[str],
        insights: List[str]
    ) -> Dict[str, Any]:
        """Build an integrated solution from discussion elements"""
        return {
            "core_principles": agreements[:3] if agreements else [],
            "key_innovations": insights[:2] if insights else [],
            "balanced_approaches": [
                f"Balance between different viewpoints on: {d}" 
                for d in disagreements[:2]
            ] if disagreements else [],
            "implementation_priorities": [
                "Focus on agreed principles first",
                "Prototype disputed areas",
                "Integrate innovative insights"
            ]
        }
    
    async def _resolve_conflicts(self, disagreements: List[str]) -> List[str]:
        """Attempt to resolve conflicts from disagreements"""
        if not disagreements:
            return []
        
        # Simple conflict resolution (in production, would be more sophisticated)
        resolved = []
        for disagreement in disagreements[:3]:
            resolved.append(f"Resolved: {disagreement} through compromise approach")
        
        return resolved
    
    async def _identify_remaining_tensions(
        self,
        disagreements: List[str],
        resolved_conflicts: List[str]
    ) -> List[str]:
        """Identify tensions that still need to be addressed"""
        # Tensions that couldn't be resolved
        remaining = []
        
        if len(disagreements) > len(resolved_conflicts):
            remaining = disagreements[len(resolved_conflicts):]
        
        return remaining[:2]  # Limit to top 2 remaining tensions
    
    async def _create_implementation_framework(
        self,
        integrated_solution: Dict[str, Any],
        resolved_conflicts: List[str]
    ) -> Dict[str, Any]:
        """Create framework for implementing the synthesized solution"""
        return {
            "phase_1": "Implement core agreed principles",
            "phase_2": "Address resolved conflicts through compromise",
            "phase_3": "Integrate innovative insights",
            "validation_approach": "Iterative testing and feedback",
            "risk_mitigation": "Prototype disputed areas first",
            "success_metrics": [
                "Stakeholder satisfaction",
                "Technical feasibility validation",
                "Performance benchmarks met"
            ]
        }
    
    async def _assess_synthesis_confidence(self, synthesis_results: Dict[str, Any]) -> float:
        """Assess confidence in the synthesis results"""
        # Simple confidence calculation
        confidence_factors = []
        
        # More agreements = higher confidence
        agreements_count = len(synthesis_results["integrated_solution"].get("core_principles", []))
        confidence_factors.append(min(1.0, agreements_count / 3.0))
        
        # Fewer remaining tensions = higher confidence
        tensions_count = len(synthesis_results.get("remaining_tensions", []))
        confidence_factors.append(max(0.0, 1.0 - (tensions_count / 5.0)))
        
        # More resolved conflicts = higher confidence
        resolved_count = len(synthesis_results.get("resolved_conflicts", []))
        confidence_factors.append(min(1.0, resolved_count / 3.0))
        
        # Calculate average confidence
        return sum(confidence_factors) / len(confidence_factors) if confidence_factors else 0.5

