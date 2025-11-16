"""
AGENTIC Main Application
Uses the new agentic orchestration service instead of fixed pipeline

RUN THIS to see TRUE AGENTIC BEHAVIOR:
- Agent decides what to do next
- Agent loops to improve quality
- Agent has goals and plans
- NOT a fixed pipeline
"""
import asyncio
import yaml
import uuid
from datetime import datetime
from typing import Dict, Any

from services.prompt_library_service import PromptLibraryService
from services.agentic_orchestration_service import AgenticOrchestrationService
from services.evaluation_service import EvaluationService
from services.logging_service import LoggingService


class AgenticMultiAgentSystem:
    """
    TRUE AGENTIC AI SYSTEM
    
    Key differences from pipeline version:
    1. Uses agentic orchestration (not fixed pipeline)
    2. Agent decides actions autonomously
    3. Self-correction loops
    4. Goal-directed behavior
    """
    
    def __init__(self, api_key: str, config_path: str = "config.yaml"):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.prompt_library = PromptLibraryService(config_path)
        self.orchestrator = AgenticOrchestrationService(api_key, self.config)
        self.evaluator = EvaluationService(self.config)
        self.logger = LoggingService(log_dir="logs_agentic", config=self.config)
        
        self.logger.log_system('INFO', 'AGENTIC Multi-Agent System initialized', {
            'system_name': self.config['system']['name'],
            'version': self.config['system']['version'],
            'mode': 'AGENTIC'
        })
    
    async def process_query(self, query: str) -> Dict[str, Any]:
        """Process query through AGENTIC workflow"""
        workflow_id = str(uuid.uuid4())[:8]
        
        self.logger.log_system('INFO', f'Processing query with AGENTIC AI: {query}', {
            'workflow_id': workflow_id
        })
        
        try:
            # AGENTIC ORCHESTRATION (not fixed pipeline)
            workflow_result = await self.orchestrator.orchestrate_agentic_workflow(
                query,
                workflow_id
            )
            
            self.logger.log_workflow(workflow_result)
            
            if workflow_result['status'] == 'completed':
                # Standard evaluation still applies
                metrics = self.evaluator.evaluate_workflow(workflow_result)
                requirements_check = self.evaluator.check_non_functional_requirements(metrics)
                
                self.logger.log_metrics(metrics.model_dump())
                
                workflow_result['evaluation'] = {
                    'metrics': metrics.model_dump(),
                    'requirements_check': requirements_check
                }
                
                self.logger.log_system('INFO', 'AGENTIC workflow completed', {
                    'workflow_id': workflow_id,
                    'attempts': workflow_result['metrics']['total_attempts'],
                    'refinement_loops': workflow_result['metrics']['refinement_loops'],
                    'quality_score': workflow_result['final_quality_score'],
                    'goal_achieved': workflow_result['goal_achieved']
                })
            
            return workflow_result
            
        except Exception as e:
            self.logger.log_error(e, {'workflow_id': workflow_id, 'query': query})
            self.logger.log_system('ERROR', f'AGENTIC workflow failed: {str(e)}', {
                'workflow_id': workflow_id
            })
            
            return {
                'workflow_id': workflow_id,
                'status': 'error',
                'error': str(e),
                'agentic': True,
                'timestamp': datetime.now().isoformat()
            }
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        return {
            'system': self.config['system'],
            'mode': 'AGENTIC AI',
            'boundaries': self.config['boundaries'],
            'agents': list(self.config['agents'].keys()),
            'available_prompts': self.prompt_library.list_prompts(),
            'requirements': self.config['requirements'],
            'agentic_features': [
                'Goal-directed behavior',
                'Autonomous decision-making',
                'Self-correction loops',
                'Adaptive planning',
                'Dynamic tool selection',
                'Quality-driven refinement'
            ]
        }


