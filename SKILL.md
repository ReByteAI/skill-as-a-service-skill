---
name: skill-as-a-service
description: |
  Run coding agents (Claude Code, Gemini, Codex) with specific skills in the cloud via API.
  No local setup, no CLI installation, no config files -- just an API key.
  Use when:
  - User wants to run a coding agent with skills attached, without any local setup
  - User wants to fire off tasks to Claude Code (or other agents) from their own code
  - User needs to create a task with specific skills (deep research, PDF, data analysis, etc.)
  - User wants to share task results with end users via a public link
  - User wants to run multiple tasks concurrently or in the same workspace

  Requires a REBYTE_API_KEY environment variable.
---

# Coding Agents with Skills, via API

Run coding agents like Claude Code, Gemini CLI, or Codex with specific skills -- all from a single API key. No local setup, no CLI installation, no configuration files. Each task gets its own isolated cloud environment with the skills you need.

If you want to run a coding agent on a task and have it use specific skills (deep research, PDF processing, data analysis, etc.), this is for you. As long as you have a `REBYTE_API_KEY`, you can fire off as many tasks as you want without touching any local settings.

## Task Lifecycle

```
 1. CREATE                  2. RETURN URL                3. SHARE (optional)
 ┌──────────────┐           ┌──────────────┐            ┌──────────────┐
 │ POST /tasks  │           │              │            │ PATCH        │
 │              │──────────▶│  Give the    │───────────▶│ /tasks/:id/  │
 │ prompt       │           │  task URL    │            │ visibility   │
 │ skills       │           │  to the user │            │              │
 │ executor     │           │              │            │ → public     │
 │ repo         │           │  They watch  │            │ → shareUrl   │
 └──────────────┘           │  it live     │            └──────────────┘
                            └──────┬───────┘                   │
                                   │                           ▼
                                   │                    Anyone can view
                                   │                    (no login needed)
                                   │
                          ┌────────▼───────┐
                          │  Optional:     │
                          │                │
                          │  • Poll status │  GET /tasks/:id
                          │  • Follow up   │  POST /tasks/:id/prompts
                          │  • Reuse VM    │  POST /tasks (with workspaceId)
                          └────────────────┘
```

**The core flow is simple:**
1. **Create** a task with a prompt, skills, and optionally a GitHub repo
2. **Return the URL** to the user -- they can watch the task execute live in the browser
3. **Optionally share** the result by setting visibility to `public` for a link anyone can view

You don't need to poll for completion. You don't even need to know when it finishes. The URL is live from the moment the task starts -- the user sees the agent working in real time.

## Agent Instructions: Setup & Authentication

### Step 1: Verify API Key
Before performing any action, check if the `REBYTE_API_KEY` environment variable is available.
- **If missing**: Pause and ask the user: *"I need an API key to proceed. You can get one at [app.rebyte.ai/settings/api-keys](https://app.rebyte.ai/settings/api-keys). Please provide your key or set the `REBYTE_API_KEY` environment variable."*
- **If present**: Continue with the user's request.

## API Overview

**Base URL:** `https://api.rebyte.ai/v1`

**Authentication:** `API_KEY` header with your API key.

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /v1/tasks | Create a task (blocks until running) |
| GET | /v1/tasks | List API-created tasks |
| GET | /v1/tasks/:id | Get task with derived status and prompts |
| POST | /v1/tasks/:id/prompts | Send a follow-up prompt |
| PATCH | /v1/tasks/:id/visibility | Change task visibility (get share URL) |
| DELETE | /v1/tasks/:id | Soft-delete a task |

## Quick Start

### Create a task and return the URL

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

That's it. Give the `url` to the user -- they can watch the agent work in real time. The task runs in the cloud regardless of whether anyone is watching.

### Make it shareable (optional)

If the user viewing the URL isn't logged in to your org, set visibility to `public`:

```bash
curl -X PATCH https://api.rebyte.ai/v1/tasks/$TASK_ID/visibility \
  -H "API_KEY: $REBYTE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"visibility": "public"}'
```

Response:
```json
{
  "visibility": "public",
  "shareUrl": "https://app.rebyte.ai/share/550e8400-e29b-41d4-a716-446655440000"
}
```

The `shareUrl` is viewable by anyone -- no login required.

### Poll for status (optional)

If you need to know when a task finishes (e.g., to chain work):

```bash
curl https://api.rebyte.ai/v1/tasks/$TASK_ID \
  -H "API_KEY: $REBYTE_API_KEY"
```

### Send a follow-up (optional)

```bash
curl -X POST https://api.rebyte.ai/v1/tasks/$TASK_ID/prompts \
  -H "API_KEY: $REBYTE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Now fix the critical issues you found"}'
```

### Reuse a workspace (optional)

Pass `workspaceId` from a previous create response to run a new task in the same VM. Skips provisioning and is much faster.

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

## Lifecycle Examples (Python)

### Simplest: fire and forget

```python
from scripts.rebyte_client import RebyteClient

client = RebyteClient()  # reads REBYTE_API_KEY from env

task = client.create_task(
    prompt="Analyze this repo for security vulnerabilities",
    skills=["deep-research"],
    github_url="my-org/my-repo"
)

# Just return the URL -- the user watches it live
print(f"Watch here: {task['url']}")
```

### With sharing

```python
task = client.create_task(
    prompt="Generate a report on Q4 sales data",
    skills=["data-analysis"]
)

# Make it public so anyone can view
vis = client.set_visibility(task["id"], "public")
print(f"Share this link: {vis['shareUrl']}")
```

### With polling (when you need to chain work)

```python
task = client.create_task(prompt="Build a REST API with Express")
result = client.wait_for_task(task["id"])
print(f"Status: {result['status']}")

# Now send a follow-up
client.follow_up(task["id"], prompt="Add authentication with JWT")
result = client.wait_for_task(task["id"])
print(f"Done: {result['url']}")
```

## Task Status

| Status | Meaning |
|--------|--------|
| `running` | Any prompt is pending or running |
| `completed` | All prompts done, latest succeeded |
| `failed` | All prompts done, latest failed |
| `canceled` | All prompts done, latest canceled |

## Visibility Levels

| Level | Who can view |
|-------|-------------|
| `private` | Only the API key owner |
| `shared` | All organization members (default) |
| `public` | Anyone with the link (read-only) |

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
