"""
Main Application - Entry point for the Multi-Agent System
Lifecycle: Agile - Supports iterative development and testing
Architecture: Microservices - Coordinates independent services
"""
import asyncio
import yaml
import uuid
from datetime import datetime
from typing import Dict, Any

from services.prompt_library_service import PromptLibraryService
from services.agent_orchestration_service import AgentOrchestrationService
from services.evaluation_service import EvaluationService
from services.logging_service import LoggingService


class MultiAgentSystem:
    """
    Main system coordinator implementing software engineering best practices
    """
    
    def __init__(self, api_key: str, config_path: str = "config.yaml"):
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Initialize microservices
        self.prompt_library = PromptLibraryService(config_path)
        self.orchestrator = AgentOrchestrationService(api_key, self.config)
        self.evaluator = EvaluationService(self.config)
        self.logger = LoggingService(config=self.config)
        
        self.logger.log_system('INFO', 'Multi-Agent System initialized', {
            'system_name': self.config['system']['name'],
            'version': self.config['system']['version']
        })
    
    async def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process a user query through the multi-agent workflow
        Returns: Complete workflow result with metrics and evaluation
        """
        workflow_id = str(uuid.uuid4())[:8]
        
        self.logger.log_system('INFO', f'Processing query: {query}', {
            'workflow_id': workflow_id
        })
        
        try:
            # Execute multi-agent workflow
            workflow_result = await self.orchestrator.orchestrate_multi_agent_workflow(
                query, 
                workflow_id
            )
            
            # Log workflow execution
            self.logger.log_workflow(workflow_result)
            
            # Evaluate the workflow
            if workflow_result['status'] == 'completed':
                metrics = self.evaluator.evaluate_workflow(workflow_result)
                
                # Check non-functional requirements
                requirements_check = self.evaluator.check_non_functional_requirements(metrics)
                
                # Log metrics
                # self.logger.log_metrics(metrics.dict())
                self.logger.log_metrics(metrics.model_dump())
                
                # Add evaluation to result
                workflow_result['evaluation'] = {
                    # 'metrics': metrics.dict(),
                    'metrics': metrics.model_dump(),
                    'requirements_check': requirements_check
                }
                
                self.logger.log_system('INFO', 'Workflow completed successfully', {
                    'workflow_id': workflow_id,
                    'accuracy': metrics.accuracy_score,
                    'latency_ms': metrics.latency_ms
                })
            
            return workflow_result
            
        except Exception as e:
            self.logger.log_error(e, {'workflow_id': workflow_id, 'query': query})
            self.logger.log_system('ERROR', f'Workflow failed: {str(e)}', {
                'workflow_id': workflow_id
            })
            
            return {
                'workflow_id': workflow_id,
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def run_batch_experiment(self, queries: list, experiment_name: str) -> Dict[str, Any]:
        """
        Run batch experiments for data collection
        Useful for testing and evaluation
        """
        self.logger.log_system('INFO', f'Starting batch experiment: {experiment_name}', {
            'num_queries': len(queries)
        })
        
        results = []
        
        for i, query in enumerate(queries):
            print(f"\nProcessing query {i+1}/{len(queries)}: {query[:50]}...")
            result = await self.process_query(query)
            results.append(result)
            
            # Small delay to respect rate limits
            await asyncio.sleep(1)
        
        # Generate aggregate report
        report = self.evaluator.generate_report()
        
        # Check for drift
        drift_analysis = self.evaluator.detect_drift()
        
        experiment_summary = {
            'experiment_name': experiment_name,
            'total_queries': len(queries),
            'results': results,
            'aggregate_metrics': report,
            'drift_analysis': drift_analysis,
            'timestamp': datetime.now().isoformat()
        }
        
        self.logger.log_system('INFO', f'Batch experiment completed: {experiment_name}', {
            'total_queries': len(queries),
            'success_rate': report.get('success_rate', 0)
        })
        
        return experiment_summary
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information and status"""
        return {
            'system': self.config['system'],
            'boundaries': self.config['boundaries'],
            'agents': list(self.config['agents'].keys()),
            'available_prompts': self.prompt_library.list_prompts(),
            'requirements': self.config['requirements']
        }


