#!/usr/bin/env python3
"""
Test suite for self_improver.py
"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from self_improver import SelfImprover, ErrorPattern, Improvement, PerformanceMetrics


class TestErrorPattern:
    """Tests for ErrorPattern dataclass."""
    
    def test_creation(self):
        """Test error pattern creation."""
        pattern = ErrorPattern(
            pattern="ConnectionError to <URL>",
            count=5,
            agents_affected=["agent1", "agent2"],
            first_seen="2026-04-01",
            last_seen="2026-04-10",
            suggested_fix="Add retry logic"
        )
        
        assert pattern.count == 5
        assert len(pattern.agents_affected) == 2


class TestImprovement:
    """Tests for Improvement dataclass."""
    
    def test_creation(self):
        """Test improvement creation."""
        improvement = Improvement(
            category="code",
            description="Add error handling",
            priority=5,
            affected_files=["file.py"],
            rationale="Common failure"
        )
        
        assert improvement.category == "code"
        assert improvement.priority == 5


class TestPerformanceMetrics:
    """Tests for PerformanceMetrics dataclass."""
    
    def test_metrics_calculation(self):
        """Test metrics structure."""
        metrics = PerformanceMetrics(
            agent_id="test-agent",
            total_tasks=100,
            successful_tasks=95,
            failed_tasks=5,
            avg_response_time=1.5,
            error_rate=5.0,
            timestamp=datetime.now().isoformat()
        )
        
        assert metrics.error_rate == 5.0
        assert metrics.total_tasks == 100


class TestSelfImprover:
    """Tests for SelfImprover class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.improver = SelfImprover(output_dir=self.temp_dir)
    
    def test_init_learning_files(self):
        """Test learning files initialization."""
        assert self.improver.errors_file.exists()
        assert self.improver.successes_file.exists()
        assert self.improver.improvements_file.exists()
    
    def test_extract_error_pattern(self):
        """Test error pattern extraction."""
        line = "2026-04-13 10:00:00 ERROR Connection to api.example.com failed"
        pattern = self.improver._extract_error_pattern(line)
        
        assert pattern is not None
        assert "ERROR" in pattern
        assert "Connection" in pattern
    
    def test_suggest_fix(self):
        """Test fix suggestion."""
        connection_fix = self.improver._suggest_fix("ConnectionError")
        assert "retry" in connection_fix.lower()
        
        timeout_fix = self.improver._suggest_fix("TimeoutError")
        assert "timeout" in timeout_fix.lower()
        
        unknown_fix = self.improver._suggest_fix("UnknownError")
        assert "defensive" in unknown_fix.lower()
    
    def test_generate_improvements(self):
        """Test improvement generation."""
        patterns = [
            ErrorPattern(
                pattern="ConnectionError",
                count=10,
                agents_affected=["agent1"],
                first_seen="2026-04-01",
                last_seen="2026-04-10",
                suggested_fix="Add retry"
            )
        ]
        
        improvements = self.improver.generate_improvements(patterns)
        
        assert len(improvements) > 0
        assert improvements[0].priority == 5  # High priority for frequent errors
    
    def test_calculate_performance_metrics(self):
        """Test performance metrics calculation."""
        logs = [
            {"success": True, "response_time": 1.0},
            {"success": True, "response_time": 2.0},
            {"success": False, "response_time": 0.5}
        ]
        
        metrics = self.improver.calculate_performance_metrics("test-agent", logs)
        
        assert metrics.total_tasks == 3
        assert metrics.successful_tasks == 2
        assert metrics.failed_tasks == 1
        assert metrics.error_rate == pytest.approx(33.33, rel=0.1)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
