#!/usr/bin/env python3
"""
Domain Researcher - Identifies agent opportunities through continuous research.

This module continuously scans for emerging domains, workflow inefficiencies,
and automation opportunities suitable for agent creation.
"""

import json
import logging
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Optional
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("WORLD_CEO_LOG_LEVEL", "INFO")),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("domain_researcher")


@dataclass
class DomainScore:
    """Scoring breakdown for a domain opportunity."""
    pain: int  # 0-25: How acute is the problem?
    data: int  # 0-25: Is quality data available?
    tools: int  # 0-25: Can we build effective tools?
    value: int  # 0-25: What's the potential impact?
    
    @property
    def total(self) -> int:
        return self.pain + self.data + self.tools + self.value


@dataclass
class DomainAnalysis:
    """Complete analysis of a domain opportunity."""
    id: str
    name: str
    description: str
    category: str  # data_processing, communication, research, integration, creative
    score: DomainScore
    pain_points: List[str]
    data_sources: List[str]
    required_tools: List[str]
    target_users: str
    competitors: List[str]
    research_date: str
    source_urls: List[str]
    
    def to_dict(self) -> dict:
        score_dict = asdict(self.score)
        score_dict["total"] = self.score.total
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "score": score_dict,
            "pain_points": self.pain_points,
            "data_sources": self.data_sources,
            "required_tools": self.required_tools,
            "target_users": self.target_users,
            "competitors": self.competitors,
            "research_date": self.research_date,
            "source_urls": self.source_urls
        }