async def main():
    """
    Main entry point - Replace YOUR_API_KEY_HERE with your OpenAI API key
    """
    # REPLACE THIS WITH YOUR OPENAI API KEY
    API_KEY = "YOUR_API_KEY_HERE"
    
    if API_KEY == "YOUR_API_KEY_HERE":
        print("ERROR: Please replace YOUR_API_KEY_HERE with your actual OpenAI API key in main.py")
        return
    
    # Initialize system
    system = MultiAgentSystem(api_key=API_KEY)
    
    print("=" * 80)
    print("Multi-Agent Research Assistant System")
    print("Demonstrating Software Engineering Practices for Prompt Engineering")
    print("=" * 80)
    
    # Display system info
    info = system.get_system_info()
    print(f"\nSystem: {info['system']['name']} v{info['system']['version']}")
    print(f"Agents: {', '.join(info['agents'])}")
    print(f"Available Prompts: {', '.join(info['available_prompts'])}")
    
    # Example 1: Single query
    print("\n" + "=" * 80)
    print("EXAMPLE 1: Single Query Processing")
    print("=" * 80)
    
    query = "What are the key principles of software engineering?"
    print(f"\nQuery: {query}")
    
    result = await system.process_query(query)
    
    print(f"\nStatus: {result['status']}")
    
    if result['status'] == 'completed':
        print("\n--- Research Stage ---")
        print(result['stages']['research']['response'][:300] + "...")
        
        print("\n--- Analysis Stage ---")
        print(result['stages']['analysis']['response'][:300] + "...")
        
        print("\n--- Validation Stage ---")
        print(result['stages']['validation']['response'][:400] + "...")
        
        print("\n--- Metrics ---")
        metrics = result['evaluation']['metrics']
        print(f"Accuracy Score: {metrics['accuracy_score']:.2f}")
        print(f"Total Latency: {metrics['latency_ms']:.2f}ms")
        print(f"Token Efficiency: {metrics['token_efficiency']:.2f}")
        print(f"Reliability: {metrics['reliability_score']:.2f}")
        
        print("\n--- Requirements Check ---")
        req_check = result['evaluation']['requirements_check']
        for req, passed in req_check.items():
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"{req}: {status}")
    
    # Example 2: Batch experiment
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Batch Experiment (Multiple Queries)")
    print("=" * 80)
    
    test_queries = [
        "Explain microservices architecture",
        "What is Agile methodology?",
        # "Describe the importance of testing in software development"
    ]
    
    experiment_result = await system.run_batch_experiment(
        queries=test_queries,
        experiment_name="Software Engineering Concepts"
    )
    

    ### --------------------------------------- Added from GPT ------------------------------------------------------------------
    print("\n--- Individual Query Results ---")

    for i, res in enumerate(experiment_result['results'], 1):
        print(f"\n===== Query {i}/{len(experiment_result['results'])} =====")
        print(f"Query: {res.get('query', '(not logged)')}")

        if res['status'] != 'completed':
            print("❌ Failed")
            print(f"Error: {res.get('error')}")
            continue

    print("\n--- Research Stage ---")
    print(res['stages']['research']['response'][:300] + "...\n")

    print("--- Analysis Stage ---")
    print(res['stages']['analysis']['response'][:300] + "...\n")

    print("--- Validation Stage ---")
    print(res['stages']['validation']['response'][:400] + "...\n")

    metrics = res['evaluation']['metrics']
    print("--- Metrics ---")
    print(f"Accuracy: {metrics['accuracy_score']:.2f}")
    print(f"Latency: {metrics['latency_ms']:.2f}ms")
    print(f"Efficiency: {metrics['token_efficiency']:.2f}")
    print(f"Reliability: {metrics['reliability_score']:.2f}")

    req = res['evaluation']['requirements_check']
    print("\n--- Requirements ---")
    for k, v in req.items():
        print(f"{k}: {'✓' if v else '✗'}")

    ### -----------------------------------------------------------------------------------------------------------------------

    print("\n--- Experiment Summary ---")
    print(f"Total Queries: {experiment_result['total_queries']}")
    
    agg_metrics = experiment_result['aggregate_metrics']
    print(f"\nAggregate Metrics:")
    print(f"  Average Accuracy: {agg_metrics['average_accuracy']:.2f}")
    print(f"  Average Latency: {agg_metrics['average_latency_ms']:.2f}ms")
    print(f"  Average Reliability: {agg_metrics['average_reliability']:.2f}")
    print(f"  Success Rate: {agg_metrics['success_rate']:.2%}")
    
    drift = experiment_result['drift_analysis']
    print(f"\nDrift Detection: {'⚠ DETECTED' if drift['drift_detected'] else '✓ NO DRIFT'}")
    
    print("\n" + "=" * 80)
    print("Experiments completed! Check the 'logs/' directory for detailed logs.")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())


