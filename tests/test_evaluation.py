"""
Unit Tests for Evaluation Service
Testing: Metrics calculation, drift detection, requirements validation
"""
import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.evaluation_service import EvaluationService, EvaluationMetrics
from datetime import datetime


class TestEvaluationService:
    """
    Testing: Validation of evaluation logic
    Ensures metrics are calculated correctly
    """
    
    @pytest.fixture
    def eval_service(self):
        """Fixture to create evaluation service"""
        config = {
            'requirements': {
                'non_functional': {
                    'max_latency_ms': 10000,
                    'min_accuracy_threshold': 0.75,
                    'min_reliability_threshold': 0.95,
                    'max_token_usage_per_request': 2000
                }
            }
        }
        return EvaluationService(config)
    
    @pytest.fixture
    def sample_workflow_result(self):
        """Sample workflow result for testing"""
        return {
            'workflow_id': 'test_001',
            'status': 'completed',
            'stages': {
                'research': {
                    'response': 'Research findings here...',
                    'latency_ms': 1500,
                    'tokens': {
                        'prompt_tokens': 100,
                        'completion_tokens': 200,
                        'total_tokens': 300
                    },
                    'success': True
                },
                'analysis': {
                    'response': 'Analysis here...',
                    'latency_ms': 1200,
                    'tokens': {
                        'prompt_tokens': 150,
                        'completion_tokens': 180,
                        'total_tokens': 330
                    },
                    'success': True
                },
                'validation': {
                    'response': 'Overall Quality Score: 85\nRecommendation: APPROVE',
                    'latency_ms': 800,
                    'tokens': {
                        'prompt_tokens': 120,
                        'completion_tokens': 100,
                        'total_tokens': 220
                    },
                    'success': True
                }
            },
            'metrics': {
                'total_latency_ms': 3500,
                'total_tokens': 850,
                'stages_completed': 3
            }
        }
    
    def test_evaluate_workflow(self, eval_service, sample_workflow_result):
        """Test workflow evaluation"""
        metrics = eval_service.evaluate_workflow(sample_workflow_result)
        
        assert isinstance(metrics, EvaluationMetrics)
        assert metrics.workflow_id == 'test_001'
        assert metrics.accuracy_score > 0
        assert metrics.latency_ms > 0
        assert metrics.reliability_score == 1.0  # All stages succeeded
    
    def test_accuracy_calculation(self, eval_service, sample_workflow_result):
        """Test accuracy score calculation from validation"""
        metrics = eval_service.evaluate_workflow(sample_workflow_result)
        
        # Should extract 85/100 = 0.85 from the validation response
        assert metrics.accuracy_score >= 0.8
        assert metrics.accuracy_score <= 1.0
    
    def test_token_efficiency(self, eval_service, sample_workflow_result):
        """Test token efficiency calculation"""
        metrics = eval_service.evaluate_workflow(sample_workflow_result)
        
        # Total completion: 480, Total prompt: 370
        # Efficiency = 480/370 ≈ 1.3
        assert metrics.token_efficiency > 1.0  # Should generate more output than input
    
    def test_reliability_score_success(self, eval_service, sample_workflow_result):
        """Test reliability score for successful workflow"""
        metrics = eval_service.evaluate_workflow(sample_workflow_result)
        
        assert metrics.reliability_score == 1.0
    
    def test_reliability_score_partial_failure(self, eval_service, sample_workflow_result):
        """Test reliability score for partial failure"""
        sample_workflow_result['status'] = 'failed'
        sample_workflow_result['metrics']['stages_completed'] = 2
        
        metrics = eval_service.evaluate_workflow(sample_workflow_result)
        
        assert metrics.reliability_score < 1.0
        assert metrics.reliability_score == 2.0 / 3.0  # 2 out of 3 stages
    
    def test_check_non_functional_requirements_pass(self, eval_service, sample_workflow_result):
        """Test non-functional requirements check - passing case"""
        metrics = eval_service.evaluate_workflow(sample_workflow_result)
        results = eval_service.check_non_functional_requirements(metrics)
        
        assert results['latency_ok'] == True
        assert results['accuracy_ok'] == True
        assert results['reliability_ok'] == True
        assert results['all_requirements_met'] == True
    
    def test_check_non_functional_requirements_fail_latency(self, eval_service, sample_workflow_result):
        """Test non-functional requirements check - latency failure"""
        sample_workflow_result['metrics']['total_latency_ms'] = 15000  # Exceeds 10000ms limit
        
        metrics = eval_service.evaluate_workflow(sample_workflow_result)
        results = eval_service.check_non_functional_requirements(metrics)
        
        assert results['latency_ok'] == False
        assert results['all_requirements_met'] == False
    
    def test_drift_detection_insufficient_data(self, eval_service, sample_workflow_result):
        """Test drift detection with insufficient data"""
        drift = eval_service.detect_drift(window_size=10)
        
        assert drift['drift_detected'] == False
        assert drift['reason'] == 'Insufficient data'
    
    def test_drift_detection_with_data(self, eval_service, sample_workflow_result):
        """Test drift detection with sufficient data"""
        # Add multiple workflow evaluations
        for i in range(25):
            # Vary metrics slightly
            sample_workflow_result['workflow_id'] = f'test_{i:03d}'
            sample_workflow_result['metrics']['total_latency_ms'] = 3500 + (i * 10)
            
            eval_service.evaluate_workflow(sample_workflow_result)
        
        drift = eval_service.detect_drift(window_size=10)
        
        assert 'drift_detected' in drift
        assert 'baseline' in drift
        assert 'recent' in drift
    
    def test_generate_report(self, eval_service, sample_workflow_result):
        """Test report generation"""
        # Add some workflows
        for i in range(5):
            sample_workflow_result['workflow_id'] = f'test_{i:03d}'
            eval_service.evaluate_workflow(sample_workflow_result)
        
        report = eval_service.generate_report()
        
        assert report['total_workflows'] == 5
        assert 'average_accuracy' in report
        assert 'average_latency_ms' in report
        assert 'average_reliability' in report
        assert 'success_rate' in report
    
    def test_stage_metrics_extraction(self, eval_service, sample_workflow_result):
        """Test that stage-level metrics are extracted"""
        metrics = eval_service.evaluate_workflow(sample_workflow_result)
        
        assert 'research' in metrics.stage_metrics
        assert 'analysis' in metrics.stage_metrics
        assert 'validation' in metrics.stage_metrics
        
        assert metrics.stage_metrics['research']['latency_ms'] == 1500
        assert metrics.stage_metrics['research']['success'] == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])