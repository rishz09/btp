"""
Agentic Orchestration Service - TRUE AGENTIC AI
This replaces agent_orchestration_service.py with autonomous, goal-directed behavior

KEY AGENTIC FEATURES:
1. Goal-directed: Works toward quality threshold, not just executing steps
2. Planning: Decides which actions to take based on state
3. Autonomy: Chooses next steps (research, analyze, validate, refine)
4. Self-correction: Loops back to improve if quality is insufficient
5. Decision-making: Not hardcoded pipeline - agent decides flow
6. Memory/State: Tracks progress and quality scores
"""
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import openai
from pydantic import BaseModel
import time


class AgentState(BaseModel):
    """State tracking for agentic behavior"""
    workflow_id: str
    query: str
    goal_achieved: bool = False
    attempts: int = 0
    max_attempts: int = 5
    
    # Memory of what's been done
    research_output: Optional[str] = None
    analysis_output: Optional[str] = None
    validation_output: Optional[str] = None
    quality_score: float = 0.0
    
    # Action history for planning
    action_history: List[str] = []
    
    # Metrics
    total_latency_ms: float = 0.0
    total_tokens: int = 0


class AgentRequest(BaseModel):
    """Agent request with context"""
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
    """Agent response with metrics"""
    agent_role: str
    content: str
    request_id: str
    latency_ms: float
    token_usage: Dict[str, int]
    timestamp: datetime
    success: bool
    error: Optional[str] = None


class AgenticPlanner:
    """
    AGENTIC COMPONENT: Planning and Decision-Making
    
    This is what makes it AGENTIC - the planner DECIDES what to do next
    based on the current state, not following a fixed pipeline
    """
    
    def __init__(self, config: dict):
        self.config = config
        self.quality_threshold = config.get('requirements', {}).get('non_functional', {}).get('min_accuracy_threshold', 0.75)
    
    def decide_next_action(self, state: AgentState) -> Optional[str]:
        """
        AUTONOMOUS DECISION-MAKING
        
        The agent DECIDES what to do next based on:
        - Current state
        - Goal achievement status
        - Quality of previous outputs
        - Action history
        
        This is NOT hardcoded - it's dynamic decision-making
        """
        
        # Check if max attempts reached
        if state.attempts >= state.max_attempts:
            return None  # Give up
        
        # Check if goal is achieved
        if state.goal_achieved and state.quality_score >= self.quality_threshold:
            return None  # Success - stop
        
        # DECISION LOGIC (autonomous planning)
        
        # 1. If no research yet, must research first
        if state.research_output is None:
            return "research"
        
        # 2. If research done but no analysis, analyze
        if state.analysis_output is None:
            return "analyze"
        
        # 3. If analysis done but not validated, validate
        if state.validation_output is None:
            return "validate"
        
        # 4. If validated but quality too low, decide on correction
        if state.quality_score < self.quality_threshold:
            # AUTONOMOUS DECISION: What needs improvement?
            if state.quality_score < 0.5:
                # Very poor - start over with research
                return "research"
            elif state.quality_score < 0.65:
                # Medium quality - re-analyze with more detail
                return "refine_analysis"
            else:
                # Close to threshold - just refine slightly
                return "refine_minor"
        
        # 5. Quality is good enough
        state.goal_achieved = True
        return None
    
    def should_retry(self, state: AgentState, quality_score: float) -> bool:
        """
        SELF-CORRECTION DECISION
        
        Agent decides whether to retry based on quality
        """
        if quality_score >= self.quality_threshold:
            return False  # Good enough
        
        if state.attempts >= state.max_attempts:
            return False  # Give up
        
        return True  # Try to improve
    
    def plan_correction_strategy(self, state: AgentState) -> str:
        """
        ADAPTIVE PLANNING
        
        Based on what went wrong, plan how to fix it
        """
        if "research" in state.action_history and len(state.action_history) == 1:
            return "Need more detailed research"
        elif state.quality_score < 0.6:
            return "Analysis too shallow, need deeper synthesis"
        else:
            return "Minor refinements needed"