# import asyncio
# import yaml
# import uuid
# from datetime import datetime
# from typing import Dict, Any

# from services.prompt_library_service import PromptLibraryService
# from services.agent_orchestration_service import AgentOrchestrationService
# from services.evaluation_service import EvaluationService
# from services.logging_service import LoggingService


# class MultiAgentSystem:
#     """Main system coordinator implementing software engineering best practices"""

#     def __init__(self, api_key: str, config_path: str = "config.yaml"):
#         with open(config_path, "r") as f:
#             self.config = yaml.safe_load(f)

#         self.prompt_library = PromptLibraryService(config_path)
#         self.orchestrator = AgentOrchestrationService(api_key, self.config)
#         self.evaluator = EvaluationService(self.config)
#         self.logger = LoggingService(config=self.config)

#         self.logger.log_system(
#             "INFO",
#             "Multi-Agent System initialized",
#             {"system_name": self.config["system"]["name"], "version": self.config["system"]["version"]},
#         )

#     async def process_query(self, query: str) -> Dict[str, Any]:
#         workflow_id = str(uuid.uuid4())[:8]

#         self.logger.log_system("INFO", f"Processing query: {query}", {"workflow_id": workflow_id})
#         try:
#             workflow_result = await self.orchestrator.orchestrate_multi_agent_workflow(query, workflow_id)
#             self.logger.log_workflow(workflow_result)

#             if workflow_result["status"] == "completed":
#                 metrics = self.evaluator.evaluate_workflow(workflow_result)
#                 requirements_check = self.evaluator.check_non_functional_requirements(metrics)
#                 self.logger.log_metrics(metrics.model_dump())

#                 workflow_result["evaluation"] = {
#                     "metrics": metrics.model_dump(),
#                     "requirements_check": requirements_check,
#                 }

#                 self.logger.log_system(
#                     "INFO",
#                     "Workflow completed successfully",
#                     {
#                         "workflow_id": workflow_id,
#                         "accuracy": metrics.accuracy_score,
#                         "latency_ms": metrics.latency_ms,
#                     },
#                 )
#             return workflow_result

#         except Exception as e:
#             self.logger.log_error(e, {"workflow_id": workflow_id, "query": query})
#             self.logger.log_system("ERROR", f"Workflow failed: {str(e)}", {"workflow_id": workflow_id})
#             return {
#                 "workflow_id": workflow_id,
#                 "status": "error",
#                 "error": str(e),
#                 "timestamp": datetime.now().isoformat(),
#             }

#     async def run_batch_experiment(self, queries: list, experiment_name: str) -> Dict[str, Any]:
#         self.logger.log_system("INFO", f"Starting batch experiment: {experiment_name}", {"num_queries": len(queries)})
#         results = []

#         for i, query in enumerate(queries):
#             print(f"\nProcessing query {i+1}/{len(queries)}: {query[:50]}...")
#             result = await self.process_query(query)
#             results.append(result)
#             await asyncio.sleep(1)

#         report = self.evaluator.generate_report()
#         drift_analysis = self.evaluator.detect_drift()

#         experiment_summary = {
#             "experiment_name": experiment_name,
#             "total_queries": len(queries),
#             "results": results,
#             "aggregate_metrics": report,
#             "drift_analysis": drift_analysis,
#             "timestamp": datetime.now().isoformat(),
#         }

