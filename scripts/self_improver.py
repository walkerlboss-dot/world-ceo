#!/usr/bin/env python3
"""
Self-Improver - Analyzes failures and updates patterns for continuous improvement.

This module:
- Analyzes agent logs for error patterns
- Updates code templates based on learnings
- Tracks performance metrics
- Evolves domain research methodologies
"""

import json
import logging
import os
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("WORLD_CEO_LOG_LEVEL", "INFO")),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("self_improver")


@dataclass
class ErrorPattern:
    """Identified error pattern."""
    pattern: str
    count: int
    agents_affected: List[str]
    first_seen: str
    last_seen: str
    suggested_fix: str


@dataclass
class Improvement:
    """Suggested improvement."""
    category: str  # code, docs, process, research
    description: str
    priority: int  # 1-5
    affected_files: List[str]
    rationale: str


@dataclass
class PerformanceMetrics:
    """Performance metrics for an agent."""
    agent_id: str
    total_tasks: int
    successful_tasks: int
    failed_tasks: int
    avg_response_time: float
    error_rate: float
    timestamp: str


class SelfImprover:
    """Analyzes performance and suggests improvements."""
    
    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = Path(output_dir or os.getenv("WORLD_CEO_OUTPUT_DIR", "./output"))
        self.learnings_dir = self.output_dir / ".learnings"
        self.learnings_dir.mkdir(parents=True, exist_ok=True)
        
        # Learning files
        self.errors_file = self.learnings_dir / "errors.md"
        self.successes_file = self.learnings_dir / "successes.md"
        self.improvements_file = self.learnings_dir / "improvements.md"
        self.metrics_file = self.learnings_dir / "metrics.json"
        
        # Initialize learning files if they don't exist
        self._init_learning_files()
    
    def _init_learning_files(self):
        """Initialize learning files with headers."""
        if not self.errors_file.exists():
            self.errors_file.write_text("# Error Patterns\n\n")
        
        if not self.successes_file.exists():
            self.successes_file.write_text("# Success Patterns\n\n")
        
        if not self.improvements_file.exists():
            self.improvements_file.write_text("# Improvements Applied\n\n")
    
    def analyze_logs(self, log_dir: Path, days: int = 7) -> List[ErrorPattern]:
        """
        Analyze agent logs for error patterns.
        
        Args:
            log_dir: Directory containing log files
            days: Number of days to analyze
            
        Returns:
            List of identified error patterns
        """
        logger.info(f"Analyzing logs from {log_dir} for last {days} days")
        
        error_patterns = defaultdict(lambda: {
            "count": 0,
            "agents": set(),
            "first_seen": None,
            "last_seen": None
        })
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Scan log files
        for log_file in log_dir.glob("**/*.log"):
            try:
                content = log_file.read_text()
                agent_name = log_file.stem
                
                # Find error lines
                error_lines = re.findall(r'ERROR.*', content)
                
                for line in error_lines:
                    # Extract error pattern (simplified)
                    pattern = self._extract_error_pattern(line)
                    
                    if pattern:
                        error_patterns[pattern]["count"] += 1
                        error_patterns[pattern]["agents"].add(agent_name)
                        
                        # Update timestamps
                        timestamp_match = re.search(r'(\d{{4}}-\d{{2}}-\d{{2}})', line)
                        if timestamp_match:
                            ts = timestamp_match.group(1)
                            if error_patterns[pattern]["first_seen"] is None:
                                error_patterns[pattern]["first_seen"] = ts
                            error_patterns[pattern]["last_seen"] = ts
                            
            except Exception as e:
                logger.warning(f"Failed to analyze {log_file}: {e}")
        
        # Convert to ErrorPattern objects
        results = []
        for pattern, data in error_patterns.items():
            if data["count"] >= 2:  # Only patterns occurring multiple times
                results.append(ErrorPattern(
                    pattern=pattern,
                    count=data["count"],
                    agents_affected=list(data["agents"]),
                    first_seen=data["first_seen"] or datetime.now().isoformat(),
                    last_seen=data["last_seen"] or datetime.now().isoformat(),
                    suggested_fix=self._suggest_fix(pattern)
                ))
        
        # Sort by count
        results.sort(key=lambda x: x.count, reverse=True)
        
        logger.info(f"Found {len(results)} error patterns")
        return results
    
    def _extract_error_pattern(self, error_line: str) -> Optional[str]:
        """Extract a generalized error pattern from an error line."""
        # Remove timestamps and specific values
        pattern = re.sub(r'\d{{4}}-\d{{2}}-\d{{2}} \d{{2}}:\d{{2}}:\d{{2}}', '', error_line)
        pattern = re.sub(r'\b[0-9a-f]{{8}}-[0-9a-f]{{4}}-[0-9a-f]{{4}}-[0-9a-f]{{4}}-[0-9a-f]{{12}}\b', '<UUID>', pattern)
        pattern = re.sub(r'\b\d+\b', '<NUM>', pattern)
        pattern = re.sub(r"'[^']*'", "'<STR>'", pattern)
        pattern = re.sub(r'"[^"]*"', '"<STR>"', pattern)
        
        # Normalize whitespace
        pattern = ' '.join(pattern.split())
        
        return pattern.strip() if pattern.strip() else None
    
    def _suggest_fix(self, pattern: str) -> str:
        """Suggest a fix for an error pattern."""
        # Common error patterns and their fixes
        fixes = {
            "ConnectionError": "Add retry logic with exponential backoff",
            "TimeoutError": "Increase timeout or implement async processing",
            "KeyError": "Add input validation and default values",
            "ValueError": "Add type checking and conversion",
            "FileNotFoundError": "Check file existence before operations",
            "PermissionError": "Check permissions or use temporary files",
            "RateLimit": "Implement rate limiting and request queuing",
            "JSONDecodeError": "Add JSON validation and error handling"
        }
        
        for error_type, fix in fixes.items():
            if error_type.lower() in pattern.lower():
                return fix
        
        return "Review and add defensive error handling"
    
    def log_error_pattern(self, pattern: ErrorPattern):
        """Log an error pattern to the learnings file."""
        entry = f"""
## {pattern.pattern[:80]}...

- **Count**: {pattern.count}
- **Agents**: {', '.join(pattern.agents_affected)}
- **First Seen**: {pattern.first_seen}
- **Last Seen**: {pattern.last_seen}
- **Suggested Fix**: {pattern.suggested_fix}
- **Logged**: {datetime.now().isoformat()}

"""
        
        with open(self.errors_file, 'a') as f:
            f.write(entry)
        
        logger.info(f"Logged error pattern: {pattern.pattern[:50]}...")
    
    def log_success_pattern(self, agent_name: str, technique: str, context: str):
        """Log a successful technique or pattern."""
        entry = f"""
## {technique}

- **Agent**: {agent_name}
- **Context**: {context}
- **Logged**: {datetime.now().isoformat()}

"""
        
        with open(self.successes_file, 'a') as f:
            f.write(entry)
        
        logger.info(f"Logged success pattern: {technique}")
    
    def generate_improvements(self, error_patterns: List[ErrorPattern]) -> List[Improvement]:
        """
        Generate improvement suggestions from error patterns.
        
        Args:
            error_patterns: List of error patterns
            
        Returns:
            List of improvement suggestions
        """
        improvements = []
        
        for pattern in error_patterns:
            if pattern.count >= 5:
                # High-frequency error warrants template update
                improvements.append(Improvement(
                    category="code",
                    description=f"Update error handling for: {pattern.pattern[:60]}...",
                    priority=5,
                    affected_files=["templates/error_handler.py"],
                    rationale=f"Pattern occurred {pattern.count} times across {len(pattern.agents_affected)} agents"
                ))
            elif pattern.count >= 3:
                # Medium frequency - document and patch
                improvements.append(Improvement(
                    category="docs",
                    description=f"Document handling for: {pattern.pattern[:60]}...",
                    priority=3,
                    affected_files=["docs/error_handling.md"],
                    rationale=f"Recurring pattern affecting {len(pattern.agents_affected)} agents"
                ))
        
        # Sort by priority
        improvements.sort(key=lambda x: x.priority, reverse=True)
        
        return improvements
    
    def apply_improvement(self, improvement: Improvement) -> bool:
        """
        Apply an improvement to the codebase.
        
        Args:
            improvement: Improvement to apply
            
        Returns:
            True if successful
        """
        logger.info(f"Applying improvement: {improvement.description}")
        
        # Log the improvement
        entry = f"""
## {improvement.description}

- **Category**: {improvement.category}
- **Priority**: {improvement.priority}/5
- **Files**: {', '.join(improvement.affected_files)}
- **Rationale**: {improvement.rationale}
- **Applied**: {datetime.now().isoformat()}

"""
        
        with open(self.improvements_file, 'a') as f:
            f.write(entry)
        
        # TODO: Actually apply code changes
        # For now, just log that it should be done
        
        return True
    
    def calculate_performance_metrics(self, agent_id: str, logs: List[dict]) -> PerformanceMetrics:
        """
        Calculate performance metrics from logs.
        
        Args:
            agent_id: Agent identifier
            logs: List of log entries
            
        Returns:
            PerformanceMetrics
        """
        total = len(logs)
        successful = sum(1 for log in logs if log.get("success", False))
        failed = total - successful
        
        response_times = [log.get("response_time", 0) for log in logs if "response_time" in log]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        error_rate = (failed / total * 100) if total > 0 else 0
        
        return PerformanceMetrics(
            agent_id=agent_id,
            total_tasks=total,
            successful_tasks=successful,
            failed_tasks=failed,
            avg_response_time=avg_response_time,
            error_rate=error_rate,
            timestamp=datetime.now().isoformat()
        )
    
    def save_metrics(self, metrics: PerformanceMetrics):
        """Save performance metrics."""
        all_metrics = []
        
        if self.metrics_file.exists():
            with open(self.metrics_file, 'r') as f:
                all_metrics = json.load(f)
        
        all_metrics.append(asdict(metrics))
        
        with open(self.metrics_file, 'w') as f:
            json.dump(all_metrics, f, indent=2)
        
        logger.info(f"Saved metrics for {metrics.agent_id}")
    
    def generate_weekly_report(self) -> str:
        """Generate a weekly improvement report."""
        lines = ["# Weekly Improvement Report", f"\nGenerated: {datetime.now().isoformat()}", ""]
        
        # Error patterns
        if self.errors_file.exists():
            content = self.errors_file.read_text()
            error_count = content.count("## ")
            lines.append(f"## Error Patterns Logged: {error_count}")
        
        # Success patterns
        if self.successes_file.exists():
            content = self.successes_file.read_text()
            success_count = content.count("## ")
            lines.append(f"## Success Patterns Logged: {success_count}")
        
        # Improvements applied
        if self.improvements_file.exists():
            content = self.improvements_file.read_text()
            improvement_count = content.count("## ")
            lines.append(f"## Improvements Applied: {improvement_count}")
        
        # Performance metrics
        if self.metrics_file.exists():
            with open(self.metrics_file, 'r') as f:
                metrics = json.load(f)
            
            if metrics:
                recent = metrics[-10:]  # Last 10 entries
                avg_error_rate = sum(m["error_rate"] for m in recent) / len(recent)
                lines.append(f"\n## Recent Performance")
                lines.append(f"Average Error Rate: {avg_error_rate:.2f}%")
        
        return "\n".join(lines)
    
    def update_code_templates(self, error_patterns: List[ErrorPattern]):
        """
        Update code generation templates based on error patterns.
        
        Args:
            error_patterns: List of error patterns to address
        """
        templates_dir = self.output_dir / "templates"
        templates_dir.mkdir(exist_ok=True)
        
        # Check for common patterns that need template updates
        connection_errors = [p for p in error_patterns if "connection" in p.pattern.lower()]
        timeout_errors = [p for p in error_patterns if "timeout" in p.pattern.lower()]
        
        if connection_errors:
            logger.info("Updating templates for connection error handling")
            # TODO: Update retry logic in templates
        
        if timeout_errors:
            logger.info("Updating templates for timeout handling")
            # TODO: Update timeout configuration in templates
    
    def run_improvement_cycle(self, log_dir: Optional[Path] = None):
        """
        Run a complete improvement cycle.
        
        Args:
            log_dir: Directory containing agent logs
        """
        logger.info("Starting improvement cycle")
        
        # Analyze logs if provided
        if log_dir and log_dir.exists():
            error_patterns = self.analyze_logs(log_dir)
            
            # Log patterns
            for pattern in error_patterns:
                self.log_error_pattern(pattern)
            
            # Generate improvements
            improvements = self.generate_improvements(error_patterns)
            
            # Apply high-priority improvements
            for imp in improvements:
                if imp.priority >= 4:
                    self.apply_improvement(imp)
            
            # Update templates
            self.update_code_templates(error_patterns)
        
        # Generate report
        report = self.generate_weekly_report()
        report_path = self.learnings_dir / f"report_{datetime.now().strftime('%Y%m%d')}.md"
        report_path.write_text(report)
        
        logger.info(f"Improvement cycle complete. Report: {report_path}")


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Self-improvement analysis")
    parser.add_argument("--log-dir", "-l", help="Log directory to analyze")
    parser.add_argument("--report", "-r", action="store_true", help="Generate report")
    parser.add_argument("--cycle", "-c", action="store_true", help="Run full improvement cycle")
    
    args = parser.parse_args()
    
    improver = SelfImprover()
    
    if args.cycle:
        log_dir = Path(args.log_dir) if args.log_dir else None
        improver.run_improvement_cycle(log_dir)
    elif args.report:
        report = improver.generate_weekly_report()
        print(report)
    else:
        print("Use --cycle to run improvement cycle or --report to generate report")


if __name__ == "__main__":
    main()
