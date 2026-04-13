#!/usr/bin/env python3
"""
Test suite for deployment_manager.py
"""

import pytest
import json
import tempfile
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from deployment_manager import DeploymentManager, DeploymentResult


class TestDeploymentResult:
    """Tests for DeploymentResult dataclass."""
    
    def test_success_result(self):
        """Test successful deployment result."""
        result = DeploymentResult(
            success=True,
            repo_url="https://github.com/test/repo",
            agent_id="test-agent"
        )
        
        assert result.success is True
        assert result.repo_url == "https://github.com/test/repo"
        assert result.agent_id == "test-agent"
        assert result.timestamp is not None
    
    def test_failure_result(self):
        """Test failed deployment result."""
        result = DeploymentResult(
            success=False,
            error="Authentication failed"
        )
        
        assert result.success is False
        assert result.error == "Authentication failed"


class TestDeploymentManager:
    """Tests for DeploymentManager class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = DeploymentManager(
            output_dir=self.temp_dir,
            github_org="test-org"
        )
    
    def test_slugify(self):
        """Test slug conversion."""
        assert self.manager._slugify("Test Agent") == "test-agent"
        assert self.manager._slugify("Test_Agent") == "test-agent"
    
    def test_generate_openclaw_config(self):
        """Test OpenClaw config generation."""
        spec = {
            "description": "Test agent",
            "category": "research",
            "core_tools": ["tool1", "tool2"]
        }
        
        config = self.manager.generate_openclaw_config("Test Agent", spec)
        
        assert config["agent"]["name"] == "Test Agent"
        assert config["agent"]["category"] == "research"
        assert "tool1" in config["tools"]["allowed"]
        assert config["routing"]["enabled"] is True
    
    def test_write_openclaw_config(self):
        """Test writing OpenClaw config file."""
        spec = {"description": "Test"}
        config = self.manager.generate_openclaw_config("Test Agent", spec)
        
        config_path = self.manager.write_openclaw_config("Test Agent", config)
        
        assert config_path.exists()
        
        # Verify content
        saved_config = json.loads(config_path.read_text())
        assert saved_config["agent"]["name"] == "Test Agent"
    
    def test_generate_github_actions(self):
        """Test GitHub Actions workflow generation."""
        workflow = self.manager.generate_github_actions("Test Agent")
        
        assert "name: CI/CD" in workflow
        assert "pytest" in workflow
        assert "flake8" in workflow


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
