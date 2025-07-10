"""
Base Persona class for Hive Collective Intelligence
Provides common functionality for all persona types
"""
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from config.settings import settings

logger = logging.getLogger(__name__)


class BasePersona(ABC):
    """
    Abstract base class for all personas in the hive collective
    """
    
    def __init__(self, name: str, specialization: str, model: Optional[str] = None):
        self.name = name
        self.specialization = specialization
        self.model = model or "gpt-4"
        self.initialized = False
        self.client = None
        self.system_prompt = ""
        self.knowledge_base = {}
        self.conversation_history = []
    
    async def initialize(self):
        """Initialize the persona"""
        try:
            # Use mock AI client for testing
            if settings.system.environment == "development" or not settings.ai_models.openai_api_key or settings.ai_models.openai_api_key == "test-key":
                from utils.mock_ai_client import get_mock_ai_client
                self.client = get_mock_ai_client("openai")
                logger.info(f"Using mock AI client for {self.name} persona")
            else:
                import openai
                self.client = openai.AsyncOpenAI(api_key=settings.ai_models.openai_api_key)
                logger.info(f"Using real OpenAI client for {self.name} persona")
            
            # Load knowledge base
            await self._load_knowledge_base()
            
            # Create system prompt
            self.system_prompt = await self._create_system_prompt()
            
            self.initialized = True
            logger.info(f"{self.name} persona initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize {self.name} persona: {e}")
            raise
    
    async def shutdown(self):
        """Shutdown the persona"""
        self.initialized = False
        logger.info(f"{self.name} persona shutdown")
    
    @abstractmethod
    async def _load_knowledge_base(self):
        """Load persona-specific knowledge base"""
        pass
    
    @abstractmethod
    async def _create_system_prompt(self) -> str:
        """Create the system prompt for this persona"""
        pass
    
    async def analyze_problem(self, problem_description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a problem from this persona's perspective
        
        Args:
            problem_description: Description of the problem to analyze
            context: Additional context information
            
        Returns:
            Analysis results from this persona's perspective
        """
        try:
            if not self.initialized:
                raise RuntimeError(f"{self.name} persona not initialized")
            
            # Prepare the analysis prompt
            analysis_prompt = f"""
            As a {self.specialization} expert, please analyze the following problem:
            
            Problem: {problem_description}
            
            Context: {context}
            
            Please provide your analysis focusing on your area of expertise.
            """
            
            # Get AI response
            response = await self._get_ai_response(analysis_prompt)
            
            # Structure the response
            analysis_result = {
                "persona": self.name,
                "specialization": self.specialization,
                "analysis": response,
                "confidence": 0.8,  # Mock confidence score
                "key_points": self._extract_key_points(response),
                "recommendations": self._extract_recommendations(response),
                "concerns": self._extract_concerns(response)
            }
            
            logger.info(f"{self.name} completed problem analysis")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Failed to analyze problem with {self.name}: {e}")
            raise
    
    async def participate_in_discussion(
        self,
        discussion_context: Dict[str, Any],
        previous_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Participate in a collaborative discussion
        
        Args:
            discussion_context: Current discussion context
            previous_context: Previous discussion rounds and analyses
            
        Returns:
            Discussion contribution from this persona
        """
        try:
            if not self.initialized:
                raise RuntimeError(f"{self.name} persona not initialized")
            
            # Prepare discussion prompt
            discussion_prompt = f"""
            You are participating in a collaborative discussion as a {self.specialization} expert.
            
            Discussion Context: {discussion_context}
            Previous Context: {previous_context}
            
            Please provide your contribution to this discussion, including:
            - Your perspective on the current discussion
            - Points of agreement with other participants
            - Points of disagreement or concern
            - Suggestions for improvement or alternative approaches
            - Questions that need to be addressed
            """
            
            # Get AI response
            response = await self._get_ai_response(discussion_prompt)
            
            # Structure the contribution
            contribution = {
                "persona": self.name,
                "contribution": response,
                "agreements": self._extract_agreements(response),
                "disagreements": self._extract_disagreements(response),
                "challenges": self._extract_challenges(response),
                "improvements": self._extract_improvements(response),
                "questions": self._extract_questions(response)
            }
            
            logger.info(f"{self.name} contributed to discussion")
            return contribution
            
        except Exception as e:
            logger.error(f"Failed to participate in discussion with {self.name}: {e}")
            raise
    
    async def provide_consensus_input(
        self,
        synthesis_results: Dict[str, Any],
        proposed_decision: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Provide input for consensus building
        
        Args:
            synthesis_results: Results from the synthesis phase
            proposed_decision: Proposed decision to evaluate
            
        Returns:
            Consensus input from this persona
        """
        try:
            if not self.initialized:
                raise RuntimeError(f"{self.name} persona not initialized")
            
            # Prepare consensus prompt
            consensus_prompt = f"""
            As a {self.specialization} expert, please evaluate the following proposed decision:
            
            Synthesis Results: {synthesis_results}
            Proposed Decision: {proposed_decision}
            
            Please provide your consensus input including:
            - Whether you agree with the proposed decision (yes/no)
            - Your confidence level in this decision (0-1)
            - Reasons for your support or concerns
            - Suggested modifications if any
            - Critical issues that must be addressed
            """
            
            # Get AI response
            response = await self._get_ai_response(consensus_prompt)
            
            # Structure the consensus input
            consensus_input = {
                "persona": self.name,
                "agreement": self._extract_agreement_status(response),
                "confidence": self._extract_confidence_score(response),
                "support_reasons": self._extract_support_reasons(response),
                "concerns": self._extract_concerns(response),
                "suggested_modifications": self._extract_modifications(response),
                "critical_issues": self._extract_critical_issues(response),
                "full_response": response
            }
            
            logger.info(f"{self.name} provided consensus input")
            return consensus_input
            
        except Exception as e:
            logger.error(f"Failed to provide consensus input with {self.name}: {e}")
            raise
    
    async def _get_ai_response(self, prompt: str) -> str:
        """Get response from AI model"""
        try:
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ]
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Failed to get AI response for {self.name}: {e}")
            raise
    
    def _extract_key_points(self, response: str) -> List[str]:
        """Extract key points from response"""
        # Simple extraction - in production would use NLP
        lines = response.split('\n')
        key_points = []
        for line in lines:
            if line.strip().startswith(('•', '-', '*', '1.', '2.', '3.')):
                key_points.append(line.strip())
        return key_points[:5]  # Return top 5
    
    def _extract_recommendations(self, response: str) -> List[str]:
        """Extract recommendations from response"""
        # Simple extraction
        if "recommend" in response.lower():
            return ["Extracted recommendation from analysis"]
        return []
    
    def _extract_concerns(self, response: str) -> List[str]:
        """Extract concerns from response"""
        # Simple extraction
        if "concern" in response.lower() or "risk" in response.lower():
            return ["Identified concern from analysis"]
        return []
    
    def _extract_agreements(self, response: str) -> List[str]:
        """Extract agreements from response"""
        if "agree" in response.lower():
            return ["Agreement point identified"]
        return []
    
    def _extract_disagreements(self, response: str) -> List[str]:
        """Extract disagreements from response"""
        if "disagree" in response.lower() or "concern" in response.lower():
            return ["Disagreement point identified"]
        return []
    
    def _extract_challenges(self, response: str) -> List[str]:
        """Extract challenges from response"""
        if "challenge" in response.lower() or "difficult" in response.lower():
            return ["Challenge identified"]
        return []
    
    def _extract_improvements(self, response: str) -> List[str]:
        """Extract improvement suggestions from response"""
        if "improve" in response.lower() or "better" in response.lower():
            return ["Improvement suggestion identified"]
        return []
    
    def _extract_questions(self, response: str) -> List[str]:
        """Extract questions from response"""
        questions = []
        for line in response.split('\n'):
            if '?' in line:
                questions.append(line.strip())
        return questions[:3]  # Return top 3
    
    def _extract_agreement_status(self, response: str) -> bool:
        """Extract agreement status from response"""
        response_lower = response.lower()
        if "yes" in response_lower or "agree" in response_lower or "support" in response_lower:
            return True
        return False
    
    def _extract_confidence_score(self, response: str) -> float:
        """Extract confidence score from response"""
        # Simple extraction - look for numbers between 0-1 or percentages
        import re
        
        # Look for confidence patterns
        confidence_patterns = [
            r'confidence[:\s]+(\d+(?:\.\d+)?)',
            r'(\d+(?:\.\d+)?)[:\s]*confidence',
            r'(\d+)%',
            r'(\d+(?:\.\d+)?)/10'
        ]
        
        for pattern in confidence_patterns:
            match = re.search(pattern, response.lower())
            if match:
                value = float(match.group(1))
                if value > 1:  # Assume percentage or out of 10
                    return min(value / 100 if value <= 100 else value / 10, 1.0)
                return value
        
        # Default confidence based on agreement
        return 0.8 if self._extract_agreement_status(response) else 0.3
    
    def _extract_support_reasons(self, response: str) -> List[str]:
        """Extract support reasons from response"""
        if "support" in response.lower() or "because" in response.lower():
            return ["Support reason identified"]
        return []
    
    def _extract_modifications(self, response: str) -> List[str]:
        """Extract suggested modifications from response"""
        if "modify" in response.lower() or "change" in response.lower() or "suggest" in response.lower():
            return ["Modification suggestion identified"]
        return []
    
    def _extract_critical_issues(self, response: str) -> List[str]:
        """Extract critical issues from response"""
        if "critical" in response.lower() or "must" in response.lower() or "essential" in response.lower():
            return ["Critical issue identified"]
        return []