class DomainResearcher:
    """Researches and scores domain opportunities for agent creation."""
    
    CATEGORIES = [
        "data_processing",
        "communication", 
        "research",
        "integration",
        "creative"
    ]
    
    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = Path(output_dir or os.getenv("WORLD_CEO_OUTPUT_DIR", "./output"))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.domains_file = self.output_dir / "domains.json"
        self.research_log = self.output_dir / "research_log.jsonl"
        
    def _generate_id(self, name: str) -> str:
        """Generate a unique ID for a domain."""
        timestamp = datetime.now().strftime("%Y%m%d")
        slug = name.lower().replace(" ", "-").replace("_", "-")[:30]
        return f"{timestamp}-{slug}"
    
    def score_domain(
        self,
        pain_points: List[str],
        data_sources: List[str],
        required_tools: List[str],
        target_users: str
    ) -> DomainScore:
        """
        Score a domain opportunity based on key factors.
        
        Args:
            pain_points: List of identified pain points
            data_sources: Available data sources
            required_tools: Tools needed for solution
            target_users: Description of target user base
            
        Returns:
            DomainScore with breakdown
        """
        # Pain score: More severe/more pain points = higher score
        pain_score = min(25, len(pain_points) * 5 + 10)
        
        # Data score: More reliable sources = higher score
        data_score = min(25, len(data_sources) * 8 + 5)
        
        # Tools score: Feasibility based on tool availability
        tool_score = min(25, len(required_tools) * 6 + 7)
        
        # Value score: Based on target user base size/impact
        value_indicators = {
            "enterprise": 25,
            "business": 20,
            "developer": 18,
            "professional": 15,
            "consumer": 12,
            "niche": 8
        }
        value_score = 10
        for indicator, score in value_indicators.items():
            if indicator in target_users.lower():
                value_score = score
                break
        
        return DomainScore(
            pain=pain_score,
            data=data_score,
            tools=tool_score,
            value=value_score
        )
    
    def analyze_domain(
        self,
        name: str,
        description: str,
        category: str,
        pain_points: List[str],
        data_sources: List[str],
        required_tools: List[str],
        target_users: str,
        competitors: Optional[List[str]] = None,
        source_urls: Optional[List[str]] = None
    ) -> DomainAnalysis:
        """
        Perform complete analysis of a domain opportunity.
        
        Args:
            name: Domain name
            description: Brief description
            category: One of CATEGORIES
            pain_points: List of pain points
            data_sources: Available data sources
            required_tools: Required tools/APIs
            target_users: Target user description
            competitors: Existing solutions
            source_urls: Research source URLs
            
        Returns:
            Complete DomainAnalysis
        """
        if category not in self.CATEGORIES:
            raise ValueError(f"Invalid category. Must be one of: {self.CATEGORIES}")
        
        score = self.score_domain(
            pain_points, data_sources, required_tools, target_users
        )
        
        analysis = DomainAnalysis(
            id=self._generate_id(name),
            name=name,
            description=description,
            category=category,
            score=score,
            pain_points=pain_points,
            data_sources=data_sources,
            required_tools=required_tools,
            target_users=target_users,
            competitors=competitors or [],
            research_date=datetime.now().isoformat(),
            source_urls=source_urls or []
        )
        
        logger.info(f"Analyzed domain '{name}' with score {score.total}/100")
        return analysis
    
    def save_analysis(self, analysis: DomainAnalysis) -> None:
        """Save domain analysis to persistent storage."""
        # Load existing domains
        domains = []
        if self.domains_file.exists():
            with open(self.domains_file, 'r') as f:
                domains = json.load(f)
        
        # Update or append
        existing = [d for d in domains if d["id"] == analysis.id]
        if existing:
            domains = [d for d in domains if d["id"] != analysis.id]
        domains.append(analysis.to_dict())
        
        # Save
        with open(self.domains_file, 'w') as f:
            json.dump(domains, f, indent=2)
        
        # Append to log
        with open(self.research_log, 'a') as f:
            f.write(json.dumps(analysis.to_dict()) + "\n")
        
        logger.info(f"Saved analysis for domain '{analysis.name}'")
    
    def get_top_opportunities(self, min_score: int = 60, limit: int = 10) -> List[dict]:
        """
        Get top-scoring domain opportunities.
        
        Args:
            min_score: Minimum total score to include
            limit: Maximum number to return
            
        Returns:
            List of domain analyses sorted by score
        """
        if not self.domains_file.exists():
            return []
        
        with open(self.domains_file, 'r') as f:
            domains = json.load(f)
        
        # Filter and sort
        qualified = [d for d in domains if d["score"]["total"] >= min_score]
        qualified.sort(key=lambda x: x["score"]["total"], reverse=True)
        
        return qualified[:limit]
    
    def research_from_query(self, query: str) -> Optional[DomainAnalysis]:
        """
        Research a domain based on a user query or topic.
        This is a placeholder for integration with search tools.
        
        Args:
            query: Research query
            
        Returns:
            DomainAnalysis if successful
        """
        logger.info(f"Starting research for query: {query}")
        
        # TODO: Integrate with web_search and browser tools
        # For now, return None to indicate manual analysis needed
        
        logger.warning("Automated research not yet implemented. Use analyze_domain() for manual input.")
        return None
    
    def generate_research_report(self) -> str:
        """Generate a markdown report of all researched domains."""
        if not self.domains_file.exists():
            return "# Domain Research Report\n\nNo domains researched yet."
        
        with open(self.domains_file, 'r') as f:
            domains = json.load(f)
        
        # Sort by score
        domains.sort(key=lambda x: x["score"]["total"], reverse=True)
        
        lines = ["# Domain Research Report", f"\nGenerated: {datetime.now().isoformat()}", "\n## Summary\n"]
        lines.append(f"Total domains researched: {len(domains)}")
        
        high_priority = [d for d in domains if d["score"]["total"] >= 80]
        viable = [d for d in domains if 60 <= d["score"]["total"] < 80]
        
        lines.append(f"High priority (80+): {len(high_priority)}")
        lines.append(f"Viable (60-79): {len(viable)}")
        
        lines.append("\n## High Priority Opportunities\n")
        for d in high_priority[:5]:
            lines.append(f"### {d['name']} ({d['score']['total']}/100)")
            lines.append(f"**Category:** {d['category']}")
            lines.append(f"**Description:** {d['description']}")
            lines.append(f"**Target Users:** {d['target_users']}")
            lines.append(f"**Pain Points:** {', '.join(d['pain_points'][:3])}")
            lines.append("")
        
        return "\n".join(lines)


def main():
    """CLI entry point for domain research."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Research domain opportunities")
    parser.add_argument("--output", "-o", help="Output directory")
    parser.add_argument("--report", "-r", action="store_true", help="Generate report")
    parser.add_argument("--top", "-t", type=int, default=10, help="Show top N opportunities")
    
    args = parser.parse_args()
    
    researcher = DomainResearcher(output_dir=args.output)
    
    if args.report:
        report = researcher.generate_research_report()
        print(report)
    else:
        opportunities = researcher.get_top_opportunities(limit=args.top)
        print(f"\nTop {len(opportunities)} Opportunities:\n")
        for opp in opportunities:
            print(f"  {opp['name']}: {opp['score']['total']}/100 ({opp['category']})")


if __name__ == "__main__":
    main()
