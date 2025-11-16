"""
Integration Tests
Testing: End-to-end workflow testing, stress testing, noise tolerance
NOTE: These tests require a valid OpenAI API key
"""
import pytest
import asyncio
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import MultiAgentSystem
import time


# Skip these tests if no API key is provided
API_KEY = os.getenv('OPENAI_API_KEY', 'YOUR_API_KEY_HERE')
SKIP_INTEGRATION = API_KEY == 'YOUR_API_KEY_HERE'


@pytest.mark.skipif(SKIP_INTEGRATION, reason="No API key provided")
@pytest.mark.asyncio
class TestIntegration:
    """
    Integration Testing: Tests full system workflows
    Requires: Valid OpenAI API key in environment
    """
    
    @pytest.fixture
    async def system(self):
        """Fixture to create system instance"""
        return MultiAgentSystem(api_key=API_KEY)
    
    @pytest.mark.asyncio
    async def test_single_query_workflow(self, system):
        """
        Test complete workflow with a single query
        Validates: End-to-end processing
        """
        query = "What is software testing?"
        result = await system.process_query(query)
        
        assert result['status'] in ['completed', 'rejected']
        
        if result['status'] == 'completed':
            assert 'stages' in result
            assert 'research' in result['stages']
            assert 'analysis' in result['stages']
            assert 'validation' in result['stages']
            assert 'evaluation' in result
    
    @pytest.mark.asyncio
    async def test_boundary_enforcement(self, system):
        """
        Test that system boundaries are enforced
        System Engineering: Boundary validation
        """
        # Query with forbidden topic (medical advice)
        query = "How do I treat my illness?"
        result = await system.process_query(query)
        
        # Should be rejected due to boundaries
        assert result['status'] == 'rejected'
        assert 'forbidden topic' in result.get('reason', '').lower()
    
    @pytest.mark.asyncio
    async def test_latency_measurement(self, system):
        """
        Test that latency is measured correctly
        Non-functional Requirement: Performance monitoring
        """
        query = "Explain Agile methodology"
        result = await system.process_query(query)
        
        if result['status'] == 'completed':
            assert 'metrics' in result
            assert 'total_latency_ms' in result['metrics']
            assert result['metrics']['total_latency_ms'] > 0
    
    @pytest.mark.asyncio
    async def test_token_tracking(self, system):
        """
        Test that token usage is tracked
        Efficiency: Resource monitoring
        """
        query = "What is microservices architecture?"
        result = await system.process_query(query)
        
        if result['status'] == 'completed':
            assert 'metrics' in result
            assert 'total_tokens' in result['metrics']
            assert result['metrics']['total_tokens'] > 0
            
            # Check per-stage tokens
            for stage in result['stages'].values():
                assert 'tokens' in stage
                assert stage['tokens']['total_tokens'] > 0


@pytest.mark.skipif(SKIP_INTEGRATION, reason="No API key provided")
@pytest.mark.asyncio
class TestStressTesting:
    """
    Stress Testing: Tests system under load
    """
    
    @pytest.fixture
    async def system(self):
        return MultiAgentSystem(api_key=API_KEY)
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, system):
        """
        Stress Test: Multiple concurrent queries
        Tests: System stability under load
        """
        queries = [
            "What is Python?",
            "Explain Docker",
            "What is CI/CD?"
        ]
        
        # Execute queries concurrently
        tasks = [system.process_query(q) for q in queries]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check that at least some succeeded
        successful = sum(1 for r in results if isinstance(r, dict) and r.get('status') == 'completed')
        
        assert successful >= 1, "At least one request should succeed"
    
    @pytest.mark.asyncio
    async def test_sequential_load(self, system):
        """
        Stress Test: Sequential query load
        Tests: System consistency over time
        """
        queries = [
            "What is software design?",
            "Explain testing",
            "What is DevOps?"
        ]
        
        results = []
        for query in queries:
            result = await system.process_query(query)
            results.append(result)
            await asyncio.sleep(0.5)  # Small delay
        
        # Check consistency
        completed = [r for r in results if r['status'] == 'completed']
        
        if len(completed) >= 2:
            # Verify metrics are present
            for result in completed:
                assert 'evaluation' in result
                assert 'metrics' in result['evaluation']


@pytest.mark.skipif(SKIP_INTEGRATION, reason="No API key provided")
@pytest.mark.asyncio
class TestNoiseTolerance:
    """
    Noise Tolerance Testing: Tests system with noisy/edge-case inputs
    """
    
    @pytest.fixture
    async def system(self):
        return MultiAgentSystem(api_key=API_KEY)
    
    @pytest.mark.asyncio
    async def test_empty_query(self, system):
        """Test handling of empty query"""
        result = await system.process_query("")
        
        # System should handle gracefully
        assert 'status' in result
        assert result['status'] in ['completed', 'rejected', 'error']
    
    @pytest.mark.asyncio
    async def test_very_long_query(self, system):
        """Test handling of very long query"""
        long_query = "What is software engineering? " * 100
        result = await system.process_query(long_query)
        
        # System should handle or reject appropriately
        assert 'status' in result
    
    @pytest.mark.asyncio
    async def test_special_characters(self, system):
        """Test handling of special characters"""
        query = "What is @#$% testing!?! 🚀"
        result = await system.process_query(query)
        
        # Should process or reject gracefully
        assert 'status' in result
    
    @pytest.mark.asyncio
    async def test_ambiguous_query(self, system):
        """Test handling of ambiguous query"""
        query = "Tell me about it"
        result = await system.process_query(query)
        
        # System should attempt to process
        assert 'status' in result


@pytest.mark.skipif(SKIP_INTEGRATION, reason="No API key provided")
@pytest.mark.asyncio  
class TestRegressionBaseline:
    """
    Regression Testing: Establish and validate baselines
    """
    
    @pytest.fixture
    async def system(self):
        return MultiAgentSystem(api_key=API_KEY)
    
    @pytest.mark.asyncio
    async def test_baseline_query_consistency(self, system):
        """
        Test that same query produces consistent results
        Regression: Ensure no degradation
        """
        query = "What is Agile software development?"
        
        # Run same query twice
        result1 = await system.process_query(query)
        await asyncio.sleep(1)
        result2 = await system.process_query(query)
        
        if result1['status'] == 'completed' and result2['status'] == 'completed':
            # Check that both completed successfully
            assert result1['metrics']['stages_completed'] == result2['metrics']['stages_completed']
            
            # Latency should be within reasonable range (not regression)
            latency_diff = abs(result1['metrics']['total_latency_ms'] - result2['metrics']['total_latency_ms'])
            assert latency_diff < 5000, "Latency should be consistent"


if __name__ == "__main__":
    if SKIP_INTEGRATION:
        print("Skipping integration tests - no API key provided")
        print("Set OPENAI_API_KEY environment variable to run these tests")
    else:
        pytest.main([__file__, "-v", "-s"])