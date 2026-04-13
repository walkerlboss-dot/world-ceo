#!/usr/bin/env python3
"""
Agent Generator - Master orchestrator for autonomous agent creation.

This module coordinates the entire agent creation pipeline:
1. Domain analysis
2. Specification generation
3. Code generation
4. Deployment
"""

import json
import logging
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Import sibling modules
sys.path.insert(0, str(Path(__file__).parent))

try:
    from domain_researcher import DomainResearcher, DomainAnalysis, DomainScore
    from spec_writer import SpecWriter, AgentSpec
    from code_generator import CodeGenerator, CodePackage
    from deployment_manager import DeploymentManager, DeploymentResult
    from self_improver import SelfImprover
except ImportError as e:
    # Fallback for when modules aren't in path
    logging.warning(f"Could not import modules: {e}")
    DomainResearcher = None
    SpecWriter = None
    CodeGenerator = None
    DeploymentManager = None
    SelfImprover = None

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("WORLD_CEO_LOG_LEVEL", "INFO")),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("agent_generator")


@dataclass
class GenerationResult:
    """Result of agent generation."""
    success: bool
    agent_name: str
    agent_dir: Optional[Path] = None
    spec_files: Optional[Dict[str, Path]] = None
    code_files: Optional[Dict[str, Path]] = None
    deployment: Optional[DeploymentResult] = None
    error: Optional[str] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        return {
            "success": self.success,
            "agent_name": self.agent_name,
            "agent_dir": str(self.agent_dir) if self.agent_dir else None,
            "spec_files": {k: str(v) for k, v in self.spec_files.items()} if self.spec_files else None,
            "code_files": {k: str(v) for k, v in self.code_files.items()} if self.code_files else None,
            "deployment": self.deployment.to_dict() if self.deployment else None,
            "error": self.error,
            "timestamp": self.timestamp
        }


