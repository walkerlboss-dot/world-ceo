#!/usr/bin/env python3
"""
Test suite for agent_generator.py
"""

import pytest
import json
import tempfile
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from agent_generator import AgentGenerator, GenerationResult


class TestGenerationResult:
    """Tests for GenerationResult dataclass."""
    
    def test_success_result(self):
        """Test successful generation result."""
        result = GenerationResult(
            success=True,
            agent_name="Test Agent",
            agent_dir=Path("/tmp/test"),
            spec_files={"SOUL.md": Path("/tmp/SOUL.md")},
            code_files={"skill.py": Path("/tmp/skill.py")}
        )
        
        assert result.success is True
        assert result.agent_name == "Test Agent"
        assert result.timestamp is not None
    
    def test_failure_result(self):
        """Test failed generation result."""
        result = GenerationResult(
            success=False,
            agent_name="Test Agent",
            error="Generation failed"
        )
        
        assert result.success is False
        assert result.error == "Generation failed"
    
    def test_to_dict(self):
        """Test result serialization."""
        result = GenerationResult(
            success=True,
            agent_name="Test Agent",
            agent_dir=Path("/tmp/test")
        )
        
        data = result.to_dict()
        assert data["success"] is True
        assert data["agent_name"] == "Test Agent"


class TestAgentGenerator:
    """Tests for AgentGenerator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.generator = AgentGenerator(output_dir=self.temp_dir)
    
    def test_generate_from_domain(self):
        """Test agent generation from domain description."""
        result = self.generator.generate_from_domain(
            name="Test Agent",
            description="A test agent",
            category="research",
            pain_points=["manual work"],
            data_sources=["API"],
            required_tools=["requests"],
            target_users="developers",
            deploy=False
        )
        
        assert result.success is True
        assert result.agent_name == "Test Agent"
        assert result.agent_dir is not None
        assert result.spec_files is not None
        assert result.code_files is not None
    
    def test_generate_from_spec_file(self):
        """Test agent generation from spec file."""
        # Create spec file
        spec = {
            "name": "File Test Agent",
            "description": "Test from file",
            "category": "data_processing",
            "pain_points": ["pain"],
            "data_sources": ["data"],
            "required_tools": ["tool"],
            "target_users": "users"
        }
        
        spec_path = Path(self.temp_dir) / "test_spec.json"
        spec_path.write_text(json.dumps(spec))
        
        result = self.generator.generate_from_spec_file(spec_path, deploy=False)
        
        assert result.success is True
        assert result.agent_name == "File Test Agent"
    
    def test_batch_generate(self):
        """Test batch agent generation."""
        domains = [
            {
                "name": "Agent 1",
                "description": "First agent",
                "category": "research",
                "pain_points": ["pain"],
                "data_sources": ["data"],
                "required_tools": ["tool"],
                "target_users": "users"
            },
            {
                "name": "Agent 2",
                "description": "Second agent",
                "category": "integration",
                "pain_points": ["pain"],
                "data_sources": ["data"],
                "required_tools": ["tool"],
                "target_users": "users"
            }
        ]
        
        results = self.generator.batch_generate(domains, deploy=False)
        
        assert len(results) == 2
        assert all(r.success for r in results)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