#         self.logger.log_system(
#             "INFO",
#             f"Batch experiment completed: {experiment_name}",
#             {"total_queries": len(queries), "success_rate": report.get("success_rate", 0)},
#         )
#         return experiment_summary

#     def get_system_info(self) -> Dict[str, Any]:
#         return {
#             "system": self.config["system"],
#             "boundaries": self.config["boundaries"],
#             "agents": list(self.config["agents"].keys()),
#             "available_prompts": self.prompt_library.list_prompts(),
#             "requirements": self.config["requirements"],
#         }


# async def main():
#     API_KEY = "YOUR_API_KEY_HERE"

#     if API_KEY == "YOUR_API_KEY_HERE":
#         print("ERROR: Please replace YOUR_API_KEY_HERE with your actual OpenAI API key in main.py")
#         return

#     system = MultiAgentSystem(api_key=API_KEY)

#     print("=" * 80)
#     print("Multi-Agent Research Assistant System")
#     print("Demonstrating Software Engineering Practices for Prompt Engineering")
#     print("=" * 80)

#     info = system.get_system_info()
#     print(f"\nSystem: {info['system']['name']} v{info['system']['version']}")
#     print(f"Agents: {', '.join(info['agents'])}")
#     print(f"Available Prompts: {', '.join(info['available_prompts'])}")

#     # --------------------------------------------------------------------------
#     # INTERACTIVE MENU
#     # --------------------------------------------------------------------------
#     while True:
#         print("\n" + "=" * 80)
#         print("Choose an option:")
#         print("1. Single Query Processing")
#         print("2. Batch Experiment")
#         print("3. Exit")
#         choice = input("Enter choice (1/2/3): ").strip()

#         if choice == "1":
#             query = input("\nEnter your query: ").strip()
#             if not query:
#                 print("❌ No query entered.")
#                 continue

#             result = await system.process_query(query)
#             print(f"\nStatus: {result['status']}")

#             if result["status"] == "completed":
#                 print("\n--- Research Stage ---")
#                 print(result["stages"]["research"]["response"][:300] + "...")

#                 print("\n--- Analysis Stage ---")
#                 print(result["stages"]["analysis"]["response"][:300] + "...")

#                 print("\n--- Validation Stage ---")
#                 print(result["stages"]["validation"]["response"][:400] + "...")

#                 metrics = result["evaluation"]["metrics"]
#                 print("\n--- Metrics ---")
#                 print(f"Accuracy: {metrics['accuracy_score']:.2f}")
#                 print(f"Latency: {metrics['latency_ms']:.2f}ms")
#                 print(f"Efficiency: {metrics['token_efficiency']:.2f}")
#                 print(f"Reliability: {metrics['reliability_score']:.2f}")

#         elif choice == "2":
#             n = input("Enter number of queries in batch: ").strip()
#             try:
#                 n = int(n)
#             except ValueError:
#                 print("❌ Invalid number.")
#                 continue

#             queries = []
#             for i in range(n):
#                 q = input(f"Enter query {i+1}: ").strip()
#                 if q:
#                     queries.append(q)

#             if not queries:
#                 print("❌ No queries entered.")
#                 continue

#             exp_name = input("Enter experiment name: ").strip() or "Unnamed Experiment"
#             experiment_result = await system.run_batch_experiment(queries, exp_name)

#             print("\n--- Experiment Summary ---")
#             agg = experiment_result["aggregate_metrics"]
#             print(f"Total Queries: {experiment_result['total_queries']}")
#             print(f"Average Accuracy: {agg['average_accuracy']:.2f}")
#             print(f"Average Latency: {agg['average_latency_ms']:.2f}ms")
#             print(f"Average Reliability: {agg['average_reliability']:.2f}")
#             print(f"Success Rate: {agg['success_rate']:.2%}")

#             drift = experiment_result["drift_analysis"]
#             print(f"Drift Detection: {'⚠ DETECTED' if drift['drift_detected'] else '✓ NO DRIFT'}")

#         elif choice == "3":
#             print("\nExiting. Check 'logs/' directory for detailed reports.")
#             break

#         else:
#             print("❌ Invalid choice. Please select 1, 2, or 3.")


# if __name__ == "__main__":
#     asyncio.run(main())
