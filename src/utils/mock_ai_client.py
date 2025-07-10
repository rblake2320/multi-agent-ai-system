"""
Mock AI Client for Testing
Provides mock responses for AI model interactions during testing
"""
import asyncio
import logging

logger = logging.getLogger(__name__)


class MockAIResponse:
    """Mock AI response object"""
    
    def __init__(self, content: str):
        self.content = content
        self.choices = [MockChoice(content)]


class MockChoice:
    """Mock choice object"""
    
    def __init__(self, content: str):
        self.message = MockMessage(content)


class MockMessage:
    """Mock message object"""
    
    def __init__(self, content: str):
        self.content = content


class MockAsyncOpenAI:
    """Mock OpenAI client for testing"""
    
    def __init__(self, api_key: str = "test-key"):
        self.api_key = api_key
        self.chat = MockChat()


class MockChat:
    """Mock chat completions"""
    
    def __init__(self):
        self.completions = MockCompletions()


class MockCompletions:
    """Mock completions"""
    
    async def create(self, **kwargs) -> MockAIResponse:
        """Create mock completion response"""
        messages = kwargs.get("messages", [])
        kwargs.get("model", "gpt-4")
        
        # Generate mock response based on the last message
        if messages:
            last_message = messages[-1].get("content", "")
            
            # Generate contextual mock responses
            if "analyze" in last_message.lower():
                content = self._generate_analysis_response(last_message)
            elif "discuss" in last_message.lower() or "debate" in last_message.lower():
                content = self._generate_discussion_response(last_message)
            elif "consensus" in last_message.lower():
                content = self._generate_consensus_response(last_message)
            elif "code" in last_message.lower():
                content = self._generate_code_response(last_message)
            else:
                content = self._generate_generic_response(last_message)
        else:
            content = "Mock AI response: No input provided"
        
        # Simulate API delay
        await asyncio.sleep(0.1)
        
        return MockAIResponse(content)
    
    def _generate_analysis_response(self, prompt: str) -> str:
        """Generate mock analysis response"""
        return """Based on my analysis, I identify the following key aspects:

1. **Technical Feasibility**: The proposed approach appears technically sound with modern frameworks and established patterns.

2. **Implementation Complexity**: Medium complexity requiring careful coordination between components.

3. **Resource Requirements**: Estimated 2-3 developers, 4-6 weeks development time.

4. **Risk Factors**: 
   - Integration complexity between multiple systems
   - Performance optimization requirements
   - Testing and validation overhead

5. **Recommendations**:
   - Start with MVP approach
   - Implement comprehensive testing
   - Plan for iterative development
   - Consider scalability from the beginning

This analysis provides a solid foundation for moving forward with implementation."""
    
    def _generate_discussion_response(self, prompt: str) -> str:
        """Generate mock discussion response"""
        return """I appreciate the opportunity to contribute to this discussion. Here are my thoughts:

**Areas of Agreement**:
- The overall approach is well-structured and follows best practices
- The technical architecture appears sound and scalable
- The timeline seems reasonable given the scope

**Points for Consideration**:
- We should ensure adequate testing coverage from the start
- Consider the user experience implications of our technical decisions
- Resource allocation may need adjustment based on complexity

**Suggestions for Improvement**:
- Add more detailed error handling specifications
- Include performance benchmarks and monitoring
- Plan for documentation and knowledge transfer

**Questions for Further Discussion**:
- How will we handle edge cases and error scenarios?
- What are the specific performance requirements?
- How will we measure success and gather feedback?

I believe this collaborative approach will lead to a robust solution."""
    
    def _generate_consensus_response(self, prompt: str) -> str:
        """Generate mock consensus response"""
        return """After careful consideration of all perspectives presented, I provide the following consensus input:

**Agreement Level**: High (85% confidence)

**Supporting Factors**:
- Technical approach is well-validated
- Resource estimates appear realistic
- Risk mitigation strategies are comprehensive
- Timeline allows for quality implementation

**Minor Concerns**:
- Testing strategy could be more detailed
- Documentation requirements need clarification

**Suggested Modifications**:
- Add specific performance benchmarks
- Include user acceptance testing phase
- Plan for post-deployment monitoring

**Final Recommendation**: 
I support moving forward with this proposal, incorporating the suggested modifications. The approach balances innovation with practical implementation considerations.

**Confidence Assessment**: 8.5/10 - Strong consensus with minor refinements needed."""
    
    def _generate_code_response(self, prompt: str) -> str:
        """Generate mock code response"""
        return """Here's a mock code implementation:

```python
class MockImplementation:
    def __init__(self):
        self.status = "initialized"
        self.components = []
    
    async def process(self, input_data):
        \"\"\"Process input data and return results\"\"\"
        try:
            # Mock processing logic
            result = {
                "status": "success",
                "data": input_data,
                "processed_at": "2025-01-07T10:00:00Z"
            }
            return result
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def validate(self):
        \"\"\"Validate implementation\"\"\"
        return True
```

This implementation provides a solid foundation that can be extended based on specific requirements."""
    
    def _generate_generic_response(self, prompt: str) -> str:
        """Generate generic mock response"""
        return """Thank you for your input. I've analyzed your request and here's my response:

**Summary**: Your request has been processed successfully.

**Key Points**:
- The input has been analyzed and understood
- Relevant considerations have been identified
- Appropriate recommendations are provided below

**Recommendations**:
- Proceed with the proposed approach
- Monitor progress and adjust as needed
- Maintain clear communication throughout

**Next Steps**:
- Implement the suggested solution
- Test thoroughly before deployment
- Gather feedback for continuous improvement

This mock response demonstrates the system's capability to process and respond to various types of input."""


# Mock clients for other AI providers
class MockAnthropic:
    """Mock Anthropic client"""
    
    def __init__(self, api_key: str = "test-key"):
        self.api_key = api_key
        self.messages = MockAnthropicMessages()


class MockAnthropicMessages:
    """Mock Anthropic messages"""
    
    async def create(self, **kwargs) -> MockAIResponse:
        """Create mock Anthropic response"""
        messages = kwargs.get("messages", [])
        content = "Mock Anthropic response: " + str(messages[-1].get("content", "")) if messages else "No input"
        await asyncio.sleep(0.1)
        return MockAIResponse(content)


class MockGoogleGenerativeAI:
    """Mock Google Generative AI client"""
    
    def __init__(self, api_key: str = "test-key"):
        self.api_key = api_key
    
    async def generate_content(self, prompt: str) -> MockAIResponse:
        """Generate mock Google AI response"""
        content = f"Mock Google AI response: {prompt}"
        await asyncio.sleep(0.1)
        return MockAIResponse(content)


def get_mock_ai_client(provider: str = "openai", api_key: str = "test-key"):
    """Get mock AI client for specified provider"""
    if provider == "openai":
        return MockAsyncOpenAI(api_key)
    elif provider == "anthropic":
        return MockAnthropic(api_key)
    elif provider == "google":
        return MockGoogleGenerativeAI(api_key)
    else:
        raise ValueError(f"Unsupported AI provider: {provider}")

