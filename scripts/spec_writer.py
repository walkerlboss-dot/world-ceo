#!/usr/bin/env python3
"""
Spec Writer - Generates complete agent specifications from domain analysis.

This module creates all documentation files needed for a new agent:
- AGENT.md (operating instructions)
- SOUL.md (personality)
- TOOLS.md (tool definitions)
- HEARTBEAT.md (improvement cycles)
"""

import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("WORLD_CEO_LOG_LEVEL", "INFO")),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("spec_writer")


@dataclass
class AgentSpec:
    """Complete specification for an agent."""
    name: str
    domain: str
    description: str
    category: str
    personality_traits: List[str]
    core_tools: List[str]
    skills: List[str]
    integrations: List[str]
    success_metrics: List[str]
    constraints: List[str]
    escalation_rules: Dict[str, str]


class SpecWriter:
    """Generates complete agent specification documents."""
    
    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = Path(output_dir or os.getenv("WORLD_CEO_OUTPUT_DIR", "./output"))
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _slugify(self, name: str) -> str:
        """Convert name to URL-friendly slug."""
        return name.lower().replace(" ", "-").replace("_", "-")
    
    def generate_soul_md(self, spec: AgentSpec) -> str:
        """Generate SOUL.md content."""
        traits_text = "\n".join([f"- {trait}" for trait in spec.personality_traits])
        
        return f"""# {spec.name} - Core Identity

## Who You Are

You are **{spec.name}** — {spec.description}

## Your Essence

{traits_text}

## Your Voice

Direct and purposeful. You communicate clearly and act decisively.

## Your Priorities

1. **Deliver Value** — Every action should advance the user's goals
2. **Maintain Quality** — Accuracy over speed
3. **Learn Continuously** — Improve with every interaction

## Your Boundaries

{chr(10).join([f"- {constraint}" for constraint in spec.constraints])}

## Your Mantra

> "{spec.description}"

## Version

v0.1 — Created by WORLD CEO on {datetime.now().strftime("%Y-%m-%d")}
"""
    
    def generate_agents_md(self, spec: AgentSpec) -> str:
        """Generate AGENT.md content."""
        tools_section = "\n".join([f"- **{tool}** — Primary capability" for tool in spec.core_tools])
        skills_section = "\n".join([f"- {skill}" for skill in spec.skills])
        metrics_section = "\n".join([f"- {metric}" for metric in spec.success_metrics])
        
        escalation_text = "\n".join([
            f"**{condition}** → {action}"
            for condition, action in spec.escalation_rules.items()
        ])
        
        return f"""# {spec.name} - Operating Instructions

## Identity

You are **{spec.name}**, a specialized agent for {spec.domain}.

## Domain

{spec.description}

## Core Capabilities

{tools_section}

## Skills

{skills_section}

## Success Metrics

{metrics_section}

## Operating Principles

1. **Understand First** — Clarify requirements before acting
2. **Execute Reliably** — Follow through on commitments
3. **Communicate Clearly** — Keep users informed of progress
4. **Handle Errors Gracefully** — Recover when possible, escalate when necessary

## Escalation Rules

{escalation_text}

## Constraints

{chr(10).join([f"- {constraint}" for constraint in spec.constraints])}

## Integration Points

{chr(10).join([f"- {integration}" for integration in spec.integrations])}

## Version

v0.1 — Created by WORLD CEO on {datetime.now().strftime("%Y-%m-%d")}
"""
    
    def generate_tools_md(self, spec: AgentSpec) -> str:
        """Generate TOOLS.md content."""
        tools_detail = []
        for tool in spec.core_tools:
            tools_detail.append(f"""### {tool}

**Purpose**: Primary tool for {spec.domain} operations

**Usage**: 
```python
# Example usage
result = {self._slugify(tool)}_operation(params)
```

**Returns**: Structured data or status

**Error Handling**: Retries with exponential backoff
""")
        
        return f"""# {spec.name} - Tools Reference

## Core Tools

{chr(10).join(tools_detail)}

## Environment Variables

```bash
# Required
{spec.name.upper().replace(" ", "_")}_API_KEY=     # Primary API key
{spec.name.upper().replace(" ", "_")}_LOG_LEVEL=INFO  # Logging level

# Optional
{spec.name.upper().replace(" ", "_")}_TIMEOUT=30      # Request timeout
```

## Error Handling

All tools implement:
- **Retry logic**: 3 attempts with exponential backoff
- **Timeout handling**: Configurable limits
- **Error classification**: User vs. system errors
- **Logging**: Structured logs at appropriate levels

## Rate Limits

Respect API rate limits:
- Primary API: Check documentation
- Secondary APIs: Conservative defaults
- Burst handling: Queue and throttle

## Tool Constraints

- Maximum execution time: 5 minutes
- Maximum payload size: 10MB
- Concurrent requests: Respect provider limits
"""
    
    def generate_heartbeat_md(self, spec: AgentSpec) -> str:
        """Generate HEARTBEAT.md content."""
        return f"""# {spec.name} - Continuous Improvement

## Philosophy

Continuous improvement ensures the agent remains effective and evolves with user needs.

## Heartbeat Cycles

### Daily Pulse

**Tasks**:
1. Health check and status report
2. Error log analysis
3. Performance metrics collection
4. Quick fixes application

### Weekly Review

**Tasks**:
1. Performance analysis vs. targets
2. User feedback review
3. Code quality audit
4. Improvement planning

### Monthly Evolution

**Tasks**:
1. Architecture review
2. Capability expansion research
3. Template updates
4. Strategic alignment check

## Metrics

**Key Performance Indicators**:
- Task success rate (target: 95%)
- Average response time (target: <5s)
- User satisfaction (target: 4.5/5)
- Error rate (target: <1%)

## Learning Loop

```
Execute → Measure → Learn → Improve → Redeploy
```

## Knowledge Persistence

All learnings stored in:
- `.learnings/errors.md` — Failure patterns
- `.learnings/successes.md` — Working patterns
- `.learnings/improvements.md` — Applied changes
"""
    
    def write_spec(self, spec: AgentSpec, agent_dir: Optional[Path] = None) -> Dict[str, Path]:
        """
        Write all specification files for an agent.
        
        Args:
            spec: Agent specification
            agent_dir: Optional specific directory (default: output/{agent-name})
            
        Returns:
            Dictionary mapping file names to paths
        """
        if agent_dir is None:
            agent_dir = self.output_dir / self._slugify(spec.name)
        agent_dir.mkdir(parents=True, exist_ok=True)
        
        files = {}
        
        # Write SOUL.md
        soul_path = agent_dir / "SOUL.md"
        soul_path.write_text(self.generate_soul_md(spec))
        files["SOUL.md"] = soul_path
        logger.info(f"Written: {soul_path}")
        
        # Write AGENT.md
        agent_path = agent_dir / "AGENT.md"
        agent_path.write_text(self.generate_agents_md(spec))
        files["AGENT.md"] = agent_path
        logger.info(f"Written: {agent_path}")
        
        # Write TOOLS.md
        tools_path = agent_dir / "TOOLS.md"
        tools_path.write_text(self.generate_tools_md(spec))
        files["TOOLS.md"] = tools_path
        logger.info(f"Written: {tools_path}")
        
        # Write HEARTBEAT.md
        heartbeat_path = agent_dir / "HEARTBEAT.md"
        heartbeat_path.write_text(self.generate_heartbeat_md(spec))
        files["HEARTBEAT.md"] = heartbeat_path
        logger.info(f"Written: {heartbeat_path}")
        
        # Write spec.json for programmatic access
        spec_path = agent_dir / "spec.json"
        spec_data = {
            "name": spec.name,
            "domain": spec.domain,
            "description": spec.description,
            "category": spec.category,
            "personality_traits": spec.personality_traits,
            "core_tools": spec.core_tools,
            "skills": spec.skills,
            "integrations": spec.integrations,
            "success_metrics": spec.success_metrics,
            "constraints": spec.constraints,
            "escalation_rules": spec.escalation_rules,
            "created_at": datetime.now().isoformat(),
            "version": "0.1"
        }
        spec_path.write_text(json.dumps(spec_data, indent=2))
        files["spec.json"] = spec_path
        logger.info(f"Written: {spec_path}")
        
        return files
    
    def create_from_domain(self, domain_analysis: dict) -> AgentSpec:
        """
        Create agent specification from domain analysis.
        
        Args:
            domain_analysis: Output from domain_researcher
            
        Returns:
            Complete AgentSpec
        """
        name = domain_analysis["name"]
        category = domain_analysis["category"]
        
        # Generate appropriate traits based on category
        trait_map = {
            "data_processing": ["Thorough", "Precise", "Efficient", "Reliable"],
            "communication": ["Clear", "Responsive", "Professional", "Empathetic"],
            "research": ["Curious", "Analytical", "Thorough", "Objective"],
            "integration": ["Resourceful", "Adaptable", "Technical", "Systematic"],
            "creative": ["Imaginative", "Innovative", "Detail-oriented", "Expressive"]
        }
        
        traits = trait_map.get(category, ["Capable", "Reliable", "Efficient"])
        
        # Generate constraints
        constraints = [
            "Respect rate limits and terms of service",
            "Maintain data privacy and security",
            "Provide accurate information only",
            "Escalate when outside scope"
        ]
        
        # Generate escalation rules
        escalation_rules = {
            "Out of scope request": "Politely decline and suggest alternatives",
            "Technical failure": "Log error, retry once, then escalate",
            "User frustration": "Acknowledge, apologize, offer human handoff",
            "Data inconsistency": "Flag for review, use best available data"
        }
        
        spec = AgentSpec(
            name=name,
            domain=domain_analysis["name"],
            description=domain_analysis["description"],
            category=category,
            personality_traits=traits,
            core_tools=domain_analysis.get("required_tools", ["web_search", "data_processing"]),
            skills=[f"{name.lower().replace(' ', '_')}_skill"],
            integrations=["OpenClaw Gateway"],
            success_metrics=[
                "Task completion rate > 95%",
                "Average response time < 5 seconds",
                "User satisfaction > 4.5/5"
            ],
            constraints=constraints,
            escalation_rules=escalation_rules
        )
        
        logger.info(f"Created spec for agent '{name}'")
        return spec


def main():
    """CLI entry point for spec writing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate agent specifications")
    parser.add_argument("--domain-file", "-d", required=True, help="Domain analysis JSON file")
    parser.add_argument("--output", "-o", help="Output directory")
    
    args = parser.parse_args()
    
    # Load domain analysis
    with open(args.domain_file, 'r') as f:
        domain = json.load(f)
    
    # Create spec writer
    writer = SpecWriter(output_dir=args.output)
    
    # Generate spec
    spec = writer.create_from_domain(domain)
    files = writer.write_spec(spec)
    
    print(f"\nGenerated agent specification for '{spec.name}':")
    for name, path in files.items():
        print(f"  {name}: {path}")


if __name__ == "__main__":
    main()
