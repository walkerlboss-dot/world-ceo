# WORLD CEO - Tools Reference

## Core Tools

### 1. Domain Research

**web_search**
- Purpose: Research emerging domains and opportunities
- Usage: `web_search(query, count=10, freshness="week")`
- Returns: Structured search results with titles, URLs, snippets

**browser**
- Purpose: Deep research on specific sites, JS-heavy pages
- Usage: `browser(action="snapshot", url=...)`, `browser(action="act", kind="click", ref=...)`
- Returns: Rendered page content, interactive automation

**web_fetch**
- Purpose: Quick content extraction from URLs
- Usage: `web_fetch(url, extractMode="markdown", maxChars=5000)`
- Returns: Clean text/markdown content

### 2. Code Generation

**write**
- Purpose: Create files with generated code
- Usage: `write(path, content)`
- Creates parent directories automatically

**edit**
- Purpose: Modify existing files
- Usage: `edit(path, edits=[{oldText, newText}])`
- Non-overlapping edits only

**read**
- Purpose: Read file contents
- Usage: `read(path, offset=1, limit=100)`
- Supports text files and images

### 3. Execution & Testing

**exec**
- Purpose: Run shell commands, scripts, tests
- Usage: `exec(command, workdir=..., timeout=300)`
- Returns: Command output or background session ID

**process**
- Purpose: Manage background processes
- Usage: `process(action="poll", sessionId=...)`
- Actions: list, poll, log, write, kill

### 4. GitHub Integration

**github CLI (gh)**
- Purpose: Repository management, PRs, issues
- Usage: `gh repo create`, `gh pr create`, `gh issue list`
- Auth: Requires `GH_TOKEN` environment variable

### 5. Memory & Knowledge

**memory_search**
- Purpose: Search prior learnings and agent specs
- Usage: `memory_search(query, corpus="all", maxResults=10)`
- Returns: Relevant memory entries

**memory_get**
- Purpose: Read specific memory files
- Usage: `memory_get(path, from=1, lines=50)`

### 6. File System

**Standard operations**
- `ls`, `cat`, `mkdir`, `cp`, `mv`, `rm`, `find`
- Use for directory traversal and file management

## Agent-Specific Tools

### Domain Researcher

```python
# Research workflow
def research_domain(topic: str) -> DomainAnalysis:
    """
    1. Search for recent discussions
    2. Fetch top result content
    3. Analyze pain points
    4. Score opportunity
    5. Return structured analysis
    """
```

### Spec Writer

```python
# Generate agent specification
def write_agent_spec(domain: DomainAnalysis) -> AgentSpec:
    """
    1. Design personality (SOUL.md)
    2. Define tools (TOOLS.md)
    3. Write operations (AGENTS.md)
    4. Create heartbeat (HEARTBEAT.md)
    5. Return complete spec package
    """
```

### Code Generator

```python
# Generate implementation
def generate_code(spec: AgentSpec) -> CodePackage:
    """
    1. Generate skill modules
    2. Create scripts
    3. Write tests
    4. Add configuration
    5. Return deployable code
    """
```

### Deployment Manager

```python
# Deploy agent
def deploy_agent(code: CodePackage, github_repo: str) -> DeploymentResult:
    """
    1. Create/update GitHub repo
    2. Push code
    3. Configure OpenClaw
    4. Verify deployment
    5. Return status
    """
```

### Self-Improver

```python
# Analyze and improve
def analyze_performance(agent_id: str) -> ImprovementPlan:
    """
    1. Read agent logs
    2. Identify patterns
    3. Update templates
    4. Queue improvements
    5. Return plan
    """
```

## Environment Variables

Required for operation:
```bash
# API Keys
BRAVE_API_KEY=           # For web search
BROWSERBASE_API_KEY=     # For browser automation
BROWSERBASE_PROJECT_ID=  # For browser sessions
GH_TOKEN=                # For GitHub operations
OPENAI_API_KEY=          # For embeddings (optional)

# Configuration
WORLD_CEO_LOG_LEVEL=INFO # DEBUG, INFO, WARN, ERROR
WORLD_CEO_OUTPUT_DIR=./output
WORLD_CEO_GITHUB_ORG=    # Default org for repos
```

## Error Handling

All tools should handle:
- **Network failures**: Retry with exponential backoff
- **Rate limits**: Respect headers, queue requests
- **Auth failures**: Clear error messages, no silent failures
- **Timeouts**: Configurable limits, graceful degradation

## Tool Constraints

- Browser sessions: Max 5 minutes
- File writes: Atomic operations
- GitHub API: Respect rate limits (5000/hour)
- Search queries: Max 10 results per call
- Memory search: Max 20 results
