"""
Unit Tests for Prompt Library Service
Testing: Unit tests for prompt templates and validation
"""
import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.prompt_library_service import PromptLibraryService, PromptTemplate


class TestPromptLibraryService:
    """
    Testing Principle: Unit tests for individual components
    Validates prompt template management and rendering
    """
    
    @pytest.fixture
    def prompt_service(self):
        """Fixture to create a fresh prompt library service"""
        return PromptLibraryService()
    
    def test_initialization(self, prompt_service):
        """Test that default prompts are initialized"""
        prompts = prompt_service.list_prompts()
        
        assert len(prompts) > 0, "Should have default prompts"
        assert 'researcher_query' in prompts
        assert 'analyzer_synthesis' in prompts
        assert 'validator_check' in prompts
    
    def test_get_prompt(self, prompt_service):
        """Test retrieving a prompt template"""
        template = prompt_service.get_prompt('researcher_query')
        
        assert template is not None
        assert template.name == 'researcher_query'
        assert template.role == 'researcher'
        assert len(template.variables) > 0
    
    def test_render_prompt_success(self, prompt_service):
        """Test successful prompt rendering"""
        rendered = prompt_service.render_prompt(
            'researcher_query',
            topic="Machine Learning",
            allowed_topics="research, analysis",
            forbidden_topics="medical advice",
            max_length=400
        )
        
        assert rendered is not None
        assert "Machine Learning" in rendered
        assert "research, analysis" in rendered
    
    def test_render_prompt_missing_variable(self, prompt_service):
        """Test that missing variables raise an error"""
        with pytest.raises(ValueError, match="Missing required variables"):
            prompt_service.render_prompt(
                'researcher_query',
                topic="Machine Learning"
                # Missing other required variables
            )
    
    def test_register_new_prompt(self, prompt_service):
        """Test registering a new prompt template"""
        new_prompt = PromptTemplate(
            name="test_prompt",
            version="1.0.0",
            template="Test template with {variable}",
            variables=["variable"],
            role="tester"
        )
        
        success = prompt_service.register_prompt(new_prompt)
        assert success
        
        retrieved = prompt_service.get_prompt("test_prompt")
        assert retrieved is not None
        assert retrieved.name == "test_prompt"
    
    def test_get_prompt_metadata(self, prompt_service):
        """Test retrieving prompt metadata"""
        metadata = prompt_service.get_prompt_metadata('researcher_query')
        
        assert metadata is not None
        assert 'name' in metadata
        assert 'version' in metadata
        assert 'role' in metadata
        assert 'variables' in metadata
        assert 'constraints' in metadata
        assert 'success_criteria' in metadata
    
    def test_prompt_constraints(self, prompt_service):
        """Test that prompts have defined constraints"""
        template = prompt_service.get_prompt('researcher_query')
        
        assert 'max_tokens' in template.constraints
        assert 'temperature' in template.constraints
        assert template.constraints['max_tokens'] > 0
    
    def test_prompt_success_criteria(self, prompt_service):
        """Test that prompts have success criteria defined"""
        template = prompt_service.get_prompt('researcher_query')
        
        assert len(template.success_criteria) > 0
        assert 'min_points' in template.success_criteria or 'factual' in template.success_criteria


if __name__ == "__main__":
    pytest.main([__file__, "-v"])