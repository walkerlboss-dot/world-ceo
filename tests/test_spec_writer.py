#!/usr/bin/env python3
"""
Test suite for spec_writer.py
"""

import pytest
import json
import tempfile
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from spec_writer import SpecWriter, AgentSpec


class TestSpecWriter:
    """Tests for SpecWriter class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.writer = SpecWriter(output_dir=self.temp_dir)
    
    def test_slugify(self):
        """Test slug conversion."""
        assert self.writer._slugify("Test Agent") == "test-agent"
        assert self.writer._slugify("Test_Agent") == "test-agent"
        assert self.writer._slugify("test-agent") == "test-agent"
    
    def test_generate_soul_md(self):
        """Test SOUL.md generation."""
        spec = AgentSpec(
            name="Test Agent",
            domain="Testing",
            description="A test agent",
            category="research",
            personality_traits=["Reliable", "Efficient"],
            core_tools=["tool1"],
            skills=["skill1"],
            integrations=["integration1"],
            success_metrics=["metric1"],
            constraints=["constraint1"],
            escalation_rules={"rule1": "action1"}
        )
        
        content = self.writer.generate_soul_md(spec)
        
        assert "Test Agent" in content
        assert "Reliable" in content
        assert "constraint1" in content
    
    def test_generate_agents_md(self):
        """Test AGENT.md generation."""
        spec = AgentSpec(
            name="Test Agent",
            domain="Testing",
            description="A test agent",
            category="research",
            personality_traits=["Reliable"],
            core_tools=["tool1"],
            skills=["skill1"],
            integrations=["integration1"],
            success_metrics=["metric1"],
            constraints=["constraint1"],
            escalation_rules={"rule1": "action1"}
        )
        
        content = self.writer.generate_agents_md(spec)
        
        assert "Test Agent" in content
        assert "tool1" in content
        assert "rule1" in content
    
    def test_write_spec(self):
        """Test writing all spec files."""
        spec = AgentSpec(
            name="Test Agent",
            domain="Testing",
            description="A test agent",
            category="research",
            personality_traits=["Reliable"],
            core_tools=["tool1"],
            skills=["skill1"],
            integrations=["integration1"],
            success_metrics=["metric1"],
            constraints=["constraint1"],
            escalation_rules={"rule1": "action1"}
        )
        
        files = self.writer.write_spec(spec)
        
        assert "SOUL.md" in files
        assert "AGENT.md" in files
        assert "TOOLS.md" in files
        assert "HEARTBEAT.md" in files
        assert "spec.json" in files
        
        # Check files exist
        for path in files.values():
            assert path.exists()
    
    def test_create_from_domain(self):
        """Test creating spec from domain analysis."""
        domain = {
            "name": "Data Cleaner",
            "description": "Cleans data",
            "category": "data_processing",
            "required_tools": ["pandas"]
        }
        
        spec = self.writer.create_from_domain(domain)
        
        assert spec.name == "Data Cleaner"
        assert spec.category == "data_processing"
        assert len(spec.personality_traits) > 0
        assert len(spec.constraints) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
