"""
Prompt Library Service - Microservice for managing prompt templates
Implements Software Design principles: Modularity, Role Specialization
"""
from typing import Dict, Optional, List, Any
from pydantic import BaseModel, Field
import yaml
import json
from datetime import datetime


class PromptTemplate(BaseModel):
    """Structured prompt template with validation"""
    name: str
    version: str
    template: str
    variables: List[str]
    role: str
    constraints: Dict[str, Any] = Field(default_factory=dict)
    success_criteria: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    last_modified: datetime = Field(default_factory=datetime.now)


class PromptLibraryService:
    """
    Requirements Engineering: Captures functional and non-functional needs
    - Functional: Template management, version control, validation
    - Non-Functional: Fast retrieval, maintainability, reusability
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        self.prompts: Dict[str, PromptTemplate] = {}
        self.config = self._load_config(config_path)
        self._initialize_default_prompts()
        
    def _load_config(self, path: str) -> dict:
        """Load system configuration"""
        try:
            with open(path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return {}
    
    def _initialize_default_prompts(self):
        """System Engineering: Define boundaries and roles for each agent"""
        
        # Researcher Agent Prompts
        self.register_prompt(PromptTemplate(
            name="researcher_query",
            version="1.0.0",
            template="""You are a research assistant tasked with gathering information.

BOUNDARIES:
- Focus ONLY on: {allowed_topics}
- DO NOT provide advice on: {forbidden_topics}
- Maximum response length: {max_length} words

TASK: Research the following topic and provide key findings:
Topic: {topic}

Requirements:
1. Provide factual, verifiable information
2. Include 3-5 key points
3. Be concise and structured
4. Cite reasoning where applicable

Response:""",
            variables=["topic", "allowed_topics", "forbidden_topics", "max_length"],
            role="researcher",
            constraints={
                "max_tokens": 500,
                "temperature": 0.3
            },
            success_criteria={
                "min_points": 3,
                "max_points": 5,
                "factual": True
            }
        ))
        
        # Analyzer Agent Prompts
        self.register_prompt(PromptTemplate(
            name="analyzer_synthesis",
            version="1.0.0",
            template="""You are an analytical assistant that synthesizes information.

ROLE: Analyze and synthesize the provided research findings.

INPUT RESEARCH:
{research_data}

ANALYSIS REQUIREMENTS:
1. Identify main themes and patterns
2. Highlight key insights (2-4 insights)
3. Note any contradictions or gaps
4. Provide a coherent summary

Constraints:
- Be objective and analytical
- Maximum {max_length} words
- Focus on synthesis, not repetition

Analysis:""",
            variables=["research_data", "max_length"],
            role="analyzer",
            constraints={
                "max_tokens": 500,
                "temperature": 0.2
            },
            success_criteria={
                "min_insights": 2,
                "max_insights": 4,
                "synthesis_quality": "high"
            }
        ))
        
        # Validator Agent Prompts
        self.register_prompt(PromptTemplate(
            name="validator_check",
            version="1.0.0",
            template="""You are a quality validation assistant.

ROLE: Validate the quality and accuracy of the analysis.

ANALYSIS TO VALIDATE:
{analysis}

VALIDATION CHECKLIST:
1. Logical consistency: Are the conclusions logical?
2. Completeness: Does it address the original query?
3. Clarity: Is it clear and well-structured?
4. Factual accuracy: Are claims reasonable and supported?

Provide validation results in this format:
- Logical Consistency: [PASS/FAIL] - [brief reason]
- Completeness: [PASS/FAIL] - [brief reason]
- Clarity: [PASS/FAIL] - [brief reason]
- Factual Accuracy: [PASS/FAIL] - [brief reason]
- Overall Quality Score: [0-100]
- Recommendation: [APPROVE/REVISE/REJECT]

Validation Result:""",
            variables=["analysis"],
            role="validator",
            constraints={
                "max_tokens": 300,
                "temperature": 0.1
            },
            success_criteria={
                "min_quality_score": 75,
                "required_checks": ["logical_consistency", "completeness", "clarity", "factual_accuracy"]
            }
        ))
    
    def register_prompt(self, prompt: PromptTemplate) -> bool:
        """Register a new prompt template"""
        self.prompts[prompt.name] = prompt
        return True
    
    def get_prompt(self, name: str) -> Optional[PromptTemplate]:
        """Retrieve a prompt template by name"""
        return self.prompts.get(name)
    
    def render_prompt(self, name: str, **kwargs) -> Optional[str]:
        """
        Render a prompt template with provided variables
        Implements: Requirements validation
        """
        template = self.get_prompt(name)
        if not template:
            return None
        
        # Validate all required variables are provided
        missing_vars = set(template.variables) - set(kwargs.keys())
        if missing_vars:
            raise ValueError(f"Missing required variables: {missing_vars}")
        
        try:
            return template.template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Invalid variable in template: {e}")
    
    def list_prompts(self) -> List[str]:
        """List all available prompts"""
        return list(self.prompts.keys())
    
    def get_prompt_metadata(self, name: str) -> Optional[Dict]:
        """Get metadata about a prompt for testing and documentation"""
        template = self.get_prompt(name)
        if not template:
            return None
        
        return {
            "name": template.name,
            "version": template.version,
            "role": template.role,
            "variables": template.variables,
            "constraints": template.constraints,
            "success_criteria": template.success_criteria,
            "created_at": template.created_at.isoformat(),
            "last_modified": template.last_modified.isoformat()
        }