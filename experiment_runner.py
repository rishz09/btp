"""
Experiment Runner - For collecting experimental data
Lifecycle: Agile iteration and experimentation
"""
import asyncio
import json
from datetime import datetime
from pathlib import Path
from main import MultiAgentSystem


class ExperimentRunner:
    """
    Experiment management for data collection and analysis
    Supports systematic experimentation for research
    """
    
    def __init__(self, api_key: str):
        self.system = MultiAgentSystem(api_key=api_key)
        self.results_dir = Path("experiment_results")
        self.results_dir.mkdir(exist_ok=True)
    
    async def run_experiment_suite(self, experiment_config: dict):
        """
        Run a complete experiment suite
        
        Args:
            experiment_config: Dictionary with experiment parameters
        """
        experiment_name = experiment_config.get('name', 'unnamed_experiment')
        queries = experiment_config.get('queries', [])
        iterations = experiment_config.get('iterations', 1)
        
        print(f"\n{'='*80}")
        print(f"Running Experiment: {experiment_name}")
        print(f"Queries: {len(queries)}")
        print(f"Iterations: {iterations}")
        print(f"{'='*80}\n")
        
        all_results = []
        
        for iteration in range(iterations):
            print(f"\nIteration {iteration + 1}/{iterations}")
            
            for i, query in enumerate(queries):
                print(f"  Query {i+1}/{len(queries)}: {query[:50]}...")
                
                result = await self.system.process_query(query)
                
                # Add experiment metadata
                result['experiment_name'] = experiment_name
                result['iteration'] = iteration + 1
                result['query_index'] = i + 1
                result['query_text'] = query
                
                all_results.append(result)
                
                await asyncio.sleep(0.5)  # Rate limiting
        
        # Save results
        self._save_results(experiment_name, all_results)
        
        # Generate analysis
        analysis = self._analyze_results(all_results)
        self._save_analysis(experiment_name, analysis)
        
        print(f"\n{'='*80}")
        print("Experiment completed!")
        print(f"Results saved to: {self.results_dir / experiment_name}")
        print(f"{'='*80}\n")
        
        return all_results, analysis
    
    def _save_results(self, experiment_name: str, results: list):
        """Save raw results to JSON"""
        experiment_dir = self.results_dir / experiment_name
        experiment_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = experiment_dir / f"results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
    
    def _analyze_results(self, results: list) -> dict:
        """Analyze experiment results"""
        completed = [r for r in results if r['status'] == 'completed']
        rejected = [r for r in results if r['status'] == 'rejected']
        failed = [r for r in results if r['status'] in ['failed', 'error']]
        
        analysis = {
            'summary': {
                'total_queries': len(results),
                'completed': len(completed),
                'rejected': len(rejected),
                'failed': len(failed),
                'success_rate': len(completed) / len(results) if results else 0
            },
            'performance': {},
            'quality': {},
            'requirements_compliance': {}
        }
        
        if completed:
            # Performance metrics
            latencies = [r['metrics']['total_latency_ms'] for r in completed]
            tokens = [r['metrics']['total_tokens'] for r in completed]
            
            analysis['performance'] = {
                'avg_latency_ms': sum(latencies) / len(latencies),
                'min_latency_ms': min(latencies),
                'max_latency_ms': max(latencies),
                'avg_tokens': sum(tokens) / len(tokens),
                'total_tokens': sum(tokens)
            }
            
            # Quality metrics
            accuracies = [r['evaluation']['metrics']['accuracy_score'] for r in completed]
            reliabilities = [r['evaluation']['metrics']['reliability_score'] for r in completed]
            
            analysis['quality'] = {
                'avg_accuracy': sum(accuracies) / len(accuracies),
                'min_accuracy': min(accuracies),
                'max_accuracy': max(accuracies),
                'avg_reliability': sum(reliabilities) / len(reliabilities)
            }
            
            # Requirements compliance
            requirements_met = [
                r['evaluation']['requirements_check']['all_requirements_met'] 
                for r in completed
            ]
            
            analysis['requirements_compliance'] = {
                'compliance_rate': sum(requirements_met) / len(requirements_met),
                'violations': len(requirements_met) - sum(requirements_met)
            }
        
        return analysis
    
    def _save_analysis(self, experiment_name: str, analysis: dict):
        """Save analysis results"""
        experiment_dir = self.results_dir / experiment_name
        experiment_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = experiment_dir / f"analysis_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(analysis, f, indent=2, default=str)
        
        # Also save as readable text
        text_filename = experiment_dir / f"analysis_{timestamp}.txt"
        with open(text_filename, 'w') as f:
            f.write(f"Experiment Analysis: {experiment_name}\n")
            f.write(f"{'='*80}\n\n")
            
            f.write("SUMMARY\n")
            f.write("-" * 40 + "\n")
            for key, value in analysis['summary'].items():
                f.write(f"{key}: {value}\n")
            
            if analysis['performance']:
                f.write("\nPERFORMANCE METRICS\n")
                f.write("-" * 40 + "\n")
                for key, value in analysis['performance'].items():
                    f.write(f"{key}: {value:.2f}\n")
            
            if analysis['quality']:
                f.write("\nQUALITY METRICS\n")
                f.write("-" * 40 + "\n")
                for key, value in analysis['quality'].items():
                    f.write(f"{key}: {value:.2f}\n")
            
            if analysis['requirements_compliance']:
                f.write("\nREQUIREMENTS COMPLIANCE\n")
                f.write("-" * 40 + "\n")
                for key, value in analysis['requirements_compliance'].items():
                    f.write(f"{key}: {value}\n")


async def main():
    """Run predefined experiments"""
    
    # REPLACE WITH YOUR API KEY
    API_KEY = 'YOUR_API_KEY_HERE'
    
    if API_KEY == "YOUR_API_KEY_HERE":
        print("ERROR: Please replace YOUR_API_KEY_HERE with your actual OpenAI API key")
        return
    
    runner = ExperimentRunner(api_key=API_KEY)
    
    # Experiment 1: Software Engineering Concepts
    experiment1 = {
        'name': 'software_engineering_concepts',
        'queries': [
            "What is requirements engineering?",
            "Explain software testing methodologies",
            "What are microservices?",
            "Describe Agile development",
            "What is CI/CD pipeline?"
        ],
        'iterations': 1
    }
    
    results1, analysis1 = await runner.run_experiment_suite(experiment1)
    
    print("\n=== Experiment 1 Analysis ===")
    print(json.dumps(analysis1, indent=2, default=str))
    
    # Experiment 2: Boundary Testing
    experiment2 = {
        'name': 'boundary_testing',
        'queries': [
            "What is Python programming?",  # Allowed
            "How do I treat my illness?",   # Forbidden - medical
            "What is machine learning?",    # Allowed
            "Give me financial advice",     # Forbidden - financial
            "Explain data structures"       # Allowed
        ],
        'iterations': 1
    }
    
    results2, analysis2 = await runner.run_experiment_suite(experiment2)
    
    print("\n=== Experiment 2 Analysis ===")
    print(json.dumps(analysis2, indent=2, default=str))
    
    # Experiment 3: Performance Testing (same query multiple times)
    experiment3 = {
        'name': 'performance_consistency',
        'queries': [
            "What is software architecture?"
        ],
        'iterations': 5
    }
    
    results3, analysis3 = await runner.run_experiment_suite(experiment3)
    
    print("\n=== Experiment 3 Analysis ===")
    print(json.dumps(analysis3, indent=2, default=str))


if __name__ == "__main__":
    asyncio.run(main())