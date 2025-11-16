"""
Agent Orchestration Service - Microservice for coordinating AI agents
Implements: Microservices Architecture, Agent Coordination
"""
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
# import openai
from openai import OpenAI
from pydantic import BaseModel
import time


class AgentRequest(BaseModel):
    """Structured agent request"""
    agent_role: str
    prompt: str
    constraints: Dict[str, Any]
    request_id: str
    timestamp: datetime = None
    
    def __init__(self, **data):
        super().__init__(**data)
        if self.timestamp is None:
            self.timestamp = datetime.now()


class AgentResponse(BaseModel):
    """Structured agent response with metrics"""
    agent_role: str
    content: str
    request_id: str
    latency_ms: float
    token_usage: Dict[str, int]
    timestamp: datetime
    success: bool
    error: Optional[str] = None


class AgentOrchestrationService:
    """
    Architecture: Microservices pattern
    Lifecycle: Supports iterative refinement (Agile)
    Maintainability: Clear separation of concerns
    """
    
    def __init__(self, api_key: str, config: dict):
        self.client = OpenAI(api_key=api_key)
        self.config = config
        self.agents_config = config.get('agents', {})
        self.boundaries = config.get('boundaries', {})
        self.requirements = config.get('requirements', {})
        
    # def _check_boundaries(self, query: str) -> tuple[bool, Optional[str]]:
    #     """
    #     System Engineering: Enforce system boundaries
    #     Identifies what the AI should and should not do
    #     """
    #     query_lower = query.lower()
        
    #     # Check forbidden topics
    #     forbidden = self.boundaries.get('forbidden_topics', [])
    #     for topic in forbidden:
    #         if topic.replace('_', ' ') in query_lower:
    #             return False, f"Query contains forbidden topic: {topic}"
        
    #     # Rate limiting check (simplified)
    #     # In production, this would use Redis or similar
        
    #     return True, None
    
    async def _check_boundaries(self, query: str) -> tuple[bool, Optional[str]]:
        """
        System Engineering: Enforce system boundaries using LLM-based semantic verification only.
        If the LLM determines the query relates to any forbidden topic, the query is rejected.
        Otherwise, it is allowed.
        """
        forbidden = self.boundaries.get('forbidden_topics', [])

        try:
            check_prompt = (
                "You are a strict compliance and content safety classifier.\n"
                "Your task is to determine if the user's query relates to any forbidden topic.\n\n"
                f"Forbidden topics: {', '.join(forbidden)}.\n\n"
                f"User query: \"{query}\"\n\n"
                "Respond ONLY with 'YES' or 'NO'.\n"
                "Say 'YES' if it clearly or indirectly involves any forbidden topic.\n"
                "Say 'NO' if it does NOT relate to any forbidden topic."
            )

            response = self.client.chat.completions.create(
                model=self.config.get('agents', {}).get('validator', {}).get('model', 'gpt-4.1-mini'),
                messages=[
                    {"role": "system", "content": "You are a compliance and ethics classifier."},
                    {"role": "user", "content": check_prompt},
                ],
                temperature=0.0,
                max_tokens=5
            )

            llm_answer = response.choices[0].message.content.strip().lower()

            if "yes" in llm_answer:
                print(f"[Boundary Check] ❌ LLM flagged query as forbidden: {query}")
                return False, "Query rejected — relates to forbidden topics."

            print(f"[Boundary Check] ✅ Query allowed: {query}")
            return True, None

        except Exception as e:
            # Fail-safe: allow the query if the LLM boundary check fails
            print(f"[Boundary Warning] LLM boundary check failed ({e}); allowing query.")
            return True, None


    async def execute_agent(self, request: AgentRequest) -> AgentResponse:
        """
        Execute a single agent request with monitoring
        Non-functional Requirements: Latency, reliability tracking
        """
        start_time = time.time()
        
        try:
            # Get agent configuration
            agent_config = self.agents_config.get(request.agent_role, {})
            
            # Prepare API call
            response = self.client.chat.completions.create(
                # model=agent_config.get('model', 'gpt-3.5-turbo'),
                model=agent_config.get('model', 'gpt-4.1-mini'),
                messages=[
                    {"role": "system", "content": f"You are a {request.agent_role} agent."},
                    {"role": "user", "content": request.prompt}
                ],
                temperature=request.constraints.get('temperature', agent_config.get('temperature', 0.5)),
                max_tokens=request.constraints.get('max_tokens', agent_config.get('max_tokens', 500))
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Check non-functional requirements
            max_latency = self.requirements.get('non_functional', {}).get('max_latency_ms', 10000)
            if latency_ms > max_latency:
                print(f"WARNING: Latency ({latency_ms}ms) exceeded threshold ({max_latency}ms)")
            
            return AgentResponse(
                agent_role=request.agent_role,
                content=response.choices[0].message.content,
                request_id=request.request_id,
                latency_ms=latency_ms,
                token_usage={
                    'prompt_tokens': response.usage.prompt_tokens,
                    'completion_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens
                },
                timestamp=datetime.now(),
                success=True
            )
            
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            return AgentResponse(
                agent_role=request.agent_role,
                content="",
                request_id=request.request_id,
                latency_ms=latency_ms,
                token_usage={'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0},
                timestamp=datetime.now(),
                success=False,
                error=str(e)
            )
    
    async def orchestrate_multi_agent_workflow(
        self, 
        query: str, 
        workflow_id: str
    ) -> Dict[str, Any]:
        """
        Software Design: Integration plan for multi-agent coordination
        Implements the research -> analyze -> validate pipeline
        """
        # System Engineering: Check boundaries
        # is_valid, error_msg = self._check_boundaries(query)
        is_valid, error_msg = await self._check_boundaries(query)
        if not is_valid:
            return {
                'workflow_id': workflow_id,
                'status': 'rejected',
                'reason': error_msg,
                'timestamp': datetime.now().isoformat()
            }
        
        results = {
            'workflow_id': workflow_id,
            'status': 'in_progress',
            'stages': {},
            'metrics': {
                'total_latency_ms': 0,
                'total_tokens': 0,
                'stages_completed': 0
            }
        }
        
        start_time = time.time()
        
        # Stage 1: Research
        from services.prompt_library_service import PromptLibraryService
        prompt_lib = PromptLibraryService()
        
        research_prompt = prompt_lib.render_prompt(
            'researcher_query',
            topic=query,
            allowed_topics=', '.join(self.boundaries.get('allowed_topics', [])),
            forbidden_topics=', '.join(self.boundaries.get('forbidden_topics', [])),
            max_length=400
        )
        
        research_request = AgentRequest(
            agent_role='researcher',
            prompt=research_prompt,
            constraints=self.agents_config.get('researcher', {}).get('constraints', {}),
            request_id=f"{workflow_id}_research"
        )
        
        research_response = await self.execute_agent(research_request)
        results['stages']['research'] = {
            'response': research_response.content,
            'latency_ms': research_response.latency_ms,
            'tokens': research_response.token_usage,
            'success': research_response.success
        }
        
        if not research_response.success:
            print(f"[ERROR] Researcher failed with error: {research_response.error}")
            results['status'] = 'failed'
            results['failed_stage'] = 'research'
            return results
        
        # Stage 2: Analysis
        analysis_prompt = prompt_lib.render_prompt(
            'analyzer_synthesis',
            research_data=research_response.content,
            max_length=300
        )
        
        analysis_request = AgentRequest(
            agent_role='analyzer',
            prompt=analysis_prompt,
            constraints=self.agents_config.get('analyzer', {}).get('constraints', {}),
            request_id=f"{workflow_id}_analysis"
        )
        
        analysis_response = await self.execute_agent(analysis_request)
        results['stages']['analysis'] = {
            'response': analysis_response.content,
            'latency_ms': analysis_response.latency_ms,
            'tokens': analysis_response.token_usage,
            'success': analysis_response.success
        }
        
        if not analysis_response.success:
            print(f"[ERROR] Analyser failed with error: {analysis_response.error}")
            results['status'] = 'failed'
            results['failed_stage'] = 'analysis'
            return results
        
        # Stage 3: Validation
        validation_prompt = prompt_lib.render_prompt(
            'validator_check',
            analysis=analysis_response.content
        )
        
        validation_request = AgentRequest(
            agent_role='validator',
            prompt=validation_prompt,
            constraints=self.agents_config.get('validator', {}).get('constraints', {}),
            request_id=f"{workflow_id}_validation"
        )
        
        validation_response = await self.execute_agent(validation_request)
        results['stages']['validation'] = {
            'response': validation_response.content,
            'latency_ms': validation_response.latency_ms,
            'tokens': validation_response.token_usage,
            'success': validation_response.success
        }
        
        if not validation_response.success:
            print(f"[ERROR] Validation failed with error: {validation_response.error}")

        # Calculate total metrics
        total_latency = sum(
            stage['latency_ms'] 
            for stage in results['stages'].values()
        )
        total_tokens = sum(
            stage['tokens']['total_tokens'] 
            for stage in results['stages'].values()
        )
        
        results['metrics']['total_latency_ms'] = total_latency
        results['metrics']['total_tokens'] = total_tokens
        results['metrics']['stages_completed'] = len(results['stages'])
        results['status'] = 'completed' if validation_response.success else 'failed'
        results['timestamp'] = datetime.now().isoformat()
        
        return results


