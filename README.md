<<<<<<< HEAD
# Multi-Agent AI System with Software Engineering Best Practices

## Project Overview

This project demonstrates the application of **Software Engineering processes to Prompt Engineering and Agentic AI**. It implements a multi-agent research assistant system that adheres to rigorous software engineering principles.

### Software Engineering Principles Implemented

#### 1. **System Engineering**

- **Boundary Definition**: Clear boundaries for what AI agents should/shouldn't do (see `config.yaml`)
- **Forbidden Topics**: Medical advice, legal advice, financial advice, personal diagnosis
- **Allowed Topics**: Research, summarization, analysis, fact-checking
- **Rate Limiting**: Configurable request limits

#### 2. **Requirements Engineering**

- **Functional Requirements**: Multi-agent coordination, prompt templating, response validation
- **Non-Functional Requirements**:
  - Max Latency: 10,000ms
  - Min Accuracy: 75%
  - Min Reliability: 95%
  - Max Tokens: 2,000 per request
- **Success Metrics**: Defined in prompt templates with validation criteria
- **Prompt Checklists**: Structured templates with required variables

#### 3. **Software Design**

- **Modularity**: Separate services for different concerns
- **Role Specialization**: Researcher, Analyzer, Validator agents with specific responsibilities
- **Integration Plan**: Clear multi-agent workflow pipeline
- **Prompt Libraries**: Reusable, versioned prompt templates

#### 4. **Lifecycle**

- **Agile Methodology**: Iterative development with continuous testing
- **Continuous Improvement**: Metrics collection for refinement

#### 5. **Architecture**

- **Microservices Pattern**:
  - Prompt Library Service
  - Agent Orchestration Service
  - Evaluation Service
  - Logging Service
- **Containerization**: Docker support for deployment
- **Service Independence**: Each service operates independently

#### 6. **Quality Attributes**

**Maintainability:**

- Model drift detection
- Structured logging (JSONL format)
- Clear service separation

**Dependability:**

- Reliability score calculation
- Error handling and recovery
- Audit trails via logging

**Efficiency:**

- Latency tracking per stage
- Token usage monitoring
- Token efficiency metrics

**Usability:**

- Clear metrics presentation
- Comprehensive reports
- Structured error messages

#### 7. **Testing**

- **Unit Tests**: Individual component validation
- **Integration Tests**: End-to-end workflow testing
- **Stress Tests**: Concurrent request handling
- **Regression Tests**: Baseline validation
- **Noise Tolerance**: Edge case handling
- **Test Framework**: pytest with async support

## Project Structure

```
.
├── config.yaml                           # System configuration
├── main.py                               # Main application entry point
├── experiment_runner.py                  # Automated experiment execution
├── requirements.txt                      # Python dependencies
├── Dockerfile                           # Container configuration
├── docker-compose.yml                   # Multi-container setup
├── services/
│   ├── prompt_library_service.py        # Prompt template management
│   ├── agent_orchestration_service.py   # Multi-agent coordination
│   ├── evaluation_service.py            # Metrics and quality assessment
│   └── logging_service.py               # Structured logging
├── tests/
│   ├── test_prompt_library.py           # Unit tests for prompts
│   ├── test_evaluation.py               # Unit tests for evaluation
│   └── test_integration.py              # Integration & stress tests
├── logs/                                # Generated logs (created at runtime)
│   ├── workflows.jsonl
│   ├── metrics.jsonl
│   ├── errors.jsonl
│   └── system.log
└── experiment_results/                  # Experimental data (created at runtime)
    └── [experiment_name]/
        ├── results_[timestamp].json
        └── analysis_[timestamp].json
```

## Installation & Setup

### Prerequisites

- Python 3.10 or higher
- OpenAI API key
- Docker (optional, for containerized deployment)

### Step 1: Clone/Download the Project

Create a project directory and save all provided files in their respective locations.

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Configure API Key

You have two options:

**Option A: Direct Edit (Quickest)**

1. Open `main.py`
2. Find line: `API_KEY = "YOUR_API_KEY_HERE"`
3. Replace with your actual OpenAI API key: `API_KEY = "sk-..."`

**Option B: Environment Variable (Recommended for production)**

```bash
export OPENAI_API_KEY="sk-..."  # Linux/Mac
# OR
set OPENAI_API_KEY=sk-...       # Windows
```

### Step 4: Verify Configuration

Check that `config.yaml` contains your desired settings:

- Boundaries (allowed/forbidden topics)
- Agent configurations
- Non-functional requirements
- Testing parameters

## Running the System

### Basic Execution

Run the main application with example queries:

```bash
python main.py
```

This will:

1. Initialize all microservices
2. Execute a single query example
3. Run a batch experiment with multiple queries
4. Display metrics and validation results
5. Generate logs in the `logs/` directory

**Expected Output:**

- System initialization details
- Agent responses (research, analysis, validation)
- Performance metrics (latency, tokens, accuracy)
- Requirements compliance check
- Aggregate statistics

### Running Experiments

For systematic data collection:

```bash
python experiment_runner.py
```

This runs predefined experiments:

1. **Software Engineering Concepts**: Tests domain knowledge
2. **Boundary Testing**: Validates system boundaries
3. **Performance Consistency**: Tests reproducibility

Results are saved in `experiment_results/[experiment_name]/`

### Running Tests

**Unit Tests Only:**

```bash
pytest tests/test_prompt_library.py -v
pytest tests/test_evaluation.py -v
```

**All Tests (requires API key):**

```bash
export OPENAI_API_KEY="sk-..."
pytest tests/ -v
```

**Specific Test Categories:**

```bash
# Integration tests
pytest tests/test_integration.py::TestIntegration -v

# Stress tests
pytest tests/test_integration.py::TestStressTesting -v

# Noise tolerance tests
pytest tests/test_integration.py::TestNoiseTolerance -v
```

### Docker Deployment

**Build and run with Docker Compose:**

```bash
# Set API key in environment
export OPENAI_API_KEY="sk-..."

# Build and start
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## Collecting Experimental Data

### Data Sources

1. **Workflow Logs** (`logs/workflows.jsonl`)

   - Each line is a JSON object with workflow execution details
   - Contains: workflow_id, status, stages_completed, latency, tokens

2. **Metrics Logs** (`logs/metrics.jsonl`)

   - Evaluation metrics for each workflow
   - Contains: accuracy_score, reliability_score, token_efficiency

3. **Experiment Results** (`experiment_results/`)
   - Structured JSON files with complete execution traces
   - Analysis summaries with aggregate statistics

### Analyzing Data

**Python Analysis:**

```python
import json

# Load workflow logs
with open('logs/workflows.jsonl', 'r') as f:
    workflows = [json.loads(line) for line in f]

# Calculate average latency
avg_latency = sum(w['total_latency_ms'] for w in workflows) / len(workflows)
print(f"Average Latency: {avg_latency:.2f}ms")

# Load metrics
with open('logs/metrics.jsonl', 'r') as f:
    metrics = [json.loads(line) for line in f]

# Calculate average accuracy
avg_accuracy = sum(m['accuracy_score'] for m in metrics) / len(metrics)
print(f"Average Accuracy: {avg_accuracy:.2%}")
```

**Command Line:**

```bash
# Count successful workflows
grep '"status": "completed"' logs/workflows.jsonl | wc -l

# Extract all latencies
grep -o '"total_latency_ms": [0-9.]*' logs/workflows.jsonl