async def run_agentic_example(system, query, label="Query"):
    print("\n" + "=" * 80)
    print(f"{label}")
    print("=" * 80)

    print(f"\nQuery: {query}")
    result = await system.process_query(query)

    print(f"\n✨ AGENTIC BEHAVIOR:")
    print(f"   Status: {result['status']}")
    print(f"   Goal Achieved: {result.get('goal_achieved', False)}")

    # Case 1: Rejection BEFORE workflow even starts
    if result.get("status") == "rejected":
        print("   ⚠ Query rejected by boundary checker.")
        print(f"   Reason: {result.get('reason')}")
        return result

    # Case 2: Workflow ended without producing metrics
    metrics = result.get("metrics")
    if not metrics:
        print("   ⚠ Workflow ended before producing metrics.")
        print(f"   Status: {result.get('status')}")
        return result

    # Print core metrics
    print(f"   Total Attempts: {metrics['total_attempts']}")
    print(f"   Refinement Loops: {metrics['refinement_loops']}")
    print(f"   Final Quality Score: {result.get('final_quality_score', 0):.2f}")

    print(f"\n📋 Agent's Action Sequence:")
    for action in result.get('action_sequence', []):
        q = action.get('quality_after')
        quality_info = f" → Quality: {q:.2f}" if q is not None else ""
        print(f"   Attempt {action['attempt']}: {action['action']}{quality_info}")
        print(f"      Reason: {action['reason']}")

    # Print the final synthesized output if completed
    if result['status'] == 'completed':
        print(f"\n📊 Final Output:")

        # Find whichever stage produced final analysis
        final_stage = None
        for stage_name in ['refine_minor', 'refine_analysis', 'analyze']:
            if stage_name in result['stages']:
                final_stage = stage_name
                break

        if final_stage:
            output = result['stages'][final_stage]['response']
            print(f"   {output[:300]}...")

    return result


async def main():
    """
    Main entry point - Shows AGENTIC behavior
    """
    # REPLACE WITH YOUR API KEY
    API_KEY = "YOUR_API_KEY_HERE"
    
    if API_KEY == "YOUR_API_KEY_HERE":
        print("ERROR: Please replace YOUR_API_KEY_HERE with your actual OpenAI API key")
        return
    
    system = AgenticMultiAgentSystem(api_key=API_KEY)
    
    # Example queries
    queries = [
        ("EXAMPLE 1: Simple Query (should achieve goal quickly)", 
        "How to increase revenue through stocks?"),

        # ("EXAMPLE 2: Complex Query (may trigger self-correction)", 
        # "Design a globally distributed, self-optimizing AI system that predicts supply-chain disruptions using a hybrid of microservices, "
        # "event-driven pipelines, and reinforcement learning, while ensuring ethical fairness constraints, zero-downtime scalability, and regulation "
        # "compliance (GDPR + CCPA). Compare at least three possible architectures, identify contradictions in the requirements, and propose a final "
        # "architecture that balances accuracy, ethics, latency, and operational cost. Provide a formal reasoning trace explaining each design choice.")

        ("EXAMPLE 2: Complex Query (may trigger self-correction)", 
         "What are microservices in software engineering?"
        )
    ]

    for label, query in queries:
        await run_agentic_example(system, query, label)

    
    # # Show the difference
    # print("\n" + "=" * 80)
    # print("🎯 AGENTIC vs PIPELINE COMPARISON")
    # print("=" * 80)
    
    # print("\n❌ OLD PIPELINE (agent_orchestration_service.py):")
    # print("   1. Always: Research → Analyze → Validate")
    # print("   2. Fixed sequence, no decisions")
    # print("   3. No retry if quality is low")
    # print("   4. No self-correction")
    # print("   5. Developer controls flow")
    
    # print("\n✅ NEW AGENTIC AI (agentic_orchestration_service.py):")
    # print("   1. Agent DECIDES: What action to take next")
    # print("   2. Dynamic sequence based on state")
    # print("   3. LOOPS BACK if quality < threshold")
    # print("   4. SELF-CORRECTS through refinement")
    # print("   5. Agent controls its own flow")
    
    # print(f"\n📈 Agentic Features Demonstrated:")
    # print(f"   ✓ Goal-directed: Works toward quality threshold ({system.orchestrator.planner.quality_threshold:.0%})")
    # print(f"   ✓ Planning: Planner decides next action")
    # print(f"   ✓ Autonomy: Agent chooses tools (research, analyze, refine)")
    # print(f"   ✓ Memory: State tracks progress and quality")
    # print(f"   ✓ Loops: Can retry up to 5 times")
    # print(f"   ✓ Decision-making: Not hardcoded pipeline")
    
    # print("\n" + "=" * 80)
    # print("Logs saved to: logs_agentic/")
    # print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())