---
name: skill-as-a-service
description: |
  Spawn cloud code agents with specialized skills and execute tasks remotely.
  Use when:
  - User needs to list available skills from a skill store
  - User wants to spawn a cloud agent with specific skills installed
  - User needs to run tasks on a deployed cloud agent
  - User wants to manage cloud agent lifecycle (list, info, terminate)
  - User needs to track task status with polling

  Requires an API key from the skill service provider.
---

# Skill as a Service

Spawn cloud code agents with specialized skills and execute tasks remotely. Specify the task, agents, and skills; the cloud handles provisioning and execution.

## Agent Instructions: Setup & Authentication

### Step 1: Verify API Key
Before performing any action, check if the `SKILL_SERVICE_API_KEY` environment variable is available.
- **If missing**: Pause and ask the user: *"I need a Rebyte API key to proceed. You can get one at [app.rebyte.ai/settings/api-keys](https://app.rebyte.ai/settings/api-keys). Please provide your key or set the `SKILL_SERVICE_API_KEY` environment variable."*
- **If present**: Continue with the user's request.

## Quick Start

### 1. Common Operations

You can use the Python client or the provided CLI tool.

#### Python Client
```python
from scripts.skill_service import get_client

client = get_client()

# List available skills
skills = client.list_skills(search="pdf")

# Spawn an agent (using skill ID or description)
agent = client.smart_spawn_agent(
    agent_name="my-worker",
    skill_queries=["pdf processing"],  # Auto-resolves to 'anthropics-pdf'
    prompt="You are a PDF expert."
)

# Run a task (waits for completion by default)
result = client.run_task(
    agent_id=agent["agent_id"],
    task_description="Extract text from the PDF",
    input_data={"file": "sample.pdf"}
)

# Terminate when done
client.terminate_agent(agent["agent_id"])
```

#### CLI Tool
```bash
# List skills
python3 scripts/skill_cli.py list-skills --search pdf

# Spawn an agent (just describe the skill you need)
python3 scripts/skill_cli.py spawn-agent --name worker --skills "pdf processing"

# Run a task
python3 scripts/skill_cli.py run-task --agent-id AGENT_ID --task "Extract text" --input '{"file": "sample.pdf"}'
```

## Detailed Resources

- **API Reference**: See [references/api.md](references/api.md) for full method signatures, response formats, and error handling.
- **Advanced Examples**: See [references/examples.md](references/examples.md) for complex workflows, custom polling, and bulk processing.

## Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SKILL_SERVICE_API_KEY` | Yes | - | API key for authentication |
| `SKILL_SERVICE_BASE_URL` | No | https://api.rebyte.ai | API base URL |
