#!/usr/bin/env python3
"""
Test suite for code_generator.py
"""

import pytest
import tempfile
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from code_generator import CodeGenerator, CodePackage


class TestCodeGenerator:
    """Tests for CodeGenerator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.generator = CodeGenerator(output_dir=self.temp_dir)
    
    def test_slugify(self):
        """Test slug conversion."""
        assert self.generator._slugify("Test Agent") == "test_agent"
        assert self.generator._slugify("Test-Agent") == "test_agent"
    
    def test_classify(self):
        """Test class name conversion."""
        assert self.generator._classify("test_agent") == "TestAgent"
        assert self.generator._classify("data_cleaner") == "DataCleaner"
    
    def test_generate_skill_py(self):
        """Test skill Python code generation."""
        spec = {"description": "Test agent"}
        code = self.generator.generate_skill_py("Test Agent", spec)
        
        assert "Test Agent" in code
        assert "TestAgentSkill" in code
        assert "TaskResult" in code
        assert "def execute" in code
    
    def test_generate_skill_md(self):
        """Test SKILL.md generation."""
        spec = {"description": "Test agent"}
        content = self.generator.generate_skill_md("Test Agent", spec)
        
        assert "Test Agent" in content
        assert "Installation" in content
        assert "Usage" in content
    
    def test_generate_config_py(self):
        """Test config module generation."""
        spec = {}
        code = self.generator.generate_config_py("Test Agent", spec)
        
        assert "@dataclass" in code
        assert "Config" in code
        assert "from_env" in code
    
    def test_generate_utils_py(self):
        """Test utils module generation."""
        spec = {}
        code = self.generator.generate_utils_py("Test Agent", spec)
        
        assert "retry" in code
        assert "safe_json_loads" in code
    
    def test_generate_test_py(self):
        """Test test suite generation."""
        spec = {}
        code = self.generator.generate_test_py("Test Agent", spec)
        
        assert "pytest" in code
        assert "TestAgentSkill" in code
        assert "test_execute_success" in code
    
    def test_generate_code(self):
        """Test complete code package generation."""
        spec = {
            "description": "Test agent",
            "skills": ["skill1"],
            "core_tools": ["tool1"]
        }
        
        code = self.generator.generate_code("Test Agent", spec)
        
        assert isinstance(code, CodePackage)
        assert code.skill_py is not None
        assert code.skill_md is not None
        assert code.config_py is not None
        assert code.utils_py is not None
        assert code.test_py is not None
        assert code.requirements_txt is not None
        assert code.readme_md is not None
    
    def test_write_code(self):
        """Test writing code to files."""
        spec = {
            "description": "Test agent",
            "skills": ["skill1"],
            "core_tools": ["tool1"]
        }
        
        code = self.generator.generate_code("Test Agent", spec)
        files = self.generator.write_code("Test Agent", code)
        
        assert "skill.py" in files
        assert "test.py" in files
        assert "requirements.txt" in files
        assert "README.md" in files
        
        # Check files exist
        for path in files.values():
            assert path.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
