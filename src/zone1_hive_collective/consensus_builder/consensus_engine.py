"""
Consensus Engine for Hive Collective Intelligence
Builds consensus and final decisions from synthesized discussion results
"""
import asyncio
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class ConsensusEngine:
    """
    Builds consensus among personas for final decision making
    """
    
    def __init__(self, personas: Dict[str, Any]):
        self.personas = personas
        self.consensus_threshold = 0.8  # 80% agreement threshold
        self.max_consensus_rounds = 3
        self.initialized = False
    
    async def initialize(self):
        """Initialize the consensus engine"""
        self.initialized = True
        logger.info("Consensus engine initialized")
    
    async def shutdown(self):
        """Shutdown the consensus engine"""
        self.initialized = False
        logger.info("Consensus engine shutdown")
    
    async def build_consensus(
        self,
        session_uuid: str,
        synthesis_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Build consensus on final decision from synthesis results
        
        Args:
            session_uuid: Debate session UUID
            synthesis_results: Results from synthesis phase
            
        Returns:
            Consensus results and final decision
        """
        try:
            logger.info(f"Building consensus for session {session_uuid}")
            
            consensus_results = {
                "session_uuid": session_uuid,
                "consensus_reached": False,
                "confidence_score": 0.0,
                "final_decision": {},
                "reasoning": "",
                "implementation_guidance": {},
                "consensus_rounds": [],
                "dissenting_opinions": [],
                "areas_of_agreement": [],
                "decision_rationale": ""
            }
            
            # Create initial proposed decision from synthesis
            proposed_decision = await self._create_proposed_decision(synthesis_results)
            
            # Conduct consensus rounds
            current_proposal = proposed_decision
            
            for round_num in range(self.max_consensus_rounds):
                logger.info(f"Starting consensus round {round_num + 1}")
                
                round_result = await self._conduct_consensus_round(
                    session_uuid,
                    round_num + 1,
                    current_proposal,
                    synthesis_results
                )
                
                consensus_results["consensus_rounds"].append(round_result)
                
                # Check if consensus is reached
                consensus_score = round_result.get("consensus_score", 0.0)
                if consensus_score >= self.consensus_threshold:
                    logger.info(f"Consensus reached in round {round_num + 1}")
                    consensus_results["consensus_reached"] = True
                    consensus_results["confidence_score"] = consensus_score
                    break
                
                # Update proposal based on feedback
                current_proposal = await self._update_proposal(
                    current_proposal,
                    round_result
                )
            
            # Finalize consensus results
            if consensus_results["consensus_reached"]:
                consensus_results.update(await self._finalize_consensus(
                    current_proposal,
                    consensus_results["consensus_rounds"]
                ))
            else:
                consensus_results.update(await self._handle_no_consensus(
                    current_proposal,
                    consensus_results["consensus_rounds"]
                ))
            
            logger.info(f"Consensus building completed for session {session_uuid}")
            return consensus_results
            
        except Exception as e:
            logger.error(f"Failed to build consensus for session {session_uuid}: {e}")
            raise
    
    async def _create_proposed_decision(self, synthesis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Create initial proposed decision from synthesis results"""
        integrated_solution = synthesis_results.get("integrated_solution", {})
        implementation_framework = synthesis_results.get("implementation_framework", {})
        
        return {
            "approach": "Integrated solution based on collective analysis",
            "core_principles": integrated_solution.get("core_principles", []),
            "key_innovations": integrated_solution.get("key_innovations", []),
            "implementation_plan": implementation_framework,
            "success_criteria": [
                "Technical feasibility validated",
                "Stakeholder requirements met",
                "Quality standards achieved",
                "Resource constraints respected"
            ],
            "risk_mitigation": [
                "Prototype critical components",
                "Iterative development approach",
                "Regular stakeholder feedback",
                "Continuous quality monitoring"
            ]
        }
    
    async def _conduct_consensus_round(
        self,
        session_uuid: str,
        round_num: int,
        proposed_decision: Dict[str, Any],
        synthesis_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Conduct a single consensus round"""
        logger.info(f"Conducting consensus round {round_num} for session {session_uuid}")
        
        round_result = {
            "round_number": round_num,
            "persona_inputs": {},
            "agreements": 0,
            "disagreements": 0,
            "consensus_score": 0.0,
            "suggested_modifications": [],
            "critical_issues": [],
            "support_reasons": [],
            "concerns": []
        }
        
        # Get consensus input from each persona
        for persona_name, persona in self.personas.items():
            try:
                consensus_input = await persona.provide_consensus_input(
                    synthesis_results,
                    proposed_decision
                )
                
                round_result["persona_inputs"][persona_name] = consensus_input
                
                # Count agreements and disagreements
                if consensus_input.get("agreement", False):
                    round_result["agreements"] += 1
                else:
                    round_result["disagreements"] += 1
                
                # Collect feedback
                if "suggested_modifications" in consensus_input:
                    round_result["suggested_modifications"].extend(
                        consensus_input["suggested_modifications"]
                    )
                
                if "critical_issues" in consensus_input:
                    round_result["critical_issues"].extend(
                        consensus_input["critical_issues"]
                    )
                
                if "support_reasons" in consensus_input:
                    round_result["support_reasons"].extend(
                        consensus_input["support_reasons"]
                    )
                
                if "concerns" in consensus_input:
                    round_result["concerns"].extend(
                        consensus_input["concerns"]
                    )
                
                logger.info(f"Received consensus input from {persona_name}")
                
            except Exception as e:
                logger.error(f"Failed to get consensus input from {persona_name}: {e}")
                round_result["persona_inputs"][persona_name] = {
                    "error": str(e),
                    "agreement": False,
                    "confidence": 0.0
                }
                round_result["disagreements"] += 1
        
        # Calculate consensus score
        total_personas = len(self.personas)
        if total_personas > 0:
            round_result["consensus_score"] = round_result["agreements"] / total_personas
        
        return round_result
    
    async def _update_proposal(
        self,
        current_proposal: Dict[str, Any],
        round_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update proposal based on consensus round feedback"""
        updated_proposal = current_proposal.copy()
        
        # Incorporate suggested modifications
        modifications = round_result.get("suggested_modifications", [])
        if modifications:
            # Add modifications to implementation plan
            if "implementation_plan" not in updated_proposal:
                updated_proposal["implementation_plan"] = {}
            
            updated_proposal["implementation_plan"]["modifications"] = modifications[:3]
        
        # Address critical issues
        critical_issues = round_result.get("critical_issues", [])
        if critical_issues:
            updated_proposal["critical_issues_addressed"] = critical_issues[:2]
        
        # Incorporate support reasons
        support_reasons = round_result.get("support_reasons", [])
        if support_reasons:
            updated_proposal["strengths"] = support_reasons[:3]
        
        return updated_proposal
    
    async def _finalize_consensus(
        self,
        final_proposal: Dict[str, Any],
        consensus_rounds: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Finalize consensus results when consensus is reached"""
        # Get the last round (successful consensus round)
        last_round = consensus_rounds[-1] if consensus_rounds else {}
        
        # Compile areas of agreement
        areas_of_agreement = []
        for round_data in consensus_rounds:
            areas_of_agreement.extend(round_data.get("support_reasons", []))
        
        # Compile final reasoning
        reasoning = await self._compile_consensus_reasoning(consensus_rounds)
        
        # Create implementation guidance
        implementation_guidance = await self._create_implementation_guidance(
            final_proposal,
            consensus_rounds
        )
        
        return {
            "final_decision": final_proposal,
            "reasoning": reasoning,
            "implementation_guidance": implementation_guidance,
            "areas_of_agreement": list(set(areas_of_agreement))[:5],
            "decision_rationale": "Consensus reached through structured debate and collaboration"
        }
    
    async def _handle_no_consensus(
        self,
        final_proposal: Dict[str, Any],
        consensus_rounds: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Handle case where consensus is not reached"""
        # Identify dissenting opinions
        dissenting_opinions = []
        remaining_concerns = []
        
        for round_data in consensus_rounds:
            dissenting_opinions.extend(round_data.get("concerns", []))
            remaining_concerns.extend(round_data.get("critical_issues", []))
        
        # Create fallback decision
        fallback_decision = {
            "approach": "Majority decision with minority concerns noted",
            "primary_solution": final_proposal,
            "dissenting_views": list(set(dissenting_opinions))[:3],
            "unresolved_issues": list(set(remaining_concerns))[:3],
            "recommendation": "Proceed with prototype to validate disputed areas"
        }
        
        reasoning = "Consensus not fully reached. Proceeding with majority decision while noting minority concerns."
        
        implementation_guidance = {
            "approach": "Phased implementation with validation",
            "phase_1": "Implement agreed components",
            "phase_2": "Prototype disputed areas",
            "phase_3": "Validate and refine based on results",
            "monitoring": "Close monitoring of dissenting concerns"
        }
        
        return {
            "final_decision": fallback_decision,
            "reasoning": reasoning,
            "implementation_guidance": implementation_guidance,
            "dissenting_opinions": list(set(dissenting_opinions))[:3],
            "decision_rationale": "Majority decision with documented minority positions"
        }
    
    async def _compile_consensus_reasoning(self, consensus_rounds: List[Dict[str, Any]]) -> str:
        """Compile reasoning from consensus rounds"""
        if not consensus_rounds:
            return "No consensus rounds conducted"
        
        last_round = consensus_rounds[-1]
        agreements = last_round.get("agreements", 0)
        total_personas = len(self.personas)
        
        reasoning = f"Consensus reached with {agreements}/{total_personas} personas in agreement. "
        
        # Add key support reasons
        support_reasons = []
        for round_data in consensus_rounds:
            support_reasons.extend(round_data.get("support_reasons", []))
        
        if support_reasons:
            unique_reasons = list(set(support_reasons))[:3]
            reasoning += f"Key supporting factors: {', '.join(unique_reasons)}."
        
        return reasoning
    
    async def _create_implementation_guidance(
        self,
        final_proposal: Dict[str, Any],
        consensus_rounds: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create detailed implementation guidance"""
        # Collect all suggested modifications
        all_modifications = []
        for round_data in consensus_rounds:
            all_modifications.extend(round_data.get("suggested_modifications", []))
        
        return {
            "implementation_approach": final_proposal.get("implementation_plan", {}),
            "key_modifications": list(set(all_modifications))[:5],
            "success_metrics": final_proposal.get("success_criteria", []),
            "risk_mitigation": final_proposal.get("risk_mitigation", []),
            "validation_strategy": [
                "Prototype critical components",
                "Stakeholder feedback loops",
                "Iterative refinement",
                "Performance monitoring"
            ],
            "next_steps": [
                "Detailed technical design",
                "Resource allocation planning",
                "Timeline development",
                "Risk assessment update"
            ]
        }