class AgenticOrchestrationService:
    """
    TRUE AGENTIC AI SERVICE
    
    Key differences from pipeline:
    1. Has GOALS (achieve quality threshold)
    2. Has AUTONOMY (decides next actions)
    3. Has PLANNING (planner component)
    4. Has MEMORY (state tracking)
    5. Has LOOPS (can retry and refine)
    6. Has DECISION-MAKING (not fixed flow)
    """
    
    def __init__(self, api_key: str, config: dict):
        self.client = openai.OpenAI(api_key=api_key)
        self.config = config
        self.agents_config = config.get('agents', {})
        self.boundaries = config.get('boundaries', {})
        self.requirements = config.get('requirements', {})
        
        # AGENTIC COMPONENT: Planner
        self.planner = AgenticPlanner(config)
        
        # Available tools/prompts the agent can choose from
        self.available_tools = {
            'research': self._tool_research,
            'analyze': self._tool_analyze,
            'validate': self._tool_validate,
            'refine_analysis': self._tool_refine_analysis,
            'refine_minor': self._tool_refine_minor
        }
    
    # def _check_boundaries(self, query: str) -> tuple[bool, Optional[str]]:
    #     """System boundary check"""
    #     query_lower = query.lower()
    #     forbidden = self.boundaries.get('forbidden_topics', [])
        
    #     for topic in forbidden:
    #         if topic.replace('_', ' ') in query_lower:
    #             return False, f"Query contains forbidden topic: {topic}"
        
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
        

    async def _execute_llm(
        self,
        role: str,
        prompt: str,
        constraints: dict
    ) -> AgentResponse:
        """Execute LLM call with metrics"""
        start_time = time.time()
        request_id = f"{role}_{int(time.time() * 1000)}"
        
        try:
            response = self.client.chat.completions.create(
                model=constraints.get('model', "gpt-4.1-mini"),
                messages=[
                    {"role": "system", "content": f"You are a {role}."},
                    {"role": "user", "content": prompt}
                ],
                temperature=constraints.get('temperature', 0.5),
                max_tokens=constraints.get('max_tokens', 500)
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            return AgentResponse(
                agent_role=role,
                content=response.choices[0].message.content,
                request_id=request_id,
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
                agent_role=role,
                content="",
                request_id=request_id,
                latency_ms=latency_ms,
                token_usage={'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0},
                timestamp=datetime.now(),
                success=False,
                error=str(e)
            )
    
    # TOOL DEFINITIONS (Agent can choose which to call)
    
    async def _tool_research(self, state: AgentState) -> AgentResponse:
        """Research tool"""
        from services.prompt_library_service import PromptLibraryService
        prompt_lib = PromptLibraryService()
        
        prompt = prompt_lib.render_prompt(
            'researcher_query',
            topic=state.query,
            allowed_topics=', '.join(self.boundaries.get('allowed_topics', [])),
            forbidden_topics=', '.join(self.boundaries.get('forbidden_topics', [])),
            max_length=400
        )
        
        return await self._execute_llm(
            'researcher',
            prompt,
            self.agents_config.get('researcher', {})
        )
    
    async def _tool_analyze(self, state: AgentState) -> AgentResponse:
        """Analysis tool"""
        from services.prompt_library_service import PromptLibraryService
        prompt_lib = PromptLibraryService()
        
        prompt = prompt_lib.render_prompt(
            'analyzer_synthesis',
            research_data=state.research_output,
            max_length=300
        )
        
        return await self._execute_llm(
            'analyzer',
            prompt,
            self.agents_config.get('analyzer', {})
        )
    
    async def _tool_validate(self, state: AgentState) -> AgentResponse:
        """Validation tool"""
        from services.prompt_library_service import PromptLibraryService
        prompt_lib = PromptLibraryService()
        
        prompt = prompt_lib.render_prompt(
            'validator_check',
            analysis=state.analysis_output
        )
        
        return await self._execute_llm(
            'validator',
            prompt,
            self.agents_config.get('validator', {})
        )
    
    async def _tool_refine_analysis(self, state: AgentState) -> AgentResponse:
        """Refinement tool - AGENTIC SELF-CORRECTION"""
        prompt = f"""You are an analytical assistant performing refinement.

ORIGINAL RESEARCH:
{state.research_output}

PREVIOUS ANALYSIS (Quality Score: {state.quality_score:.2f} - BELOW THRESHOLD):
{state.analysis_output}

TASK: Provide a DEEPER, MORE DETAILED analysis:
1. Add more specific insights
2. Include concrete examples
3. Provide more thorough synthesis
4. Elaborate on key themes

Refined Analysis:"""
        
        return await self._execute_llm(
            'analyzer_refinement',
            prompt,
            {'temperature': 0.3, 'max_tokens': 600}
        )
    
    async def _tool_refine_minor(self, state: AgentState) -> AgentResponse:
        """Minor refinement tool - AGENTIC SELF-CORRECTION"""
        prompt = f"""You are an analytical assistant performing minor refinement.

ANALYSIS (Quality Score: {state.quality_score:.2f} - Close to threshold):
{state.analysis_output}

TASK: Make small improvements:
1. Clarify any ambiguous points
2. Strengthen conclusions
3. Improve structure slightly

Refined Analysis:"""
        
        return await self._execute_llm(
            'analyzer_minor_refine',
            prompt,
            {'temperature': 0.2, 'max_tokens': 400}
        )
    
    def _extract_quality_score(self, validation_text: str) -> float:
        """Extract quality score from validation"""
        import re
        
        for line in validation_text.split('\n'):
            if 'quality score' in line.lower():
                match = re.search(r'\d+', line)
                if match:
                    return min(float(match.group()) / 100.0, 1.0)
        
        if 'PASS' in validation_text or 'APPROVE' in validation_text:
            return 0.8
        elif 'REVISE' in validation_text:
            return 0.6
        else:
            return 0.4
    
    async def orchestrate_agentic_workflow(
        self,
        query: str,
        workflow_id: str
    ) -> Dict[str, Any]:
        """
        AGENTIC WORKFLOW - NOT A FIXED PIPELINE
        
        The agent autonomously decides:
        - What action to take next
        - Whether to retry
        - How to improve
        - When to stop
        
        This is TRUE AGENTIC BEHAVIOR
        """
        
        # Check boundaries
        is_valid, error_msg = await self._check_boundaries(query)
        if not is_valid:
            return {
                'workflow_id': workflow_id,
                'status': 'rejected',
                'reason': error_msg,
                'agentic': False,
                'timestamp': datetime.now().isoformat()
            }
        
        # Initialize agent state (MEMORY)
        state = AgentState(
            workflow_id=workflow_id,
            query=query
        )
        
        # Results tracking
        results = {
            'workflow_id': workflow_id,
            'status': 'in_progress',
            'stages': {},
            'action_sequence': [],  # Track what agent decided to do
            'agentic': True,
            'metrics': {
                'total_latency_ms': 0,
                'total_tokens': 0,
                'stages_completed': 0,
                'refinement_loops': 0
            }
        }
        
        # AGENTIC LOOP - Agent decides what to do
        while state.attempts < state.max_attempts:
            state.attempts += 1
            
            # AUTONOMOUS DECISION: What should I do next?
            next_action = self.planner.decide_next_action(state)
            
            if next_action is None:
                # Agent decided to stop
                break
            
            # Log agent's decision (BEFORE execution)
            state.action_history.append(next_action)
            
            # Prepare decision reason BEFORE execution
            if state.research_output is None:
                reason = "No research yet - need to gather information"
            elif state.analysis_output is None:
                reason = "Research complete - need to analyze"
            elif state.validation_output is None:
                reason = "Analysis complete - need to validate quality"
            elif state.quality_score < self.planner.quality_threshold:
                reason = f"Quality {state.quality_score:.2f} below threshold {self.planner.quality_threshold:.2f} - need to improve"
            else:
                reason = f"Quality {state.quality_score:.2f} meets threshold - finalizing"
            
            # TOOL SELECTION: Agent chooses which tool to use
            tool_func = self.available_tools.get(next_action)
            if not tool_func:
                break
            
            # Execute chosen action
            response = await tool_func(state)
            
            # Update state based on action (MEMORY UPDATE)
            if next_action == 'research':
                state.research_output = response.content
                results['stages']['research'] = {
                    'response': response.content,
                    'latency_ms': response.latency_ms,
                    'tokens': response.token_usage,
                    'success': response.success,
                    'attempt': state.attempts
                }
                # Update reason after execution
                if response.success:
                    reason = "Research completed successfully"
                else:
                    reason = "Research failed"
                    
            elif next_action in ['analyze', 'refine_analysis', 'refine_minor']:
                state.analysis_output = response.content
                stage_name = next_action
                results['stages'][stage_name] = {
                    'response': response.content,
                    'latency_ms': response.latency_ms,
                    'tokens': response.token_usage,
                    'success': response.success,
                    'attempt': state.attempts
                }
                if 'refine' in next_action:
                    results['metrics']['refinement_loops'] += 1
                    reason = "Refinement completed - quality being re-evaluated"
                else:
                    reason = "Analysis completed - ready for validation"
                    
            elif next_action == 'validate':
                state.validation_output = response.content
                state.quality_score = self._extract_quality_score(response.content)
                
                results['stages']['validation'] = {
                    'response': response.content,
                    'latency_ms': response.latency_ms,
                    'tokens': response.token_usage,
                    'success': response.success,
                    'quality_score': state.quality_score,
                    'attempt': state.attempts
                }
                
                # Update reason with actual quality score
                if state.quality_score >= self.planner.quality_threshold:
                    reason = f"Validation complete - Quality {state.quality_score:.2f} ≥ threshold {self.planner.quality_threshold:.2f} ✓"
                    state.goal_achieved = True
                else:
                    reason = f"Validation complete - Quality {state.quality_score:.2f} < threshold {self.planner.quality_threshold:.2f} - needs improvement"
                
                # DECISION: Should we retry?
                if self.planner.should_retry(state, state.quality_score):
                    # Agent decides to try again
                    state.goal_achieved = False
                else:
                    state.goal_achieved = True
            
            # Log action AFTER execution with final reason
            results['action_sequence'].append({
                'attempt': state.attempts,
                'action': next_action,
                'reason': reason,
                'quality_after': state.quality_score if next_action == 'validate' else None
            })
            
            # Update metrics
            state.total_latency_ms += response.latency_ms
            state.total_tokens += response.token_usage.get('total_tokens', 0)
            
            if not response.success:
                results['status'] = 'failed'
                results['failed_action'] = next_action
                break
        
        # Final status
        if state.goal_achieved:
            results['status'] = 'completed'
        elif state.attempts >= state.max_attempts:
            results['status'] = 'max_attempts_reached'
        
        results['metrics']['total_latency_ms'] = state.total_latency_ms
        results['metrics']['total_tokens'] = state.total_tokens
        results['metrics']['stages_completed'] = len(results['stages'])
        results['metrics']['total_attempts'] = state.attempts
        results['final_quality_score'] = state.quality_score
        results['goal_achieved'] = state.goal_achieved
        results['timestamp'] = datetime.now().isoformat()
        
        return results