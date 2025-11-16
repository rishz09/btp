"""
Evaluation Service - Microservice for quality assessment and metrics
Implements: Testing, Monitoring, Dependability, Efficiency tracking
"""
import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
from pydantic import BaseModel
import statistics


class EvaluationMetrics(BaseModel):
    """Structured evaluation metrics"""
    workflow_id: str
    accuracy_score: float
    latency_ms: float
    token_efficiency: float
    reliability_score: float
    timestamp: datetime
    stage_metrics: Dict[str, Any] = {}


class EvaluationService:
    """
    Maintainability: Monitor system health
    Dependability: Measure reliability
    Efficiency: Track performance metrics
    """
    
    def __init__(self, config: dict):
        self.config = config
        self.requirements = config.get('requirements', {}).get('non_functional', {})
        self.metrics_history: List[EvaluationMetrics] = []
        self.baseline_metrics: Optional[Dict] = None
        
    def evaluate_workflow(self, workflow_result: Dict[str, Any]) -> EvaluationMetrics:
        """
        Comprehensive workflow evaluation
        Captures multiple dimensions of quality
        """
        workflow_id = workflow_result.get('workflow_id', 'unknown')
        stages = workflow_result.get('stages', {})
        metrics = workflow_result.get('metrics', {})
        
        # 1. Accuracy Score (based on validation)
        accuracy_score = self._calculate_accuracy(stages)
        
        # 2. Latency Analysis
        total_latency = metrics.get('total_latency_ms', 0)
        
        # 3. Token Efficiency (output tokens per input token)
        token_efficiency = self._calculate_token_efficiency(stages)
        
        # 4. Reliability Score (stage success rate)
        reliability_score = self._calculate_reliability(workflow_result)
        
        eval_metrics = EvaluationMetrics(
            workflow_id=workflow_id,
            accuracy_score=accuracy_score,
            latency_ms=total_latency,
            token_efficiency=token_efficiency,
            reliability_score=reliability_score,
            timestamp=datetime.now(),
            stage_metrics=self._extract_stage_metrics(stages)
        )
        
        self.metrics_history.append(eval_metrics)
        return eval_metrics
    
    def _calculate_accuracy(self, stages: Dict) -> float:
        """
        Calculate accuracy based on validation results
        Parses validation response for quality score
        """
        validation = stages.get('validation', {})
        if not validation.get('success', False):
            return 0.0
        
        response = validation.get('response', '')
        
        # Parse quality score from validation response
        try:
            for line in response.split('\n'):
                if 'quality score' in line.lower():
                    # Extract number between 0-100
                    import re
                    match = re.search(r'\d+', line)
                    if match:
                        score = float(match.group())
                        return min(score / 100.0, 1.0)  # Normalize to 0-1
        except Exception:
            pass
        
        # Default: Check if validation passed
        if 'PASS' in response or 'APPROVE' in response:
            return 0.8  # Default good score
        elif 'REVISE' in response:
            return 0.6  # Medium score
        else:
            return 0.4  # Lower score
    
    def _calculate_token_efficiency(self, stages: Dict) -> float:
        """
        Efficiency: Measure token usage efficiency
        Higher ratio = more output per input token
        """
        total_prompt_tokens = 0
        total_completion_tokens = 0
        
        for stage in stages.values():
            tokens = stage.get('tokens', {})
            total_prompt_tokens += tokens.get('prompt_tokens', 0)
            total_completion_tokens += tokens.get('completion_tokens', 0)
        
        if total_prompt_tokens == 0:
            return 0.0
        
        return total_completion_tokens / total_prompt_tokens
    
    def _calculate_reliability(self, workflow_result: Dict) -> float:
        """
        Dependability: Calculate reliability score
        Based on successful completion and error rates
        """
        status = workflow_result.get('status')
        stages = workflow_result.get('stages', {})
        
        if status == 'rejected':
            return 0.0
        
        if status == 'failed':
            completed = workflow_result.get('metrics', {}).get('stages_completed', 0)
            total = 3  # We have 3 stages
            return completed / total if total > 0 else 0.0
        
        # All stages completed
        return 1.0
    
    def _extract_stage_metrics(self, stages: Dict) -> Dict[str, Any]:
        """Extract per-stage metrics for detailed analysis"""
        stage_metrics = {}
        
        for stage_name, stage_data in stages.items():
            stage_metrics[stage_name] = {
                'latency_ms': stage_data.get('latency_ms', 0),
                'tokens': stage_data.get('tokens', {}),
                'success': stage_data.get('success', False)
            }
        
        return stage_metrics
    
    def check_non_functional_requirements(
        self, 
        metrics: EvaluationMetrics
    ) -> Dict[str, bool]:
        """
        Requirements Engineering: Validate non-functional requirements
        Returns pass/fail for each requirement
        """
        results = {}
        
        # Latency requirement
        max_latency = self.requirements.get('max_latency_ms', 10000)
        results['latency_ok'] = metrics.latency_ms <= max_latency
        
        # Accuracy requirement
        min_accuracy = self.requirements.get('min_accuracy_threshold', 0.75)
        results['accuracy_ok'] = metrics.accuracy_score >= min_accuracy
        
        # Reliability requirement
        min_reliability = self.requirements.get('min_reliability_threshold', 0.95)
        results['reliability_ok'] = metrics.reliability_score >= min_reliability
        
        # Token efficiency (custom threshold)
        results['token_efficiency_ok'] = metrics.token_efficiency > 0.5
        
        results['all_requirements_met'] = all(results.values())
        
        return results
    
    def detect_drift(self, window_size: int = 10) -> Dict[str, Any]:
        """
        Maintainability: Detect model drift over time
        Compares recent metrics to historical baseline
        """
        if len(self.metrics_history) < window_size:
            return {
                'drift_detected': False,
                'reason': 'Insufficient data',
                'samples': len(self.metrics_history)
            }
        
        # Get recent metrics
        recent = self.metrics_history[-window_size:]
        
        # Calculate baseline if not set
        if self.baseline_metrics is None and len(self.metrics_history) >= window_size * 2:
            baseline = self.metrics_history[:window_size]
            self.baseline_metrics = {
                'accuracy': statistics.mean([m.accuracy_score for m in baseline]),
                'latency': statistics.mean([m.latency_ms for m in baseline]),
                'reliability': statistics.mean([m.reliability_score for m in baseline])
            }
        
        if self.baseline_metrics is None:
            return {
                'drift_detected': False,
                'reason': 'Baseline not established',
                'samples': len(self.metrics_history)
            }
        
        # Compare recent to baseline
        recent_accuracy = statistics.mean([m.accuracy_score for m in recent])
        recent_latency = statistics.mean([m.latency_ms for m in recent])
        recent_reliability = statistics.mean([m.reliability_score for m in recent])
        
        drift_threshold = 0.15  # 15% change
        
        accuracy_drift = abs(recent_accuracy - self.baseline_metrics['accuracy']) / (self.baseline_metrics['accuracy'] + 0.001)
        latency_drift = abs(recent_latency - self.baseline_metrics['latency']) / (self.baseline_metrics['latency'] + 0.001)
        reliability_drift = abs(recent_reliability - self.baseline_metrics['reliability']) / (self.baseline_metrics['reliability'] + 0.001)
        
        drift_detected = (
            accuracy_drift > drift_threshold or
            latency_drift > drift_threshold or
            reliability_drift > drift_threshold
        )
        
        return {
            'drift_detected': drift_detected,
            'accuracy_drift': accuracy_drift,
            'latency_drift': latency_drift,
            'reliability_drift': reliability_drift,
            'baseline': self.baseline_metrics,
            'recent': {
                'accuracy': recent_accuracy,
                'latency': recent_latency,
                'reliability': recent_reliability
            }
        }
    
    def generate_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive evaluation report
        Usability: Clear metrics presentation
        """
        if not self.metrics_history:
            # return {'error': 'No metrics available'}
            return {
                'total_workflows': 0,
                'average_accuracy': 0,
                'average_latency_ms': 0,
                'average_reliability': 0,
                'average_token_efficiency': 0,
                'success_rate': 0,
                'timestamp': datetime.now().isoformat()
            }
        
        return {
            'total_workflows': len(self.metrics_history),
            'average_accuracy': statistics.mean([m.accuracy_score for m in self.metrics_history]),
            'average_latency_ms': statistics.mean([m.latency_ms for m in self.metrics_history]),
            'average_reliability': statistics.mean([m.reliability_score for m in self.metrics_history]),
            'average_token_efficiency': statistics.mean([m.token_efficiency for m in self.metrics_history]),
            'success_rate': sum(1 for m in self.metrics_history if m.reliability_score == 1.0) / len(self.metrics_history),
            'timestamp': datetime.now().isoformat()
        }