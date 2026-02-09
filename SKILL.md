---
name: skill-as-a-service
description: |
  Run Rebyte skills as cloud API calls. Create tasks with skills attached,
  poll for completion, send follow-ups, and view results.
  Use when:
  - User wants to run a skill in the cloud via API
  - User needs to create a task with specific skills
  - User wants to poll task status until completion
  - User needs to send follow-up prompts to a running task
  - User wants to list or manage API-created tasks
  - User wants to run multiple tasks in the same workspace/VM

  Requires a Rebyte API key.
---

# Skill as a Service

Run any Rebyte skill as a cloud API call. Specify the task, pick an executor and skills; the cloud handles provisioning and execution.

## Agent Instructions: Setup & Authentication

### Step 1: Verify API Key
Before performing any action, check if the `REBYTE_API_KEY` environment variable is available.
- **If missing**: Pause and ask the user: *"I need a Rebyte API key to proceed. You can get one at [app.rebyte.ai/settings/api-keys](https://app.rebyte.ai/settings/api-keys). Please provide your key or set the `REBYTE_API_KEY` environment variable."*
- **If present**: Continue with the user's request.

## API Overview

**Base URL:** `https://api.rebyte.ai/v1`

**Authentication:** `API_KEY` header with your Rebyte API key.

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /v1/tasks | Create a task (blocks until running) |
| GET | /v1/tasks | List API-created tasks |
| GET | /v1/tasks/:id | Get task with derived status and prompts |
| POST | /v1/tasks/:id/prompts | Send a follow-up prompt |
| DELETE | /v1/tasks/:id | Soft-delete a task |

## Quick Start

### Create a task with a skill

```bash
curl -X POST https://api.rebyte.ai/v1/tasks \
  -H "API_KEY: $REBYTE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Analyze this codebase for security issues",
    "skills": ["deep-research"]
  }'
```

Response (201):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "workspaceId": "660e8400-e29b-41d4-a716-446655440001",
  "url": "https://app.rebyte.ai/run/550e8400-e29b-41d4-a716-446655440000",
  "status": "running",
  "createdAt": "2026-02-09T10:30:00.000Z"
}
```

The call blocks until the VM is provisioned and the first prompt is sent. The task is immediately queryable.

### Poll for completion

```bash
curl https://api.rebyte.ai/v1/tasks/$TASK_ID \
  -H "API_KEY: $REBYTE_API_KEY"
```

Response:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "url": "https://app.rebyte.ai/run/550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "title": "Security Analysis of Codebase",
  "executor": "opencode",
  "model": "lite",
  "createdAt": "2026-02-09T10:30:00.000Z",
  "completedAt": "2026-02-09T10:32:00.000Z",
  "prompts": [
    {
      "id": "uuid-1",
      "status": "succeeded",
      "submittedAt": "2026-02-09T10:30:01.000Z",
      "completedAt": "2026-02-09T10:32:00.000Z"
    }
  ]
}
```

### Send a follow-up

```bash
curl -X POST https://api.rebyte.ai/v1/tasks/$TASK_ID/prompts \
  -H "API_KEY: $REBYTE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Now fix the critical issues you found"}'
```

Response (201):
```json
{"promptId": "uuid-2"}
```

### Reuse a workspace

Pass `workspaceId` from a previous create response to run a new task in the same VM. This skips provisioning, reuses the git repo and state, and is significantly faster.

```bash
# First task — provisions a new VM
RESP=$(curl -s -X POST https://api.rebyte.ai/v1/tasks \
  -H "API_KEY: $REBYTE_API_KEY" -H "Content-Type: application/json" \
  -d '{"prompt": "Set up the project", "githubUrl": "owner/repo"}')
WS_ID=$(echo $RESP | jq -r '.workspaceId')

# Second task — reuses the same VM (much faster)
curl -s -X POST https://api.rebyte.ai/v1/tasks \
  -H "API_KEY: $REBYTE_API_KEY" -H "Content-Type: application/json" \
  -d "{\"prompt\": \"Now add tests\", \"workspaceId\": \"$WS_ID\"}"
```

### List tasks

```bash
curl "https://api.rebyte.ai/v1/tasks?limit=10" \
  -H "API_KEY: $REBYTE_API_KEY"
```

### Delete a task

```bash
curl -X DELETE https://api.rebyte.ai/v1/tasks/$TASK_ID \
  -H "API_KEY: $REBYTE_API_KEY"
# Returns 204 No Content
```

## Using the Python Client

```python
from scripts.rebyte_client import RebyteClient

client = RebyteClient()  # reads REBYTE_API_KEY from env

# Create a task with skills
task = client.create_task(
    prompt="Extract text from all PDFs in the repo",
    skills=["pdf"]
)
print(f"Task {task['id']} running: {task['url']}")

# Wait for completion
result = client.wait_for_task(task["id"])
print(f"Status: {result['status']}")

# Send a follow-up
client.follow_up(task["id"], prompt="Now summarize the extracted text")

# Wait again
result = client.wait_for_task(task["id"])
print(f"Done: {result['url']}")

# Create another task in the same workspace (reuses VM)
task2 = client.create_task(
    prompt="Convert summaries to markdown",
    workspace_id=task["workspaceId"]
)
result2 = client.wait_for_task(task2["id"])

# Clean up
client.delete_task(task["id"])
client.delete_task(task2["id"])
```

## Using the CLI

```bash
# Create a task
python3 scripts/rebyte_cli.py create --prompt "Analyze this repo" --skills deep-research

# Get task status
python3 scripts/rebyte_cli.py get TASK_ID

# Send follow-up
python3 scripts/rebyte_cli.py follow-up TASK_ID --prompt "Fix the issues"

# List tasks
python3 scripts/rebyte_cli.py list

# Delete task
python3 scripts/rebyte_cli.py delete TASK_ID
```

## Task Status

| Status | Meaning |
|--------|---------|
| `running` | Any prompt is pending or running |
| `completed` | All prompts done, latest succeeded |
| `failed` | All prompts done, latest failed |
| `canceled` | All prompts done, latest canceled |

## Create Task Options

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| prompt | string | Yes | Task description (max 100,000 chars) |
| executor | string | No | `opencode` (default), `claude`, `gemini`, `codex` |
| model | string | No | Model tier (default: `lite`) |
| skills | string[] | No | Skill slugs (e.g., `["pdf", "deep-research"]`) |
| githubUrl | string | No | GitHub repo (e.g., `owner/repo`) |
| branchName | string | No | Branch name (default: `main`) |
| workspaceId | string | No | Reuse an existing workspace (same VM, repo, git state). Get from a previous create response. |

## Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `REBYTE_API_KEY` | Yes | - | API key from [app.rebyte.ai/settings/api-keys](https://app.rebyte.ai/settings/api-keys) |

## Detailed Resources

- **API Reference**: See [references/api.md](references/api.md)
- **Examples**: See [references/examples.md](references/examples.md)