class AgentGenerator:
    """Master orchestrator for agent creation."""
    
    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = Path(output_dir or os.getenv("WORLD_CEO_OUTPUT_DIR", "./output"))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.domain_researcher = DomainResearcher(output_dir=output_dir) if DomainResearcher else None
        self.spec_writer = SpecWriter(output_dir=output_dir) if SpecWriter else None
        self.code_generator = CodeGenerator(output_dir=output_dir) if CodeGenerator else None
        self.deployment_manager = DeploymentManager(output_dir=output_dir) if DeploymentManager else None
        self.self_improver = SelfImprover(output_dir=output_dir) if SelfImprover else None
    
    def generate_from_domain(
        self,
        name: str,
        description: str,
        category: str,
        pain_points: List[str],
        data_sources: List[str],
        required_tools: List[str],
        target_users: str,
        competitors: Optional[List[str]] = None,
        source_urls: Optional[List[str]] = None,
        deploy: bool = False
    ) -> GenerationResult:
        """
        Generate a complete agent from domain description.
        
        Args:
            name: Agent name
            description: Brief description
            category: Agent category
            pain_points: List of pain points
            data_sources: Available data sources
            required_tools: Required tools/APIs
            target_users: Target user description
            competitors: Existing solutions
            source_urls: Research source URLs
            deploy: Whether to deploy after generation
            
        Returns:
            GenerationResult
        """
        logger.info(f"Starting agent generation: {name}")
        
        try:
            # Step 1: Domain Analysis
            logger.info("Step 1: Analyzing domain...")
            if self.domain_researcher:
                domain_analysis = self.domain_researcher.analyze_domain(
                    name=name,
                    description=description,
                    category=category,
                    pain_points=pain_points,
                    data_sources=data_sources,
                    required_tools=required_tools,
                    target_users=target_users,
                    competitors=competitors or [],
                    source_urls=source_urls or []
                )
                self.domain_researcher.save_analysis(domain_analysis)
                domain_dict = domain_analysis.to_dict()
            else:
                # Fallback: create minimal domain dict
                domain_dict = {
                    "name": name,
                    "description": description,
                    "category": category,
                    "pain_points": pain_points,
                    "data_sources": data_sources,
                    "required_tools": required_tools,
                    "target_users": target_users
                }
            
            # Step 2: Specification Generation
            logger.info("Step 2: Generating specifications...")
            if self.spec_writer:
                spec = self.spec_writer.create_from_domain(domain_dict)
                spec_files = self.spec_writer.write_spec(spec)
            else:
                spec = None
                spec_files = {}
            
            # Step 3: Code Generation
            logger.info("Step 3: Generating code...")
            if self.code_generator:
                spec_data = {
                    "name": name,
                    "description": description,
                    "category": category,
                    "skills": [f"{name.lower().replace(' ', '_')}_skill"],
                    "core_tools": required_tools
                }
                code = self.code_generator.generate_code(name, spec_data)
                code_files = self.code_generator.write_code(name, code)
            else:
                code = None
                code_files = {}
            
            # Step 4: Deployment (optional)
            deployment_result = None
            if deploy and self.deployment_manager:
                logger.info("Step 4: Deploying agent...")
                spec_for_deploy = spec_data or domain_dict
                deployment_result = self.deployment_manager.deploy(
                    name,
                    spec_for_deploy,
                    push_to_github=True,
                    configure_openclaw=True
                )
            
            agent_dir = self.output_dir / name.lower().replace(" ", "_")
            
            logger.info(f"Agent generation complete: {name}")
            
            return GenerationResult(
                success=True,
                agent_name=name,
                agent_dir=agent_dir,
                spec_files=spec_files,
                code_files=code_files,
                deployment=deployment_result
            )
            
        except Exception as e:
            logger.error(f"Agent generation failed: {e}")
            return GenerationResult(
                success=False,
                agent_name=name,
                error=str(e)
            )
    
    def generate_from_spec_file(self, spec_path: Path, deploy: bool = False) -> GenerationResult:
        """
        Generate agent from a specification JSON file.
        
        Args:
            spec_path: Path to spec JSON file
            deploy: Whether to deploy
            
        Returns:
            GenerationResult
        """
        logger.info(f"Loading spec from: {spec_path}")
        
        with open(spec_path, 'r') as f:
            spec_data = json.load(f)
        
        return self.generate_from_domain(
            name=spec_data["name"],
            description=spec_data["description"],
            category=spec_data.get("category", "general"),
            pain_points=spec_data.get("pain_points", []),
            data_sources=spec_data.get("data_sources", []),
            required_tools=spec_data.get("required_tools", []),
            target_users=spec_data.get("target_users", "general"),
            competitors=spec_data.get("competitors"),
            source_urls=spec_data.get("source_urls"),
            deploy=deploy
        )
    
    def batch_generate(
        self,
        domains: List[Dict],
        deploy: bool = False
    ) -> List[GenerationResult]:
        """
        Generate multiple agents in batch.
        
        Args:
            domains: List of domain dictionaries
            deploy: Whether to deploy each agent
            
        Returns:
            List of GenerationResults
        """
        logger.info(f"Starting batch generation of {len(domains)} agents")
        
        results = []
        for domain in domains:
            result = self.generate_from_domain(
                name=domain["name"],
                description=domain["description"],
                category=domain.get("category", "general"),
                pain_points=domain.get("pain_points", []),
                data_sources=domain.get("data_sources", []),
                required_tools=domain.get("required_tools", []),
                target_users=domain.get("target_users", "general"),
                competitors=domain.get("competitors"),
                source_urls=domain.get("source_urls"),
                deploy=deploy
            )
            results.append(result)
        
        # Summary
        successful = sum(1 for r in results if r.success)
        logger.info(f"Batch complete: {successful}/{len(results)} agents generated successfully")
        
        return results
    
    def run_self_improvement(self):
        """Run self-improvement cycle."""
        if self.self_improver:
            logger.info("Running self-improvement cycle")
            self.self_improver.run_improvement_cycle()
        else:
            logger.warning("Self-improver not available")


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="WORLD CEO - Agent Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate from domain description
  python agent_generator.py --name "Data Cleaner" --description "Cleans messy data" \\
    --category data_processing --pain-points "manual cleaning" --data-sources "CSV files" \\
    --tools "pandas" --target-users "data analysts"

  # Generate from spec file
  python agent_generator.py --spec-file domain.json

  # Generate and deploy
  python agent_generator.py --spec-file domain.json --deploy
        """
    )
    
    parser.add_argument("--name", "-n", help="Agent name")
    parser.add_argument("--description", "-d", help="Agent description")
    parser.add_argument("--category", "-c", default="general", 
                       choices=["data_processing", "communication", "research", "integration", "creative"],
                       help="Agent category")
    parser.add_argument("--pain-points", nargs="+", help="List of pain points")
    parser.add_argument("--data-sources", nargs="+", help="List of data sources")
    parser.add_argument("--tools", nargs="+", help="List of required tools")
    parser.add_argument("--target-users", default="general", help="Target user description")
    parser.add_argument("--competitors", nargs="+", help="List of competitors")
    parser.add_argument("--source-urls", nargs="+", help="List of source URLs")
    parser.add_argument("--spec-file", "-s", type=Path, help="Path to spec JSON file")
    parser.add_argument("--output", "-o", help="Output directory")
    parser.add_argument("--deploy", action="store_true", help="Deploy after generation")
    parser.add_argument("--improve", action="store_true", help="Run self-improvement cycle")
    
    args = parser.parse_args()
    
    # Initialize generator
    generator = AgentGenerator(output_dir=args.output)
    
    # Run self-improvement if requested
    if args.improve:
        generator.run_self_improvement()
        return
    
    # Generate agent
    if args.spec_file:
        result = generator.generate_from_spec_file(args.spec_file, deploy=args.deploy)
    elif args.name and args.description:
        result = generator.generate_from_domain(
            name=args.name,
            description=args.description,
            category=args.category,
            pain_points=args.pain_points or [],
            data_sources=args.data_sources or [],
            required_tools=args.tools or [],
            target_users=args.target_users,
            competitors=args.competitors,
            source_urls=args.source_urls,
            deploy=args.deploy
        )
    else:
        parser.print_help()
        sys.exit(1)
    
    # Output result
    print(json.dumps(result.to_dict(), indent=2))
    
    if not result.success:
        sys.exit(1)


if __name__ == "__main__":
    main()
