# Examples

## Basic Usage

### Listing Skills

```python
from scripts.skill_service import list_skills

# Get all skills
all_skills = list_skills(limit=50)

# Search for specific skills
python_skills = list_skills(search="python")

# Filter by category
category_skills = list_skills(category="document")
```

### Spawning an Agent

```python
from scripts.skill_service import spawn_agent

agent = spawn_agent(
    agent_name="pdf-processor",
    skills=["anthropics-pdf", "anthropics-docx"],
    prompt="You are a document processing assistant. Help users with PDF operations.",
    max_iterations=100
)

print(f"Agent ID: {agent['agent_id']}")
```

### Running a Task

```python
from scripts.skill_service import run_task

result = run_task(
    agent_id="agent_abc123",
    task_description="Extract text from the PDF file",
    input_data={
        "file_path": "/path/to/document.pdf",
        "operation": "extract_text"
    },
    wait_for_completion=True,
    timeout_seconds=300
)

print(f"Status: {result['status']}")
print(f"Result: {result['result']}")
```

## Agent Management

### List All Agents

```python
from scripts.skill_service import get_client

client = get_client()
agents = client.list_agents(status="running", limit=20)

for agent in agents.get("agents", []):
    print(f"{agent['agent_id']}: {agent['status']}")
```

### Check Agent Info

```python
info = client.get_agent_info("agent_abc123")
print(f"Status: {info['status']}")
print(f"Skills: {info['skills']}")
print(f"Created: {info['created_at']}")
```

### Terminate Agent

```python
result = client.terminate_agent("agent_abc123")
print(f"Terminated: {result.get('success', False)}")
```

## Custom Polling

If you need custom polling logic:

```python
from scripts.skill_service import get_client

client = get_client()

# Start task without waiting
task = client.run_task(
    agent_id="agent_abc123",
    task_description="Process large file",
    wait_for_completion=False
)

task_id = task["task_id"]

# Custom polling
import time
while True:
    status = client.get_task_status(task_id)
    print(f"Status: {status['status']}")

    if status["status"] in ("completed", "failed", "cancelled"):
        break

    time.sleep(5)
```

## Error Handling

```python
from scripts.skill_service import SkillServiceClient, APIError

client = SkillServiceClient()

try:
    agent = client.spawn_agent(
        agent_name="test-agent",
        skills=["invalid-skill"],
        prompt="Test"
    )
except APIError as e:
    print(f"API Error: {e.message}")
    print(f"Status Code: {e.status_code}")
    print(f"Response: {e.response}")
```

## Complete Workflow

```python
from scripts.skill_service import get_client

client = get_client()

# 1. List available skills
skills = client.list_skills(search="pdf", limit=5)
print("Available PDF skills:", skills["skills"])

# 2. Spawn an agent
agent = client.spawn_agent(
    agent_name="my-pdf-agent",
    skills=["anthropics-pdf"],
    prompt="You are a PDF expert."
)
print(f"Agent created: {agent['agent_id']}")

# 3. Run a task
result = client.run_task(
    agent_id=agent["agent_id"],
    task_description="Merge these two PDF files",
    input_data={
        "files": ["/path/a.pdf", "/path/b.pdf"],
        "operation": "merge"
    }
)
print(f"Task completed: {result['status']}")
print(f"Output: {result['result']}")

# 4. Clean up
client.terminate_agent(agent["agent_id"])
print("Agent terminated")
```

## CLI Examples

### Basic Flow

```bash
# 1. List skills
python3 scripts/skill_cli.py list-skills --search docx

# 2. Spawn agent
python3 scripts/skill_cli.py spawn-agent --name doc-worker --skills anthropics-docx

# 3. Run task
python3 scripts/skill_cli.py run-task --agent-id agent_abc123 --task "Analyze document" --input '{"path": "report.docx"}'

# 4. List agents
python3 scripts/skill_cli.py list-agents --status running

# 5. Terminate agent
python3 scripts/skill_cli.py terminate-agent --agent-id agent_abc123
```
