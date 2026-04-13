#!/usr/bin/env python3
"""
Test suite for domain_researcher.py
"""

import pytest
import json
import tempfile
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from domain_researcher import DomainResearcher, DomainScore, DomainAnalysis


class TestDomainScore:
    """Tests for DomainScore dataclass."""
    
    def test_total_calculation(self):
        """Test that total is calculated correctly."""
        score = DomainScore(pain=20, data=15, tools=20, value=15)
        assert score.total == 70
    
    def test_max_score(self):
        """Test maximum possible score."""
        score = DomainScore(pain=25, data=25, tools=25, value=25)
        assert score.total == 100


class TestDomainResearcher:
    """Tests for DomainResearcher class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.researcher = DomainResearcher(output_dir=self.temp_dir)
    
    def test_score_domain(self):
        """Test domain scoring."""
        score = self.researcher.score_domain(
            pain_points=["pain1", "pain2", "pain3"],
            data_sources=["source1", "source2"],
            required_tools=["tool1"],
            target_users="enterprise businesses"
        )
        
        assert isinstance(score, DomainScore)
        assert score.pain > 0
        assert score.data > 0
        assert score.tools > 0
        assert score.value > 0
        assert score.total > 0
    
    def test_analyze_domain(self):
        """Test complete domain analysis."""
        analysis = self.researcher.analyze_domain(
            name="Test Agent",
            description="A test agent",
            category="data_processing",
            pain_points=["manual work"],
            data_sources=["API"],
            required_tools=["requests"],
            target_users="developers"
        )
        
        assert isinstance(analysis, DomainAnalysis)
        assert analysis.name == "Test Agent"
        assert analysis.category == "data_processing"
        assert analysis.score.total > 0
        assert analysis.id is not None
    
    def test_analyze_domain_invalid_category(self):
        """Test that invalid category raises error."""
        with pytest.raises(ValueError):
            self.researcher.analyze_domain(
                name="Test",
                description="Test",
                category="invalid_category",
                pain_points=["pain"],
                data_sources=["data"],
                required_tools=["tool"],
                target_users="users"
            )
    
    def test_save_and_load_analysis(self):
        """Test saving and loading domain analysis."""
        analysis = self.researcher.analyze_domain(
            name="Test Agent",
            description="A test agent",
            category="research",
            pain_points=["pain"],
            data_sources=["data"],
            required_tools=["tool"],
            target_users="users"
        )
        
        # Save
        self.researcher.save_analysis(analysis)
        
        # Load
        top = self.researcher.get_top_opportunities(min_score=0)
        assert len(top) >= 1
        assert top[0]["name"] == "Test Agent"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
