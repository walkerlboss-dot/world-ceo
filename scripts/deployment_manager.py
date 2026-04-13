#!/usr/bin/env python3
"""
Deployment Manager - Handles GitHub repo creation and OpenClaw integration.

This module manages:
- GitHub repository creation and updates
- Code pushing and versioning
- OpenClaw gateway configuration
- Health check setup
"""

import json
import logging
import os
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("WORLD_CEO_LOG_LEVEL", "INFO")),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("deployment_manager")


@dataclass
class DeploymentResult:
    """Result of a deployment operation."""
    success: bool
    repo_url: Optional[str] = None
    agent_id: Optional[str] = None
    error: Optional[str] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        return {
            "success": self.success,
            "repo_url": self.repo_url,
            "agent_id": self.agent_id,
            "error": self.error,
            "timestamp": self.timestamp
        }


class DeploymentManager:
    """Manages deployment of agents to GitHub and OpenClaw."""
    
    def __init__(
        self,
        github_org: Optional[str] = None,
        github_token: Optional[str] = None,
        openclaw_config_path: Optional[str] = None,
        output_dir: Optional[str] = None
    ):
        self.github_org = github_org or os.getenv("WORLD_CEO_GITHUB_ORG", "openclaw-agents")
        self.github_token = github_token or os.getenv("GH_TOKEN")
        self.openclaw_config_path = openclaw_config_path or os.getenv(
            "OPENCLAW_CONFIG_PATH",
            "/Users/aiagent/.openclaw/workspace"
        )
        self.output_dir = Path(output_dir or os.getenv("WORLD_CEO_OUTPUT_DIR", "./output"))
    
    def _slugify(self, name: str) -> str:
        """Convert name to URL-friendly slug."""
        return name.lower().replace(" ", "-").replace("_", "-")
    
    def _run_command(self, cmd: List[str], cwd: Optional[Path] = None, check: bool = True) -> subprocess.CompletedProcess:
        """Run a shell command with error handling."""
        logger.debug(f"Running: {' '.join(cmd)}")
        
        env = os.environ.copy()
        if self.github_token:
            env["GH_TOKEN"] = self.github_token
        
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
                env=env,
                check=False
            )
            
            if check and result.returncode != 0:
                raise subprocess.CalledProcessError(
                    result.returncode,
                    cmd,
                    output=result.stdout,
                    stderr=result.stderr
                )
            
            return result
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed: {e}")
            logger.error(f"stdout: {e.output}")
            logger.error(f"stderr: {e.stderr}")
            raise
    
    def check_github_auth(self) -> bool:
        """Check if GitHub CLI is authenticated."""
        try:
            result = self._run_command(["gh", "auth", "status"], check=False)
            return result.returncode == 0
        except Exception as e:
            logger.error(f"GitHub auth check failed: {e}")
            return False
    
    def create_github_repo(
        self,
        agent_name: str,
        description: str,
        private: bool = False
    ) -> str:
        """
        Create a GitHub repository for the agent.
        
        Args:
            agent_name: Name of the agent
            description: Repository description
            private: Whether to create a private repo
            
        Returns:
            Repository URL
        """
        slug = self._slugify(agent_name)
        repo_name = f"agent-{slug}"
        
        logger.info(f"Creating GitHub repository: {repo_name}")
        
        # Check if repo already exists
        check_result = self._run_command(
            ["gh", "repo", "view", f"{self.github_org}/{repo_name}"],
            check=False
        )
        
        if check_result.returncode == 0:
            logger.info(f"Repository already exists: {repo_name}")
            return f"https://github.com/{self.github_org}/{repo_name}"
        
        # Create new repository
        visibility = "--private" if private else "--public"
        
        cmd = [
            "gh", "repo", "create",
            f"{self.github_org}/{repo_name}",
            visibility,
            "--description", description,
            "--source", str(self.output_dir / slug),
            "--push"
        ]
        
        self._run_command(cmd)
        
        repo_url = f"https://github.com/{self.github_org}/{repo_name}"
        logger.info(f"Created repository: {repo_url}")
        
        return repo_url
    
    def push_to_github(
        self,
        agent_name: str,
        commit_message: Optional[str] = None
    ) -> str:
        """
        Push agent code to GitHub.
        
        Args:
            agent_name: Name of the agent
            commit_message: Optional custom commit message
            
        Returns:
            Commit SHA
        """
        slug = self._slugify(agent_name)
        agent_dir = self.output_dir / slug
        
        if not agent_dir.exists():
            raise FileNotFoundError(f"Agent directory not found: {agent_dir}")
        
        logger.info(f"Pushing {agent_name} to GitHub")
        
        # Initialize git if needed
        git_dir = agent_dir / ".git"
        if not git_dir.exists():
            self._run_command(["git", "init"], cwd=agent_dir)
            self._run_command(["git", "branch", "-M", "main"], cwd=agent_dir)
        
        # Configure git
        self._run_command(
            ["git", "config", "user.email", "world-ceo@openclaw.local"],
            cwd=agent_dir,
            check=False
        )
        self._run_command(
            ["git", "config", "user.name", "WORLD CEO"],
            cwd=agent_dir,
            check=False
        )
        
        # Add all files
        self._run_command(["git", "add", "."], cwd=agent_dir)
        
        # Check if there are changes to commit
        status_result = self._run_command(
            ["git", "status", "--porcelain"],
            cwd=agent_dir
        )
        
        if not status_result.stdout.strip():
            logger.info("No changes to commit")
            # Get current commit SHA
            result = self._run_command(
                ["git", "rev-parse", "HEAD"],
                cwd=agent_dir
            )
            return result.stdout.strip()
        
        # Commit
        message = commit_message or f"Update {agent_name} - {datetime.now().isoformat()}"
        self._run_command(["git", "commit", "-m", message], cwd=agent_dir)
        
        # Push
        self._run_command(["git", "push", "origin", "main"], cwd=agent_dir)
        
        # Get commit SHA
        result = self._run_command(
            ["git", "rev-parse", "HEAD"],
            cwd=agent_dir
        )
        commit_sha = result.stdout.strip()
        
        logger.info(f"Pushed commit: {commit_sha[:8]}")
        return commit_sha
    
    def generate_openclaw_config(self, agent_name: str, spec: dict) -> dict:
        """
        Generate OpenClaw gateway configuration for the agent.
        
        Args:
            agent_name: Name of the agent
            spec: Agent specification
            
        Returns:
            Configuration dictionary
        """
        slug = self._slugify(agent_name)
        
        config = {
            "agent": {
                "id": slug,
                "name": agent_name,
                "version": "0.1.0",
                "description": spec.get("description", ""),
                "category": spec.get("category", "general")
            },
            "routing": {
                "enabled": True,
                "patterns": [
                    f"{spec.get('category', 'general')}"
                ],
                "priority": 50
            },
            "tools": {
                "allowed": spec.get("core_tools", []),
                "permissions": ["read", "write"]
            },
            "deployment": {
                "repository": f"https://github.com/{self.github_org}/agent-{slug}",
                "entry_point": f"skills/{slug}_skill.py",
                "health_check": "/health"
            },
            "resources": {
                "max_memory": "512MB",
                "timeout": 300,
                "concurrent_requests": 5
            },
            "logging": {
                "level": "INFO",
                "destination": "stdout",
                "format": "json"
            }
        }
        
        return config
    
    def write_openclaw_config(self, agent_name: str, config: dict) -> Path:
        """
        Write OpenClaw configuration to file.
        
        Args:
            agent_name: Name of the agent
            config: Configuration dictionary
            
        Returns:
            Path to config file
        """
        slug = self._slugify(agent_name)
        config_dir = Path(self.openclaw_config_path) / "agents"
        config_dir.mkdir(parents=True, exist_ok=True)
        
        config_path = config_dir / f"{slug}.json"
        config_path.write_text(json.dumps(config, indent=2))
        
        logger.info(f"Written OpenClaw config: {config_path}")
        return config_path
    
    def deploy(
        self,
        agent_name: str,
        spec: dict,
        push_to_github: bool = True,
        configure_openclaw: bool = True
    ) -> DeploymentResult:
        """
        Deploy an agent completely.
        
        Args:
            agent_name: Name of the agent
            spec: Agent specification
            push_to_github: Whether to push to GitHub
            configure_openclaw: Whether to configure OpenClaw
            
        Returns:
            DeploymentResult
        """
        logger.info(f"Starting deployment for: {agent_name}")
        
        try:
            repo_url = None
            agent_id = None
            
            # Push to GitHub
            if push_to_github:
                if not self.check_github_auth():
                    return DeploymentResult(
                        success=False,
                        error="GitHub CLI not authenticated. Run 'gh auth login'"
                    )
                
                repo_url = self.create_github_repo(
                    agent_name,
                    spec.get("description", f"{agent_name} agent")
                )
                self.push_to_github(agent_name)
            
            # Configure OpenClaw
            if configure_openclaw:
                config = self.generate_openclaw_config(agent_name, spec)
                config_path = self.write_openclaw_config(agent_name, config)
                agent_id = config["agent"]["id"]
            
            logger.info(f"Deployment complete for: {agent_name}")
            
            return DeploymentResult(
                success=True,
                repo_url=repo_url,
                agent_id=agent_id
            )
            
        except Exception as e:
            logger.error(f"Deployment failed: {e}")
            return DeploymentResult(
                success=False,
                error=str(e)
            )
    
    def generate_github_actions(self, agent_name: str) -> str:
        """Generate GitHub Actions workflow for CI/CD."""
        slug = self._slugify(agent_name)
        
        return f'''name: CI/CD

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Lint with flake8
      run: |
        flake8 skills/ --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 skills/ --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
    
    - name: Test with pytest
      run: |
        pytest tests/ --cov=skills --cov-report=xml
    
    - name: Type check with mypy
      run: |
        mypy skills/

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to OpenClaw
      run: |
        echo "Deploying {agent_name}..."
        # Add deployment commands here
'''
    
    def write_github_actions(self, agent_name: str) -> Path:
        """Write GitHub Actions workflow file."""
        slug = self._slugify(agent_name)
        agent_dir = self.output_dir / slug
        
        workflows_dir = agent_dir / ".github" / "workflows"
        workflows_dir.mkdir(parents=True, exist_ok=True)
        
        workflow_content = self.generate_github_actions(agent_name)
        workflow_path = workflows_dir / "ci.yml"
        workflow_path.write_text(workflow_content)
        
        logger.info(f"Written GitHub Actions: {workflow_path}")
        return workflow_path


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Deploy agent")
    parser.add_argument("--spec", "-s", required=True, help="Agent spec JSON file")
    parser.add_argument("--no-github", action="store_true", help="Skip GitHub push")
    parser.add_argument("--no-openclaw", action="store_true", help="Skip OpenClaw config")
    
    args = parser.parse_args()
    
    # Load spec
    with open(args.spec, 'r') as f:
        spec = json.load(f)
    
    # Deploy
    manager = DeploymentManager()
    result = manager.deploy(
        spec["name"],
        spec,
        push_to_github=not args.no_github,
        configure_openclaw=not args.no_openclaw
    )
    
    print(json.dumps(result.to_dict(), indent=2))
    
    if not result.success:
        exit(1)


if __name__ == "__main__":
    main()