# View recent metrics
tail -n 10 logs/metrics.jsonl | jq .
```

## Experimental Metrics Available

### Performance Metrics

- **Latency**: Per-stage and total response time (ms)
- **Token Usage**: Prompt tokens, completion tokens, total tokens
- **Token Efficiency**: Ratio of output to input tokens
- **Throughput**: Requests processed per unit time

### Quality Metrics

- **Accuracy Score**: 0-1 scale based on validation
- **Reliability Score**: Stage completion success rate
- **Validation Pass Rate**: Percentage of approved results

### Requirements Compliance

- **Latency Compliance**: % within threshold
- **Accuracy Compliance**: % meeting minimum accuracy
- **Reliability Compliance**: % meeting reliability target
- **Overall Compliance Rate**: All requirements met

### Drift Detection

- **Accuracy Drift**: Change from baseline
- **Latency Drift**: Performance degradation
- **Reliability Drift**: Consistency changes

## Customization

### Adding New Agents

1. **Update `config.yaml`:**

```yaml
agents:
  my_new_agent:
    model: "gpt-4o-mini"
    temperature: 0.4
    max_tokens: 400
    role: "Custom processing"
```

2. **Create Prompt Template:**

```python
# In prompt_library_service.py
self.register_prompt(PromptTemplate(
    name="my_agent_prompt",
    version="1.0.0",
    template="Your custom prompt with {variables}",
    variables=["variables"],
    role="my_new_agent"
))
```

### Modifying Boundaries

Edit `config.yaml`:

```yaml
boundaries:
  allowed_topics:
    - your_new_topic
  forbidden_topics:
    - restricted_topic
```

### Adjusting Requirements

Edit `config.yaml`:

```yaml
requirements:
  non_functional:
    max_latency_ms: 5000 # Stricter latency
    min_accuracy_threshold: 0.85 # Higher accuracy
```

## Experimental Design Tips

### For Performance Studies

- Run 20-30 identical queries to establish baseline
- Measure: latency distribution, token usage patterns
- Compare: different temperature settings, model versions

### For Accuracy Studies

- Use diverse query sets
- Implement ground truth validation
- Measure: accuracy scores, validation pass rates

### For Reliability Studies

- Test edge cases and boundary conditions
- Introduce artificial failures
- Measure: error rates, recovery success

### For Drift Detection

- Run long-term monitoring (100+ queries)
- Establish baseline early (first 10-20 queries)
- Monitor: accuracy, latency, reliability trends

## Troubleshooting

### API Key Errors

```
Error: OpenAI API key not found
```

**Solution**: Ensure API key is set correctly in `main.py` or environment

### Import Errors

```
ModuleNotFoundError: No module named 'openai'
```

**Solution**: Run `pip install -r requirements.txt`

### Test Failures

```
tests/test_integration.py::test_query FAILED
```

**Solution**: Integration tests require valid API key. Set `OPENAI_API_KEY` environment variable.

### Rate Limiting

```
Error: Rate limit exceeded
```

**Solution**: Add delays between requests or reduce concurrent load

## Citation & Documentation

When citing this work in your project documentation:

```
This implementation demonstrates software engineering best practices for
prompt engineering and agentic AI systems, including:
- Microservices architecture with independent services
- Comprehensive testing (unit, integration, stress, regression)
- Non-functional requirements validation (latency, accuracy, reliability)
- Systematic boundary enforcement and role specialization
- Continuous monitoring with drift detection
- Structured logging and audit trails
```

## Future Enhancements

- [ ] Redis integration for distributed rate limiting
- [ ] Prometheus metrics exporter
- [ ] GraphQL API for service queries
- [ ] Real-time dashboard for monitoring
- [ ] A/B testing framework for prompt variants
- [ ] Automated prompt optimization based on metrics

## License

This is an educational project for demonstrating software engineering practices in AI systems.

---

**Ready to run?** Start with: `python main.py`

**Need data?** Use: `python experiment_runner.py`

**Questions?** Check the code comments - they're comprehensive!
=======
# btp
Adopting Software Engineering Processes for Agentic AI and Prompt Engineering
>>>>>>> 5295148c940fcf3e3e9deb60c4c7e03ee476c157
