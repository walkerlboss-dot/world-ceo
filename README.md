# WORLD CEO Agent v0.1

An autonomous agent that builds other specialized agents. WORLD CEO identifies opportunities, designs agent architectures, generates production-ready code, and deploys them into the OpenClaw ecosystem.

## Mission

Create specialized agents at scale. Identify domain opportunities, architect solutions, generate code, and deploy — all autonomously.

## Architecture

```
WORLD CEO
├── Domain Researcher    - Continuously scans for opportunities
├── Spec Writer         - Designs agent architecture
├── Code Generator      - Generates production code
├── Deployment Manager  - Deploys to GitHub/OpenClaw
└── Self-Improver       - Analyzes and evolves
```

## Quick Start

### Installation

```bash
git clone https://github.com/openclaw-agents/world-ceo.git
cd world-ceo
pip install -r requirements.txt
```

### Generate an Agent

```bash
# From domain description
python scripts/agent_generator.py \
  --name "Data Cleaner" \
  --description "Cleans and validates messy data" \
  --category data_processing \
  --pain-points "manual cleaning" "inconsistent formats" \
  --data-sources "CSV files" "JSON APIs" \
  --tools "pandas" "requests" \
  --target-users "data analysts"

# From spec file
python scripts/agent_generator.py --spec-file domain.json

# Generate and deploy
python scripts/agent_generator.py --spec-file domain.json --deploy
```

### Batch Generation

```python
from scripts.agent_generator import AgentGenerator

generator = AgentGenerator()

domains = [
    {"name": "Agent 1", "description": "...", "category": "research", ...},
    {"name": "Agent 2", "description": "...", "category": "integration", ...}
]

results = generator.batch_generate(domains)
```

## Components

### 1. Domain Researcher (`scripts/domain_researcher.py`)

Identifies and scores agent opportunities.

```python
from scripts.domain_researcher import DomainResearcher

researcher = DomainResearcher()
analysis = researcher.analyze_domain(
    name="Data Cleaner",
    description="Cleans messy data",
    category="data_processing",
    pain_points=["manual work"],
    data_sources=["CSV", "API"],
    required_tools=["pandas"],
    target_users="analysts"
)

print(f"Score: {analysis.score.total}/100")
```

### 2. Spec Writer (`scripts/spec_writer.py`)

Generates complete agent specifications.

```python
from scripts.spec_writer import SpecWriter

writer = SpecWriter()
spec = writer.create_from_domain(analysis.to_dict())
files = writer.write_spec(spec)
```

Generates:
- `SOUL.md` - Personality and identity
- `AGENT.md` - Operating instructions
- `TOOLS.md` - Tool definitions
- `HEARTBEAT.md` - Improvement cycles
- `spec.json` - Machine-readable spec

### 3. Code Generator (`scripts/code_generator.py`)

Generates production-ready Python code.

```python
from scripts.code_generator import CodeGenerator

generator = CodeGenerator()
code = generator.generate_code("Agent Name", spec)
files = generator.write_code("Agent Name", code)
```

Generates:
- Skill module with error handling
- Configuration module
- Utilities (retry, JSON parsing)
- Test suite
- Requirements.txt
- README.md

### 4. Deployment Manager (`scripts/deployment_manager.py`)

Handles GitHub and OpenClaw integration.

```python
from scripts.deployment_manager import DeploymentManager

manager = DeploymentManager()
result = manager.deploy(
    "Agent Name",
    spec,
    push_to_github=True,
    configure_openclaw=True
)
```

### 5. Self-Improver (`scripts/self_improver.py`)

Analyzes failures and updates patterns.

```python
from scripts.self_improver import SelfImprover

improver = SelfImprover()
improver.run_improvement_cycle(log_dir=Path("./logs"))
```

## Domain Scoring

Domains are scored on four dimensions (0-25 each):

| Dimension | Description |
|-----------|-------------|
| Pain | How acute is the problem? |
| Data | Is quality data available? |
| Tools | Can we build effective tools? |
| Value | What's the potential impact? |

**Scoring**:
- 80-100: High priority
- 60-79: Viable
- <60: Reject

## Directory Structure

```
world-ceo/
├── SPEC.md                    # Project specification
├── AGENTS.md                  # Operating instructions
├── SOUL.md                    # Personality
├── TOOLS.md                   # Tool reference
├── HEARTBEAT.md              # Improvement cycles
├── README.md                  # This file
├── LICENSE                    # MIT License
├── requirements.txt           # Dependencies
├── scripts/                   # Core modules
│   ├── agent_generator.py    # Master orchestrator
│   ├── domain_researcher.py  # Opportunity identification
│   ├── spec_writer.py        # Spec generation
│   ├── code_generator.py     # Code generation
│   ├── deployment_manager.py # Deployment
│   └── self_improver.py      # Continuous improvement
├── templates/                 # Code templates
│   ├── agent_template.py
│   └── SKILL.md.template
└── tests/                     # Test suite
    ├── test_agent_generator.py
    ├── test_domain_researcher.py
    ├── test_spec_writer.py
    ├── test_code_generator.py
    ├── test_deployment_manager.py
    └── test_self_improver.py
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_agent_generator.py -v

# With coverage
pytest tests/ --cov=scripts --cov-report=html
```

## Environment Variables

```bash
# API Keys
BRAVE_API_KEY=              # For web search
BROWSERBASE_API_KEY=        # For browser automation
BROWSERBASE_PROJECT_ID=     # Browserbase project
GH_TOKEN=                   # GitHub CLI token

# Configuration
WORLD_CEO_LOG_LEVEL=INFO    # DEBUG, INFO, WARN, ERROR
WORLD_CEO_OUTPUT_DIR=./output
WORLD_CEO_GITHUB_ORG=openclaw-agents
OPENCLAW_CONFIG_PATH=/path/to/config
```

## Continuous Improvement

WORLD CEO maintains continuous heartbeat cycles:

- **Daily Pulse** (every 6 hours): Health checks, log analysis
- **Weekly Review**: Performance analysis, user feedback
- **Monthly Evolution**: Architecture review, capability expansion

Run manually:
```bash
python scripts/self_improver.py --cycle --log-dir ./logs
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit a pull request

## License

MIT License - See LICENSE file

## Created By

Generated by WORLD CEO v0.1 — An autonomous agent builder

---

**Status**: v0.1 — Initial release
**Last Updated**: 2026-04-13
