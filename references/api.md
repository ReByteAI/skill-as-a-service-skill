# API Reference

## Config

Configuration dataclass for the API client.

```python
@dataclass
class Config:
    api_key: str           # API authentication key
    base_url: str = "https://api.rebyte.ai"  # API base URL
```

### from_env()

Load configuration from environment variables.

```python
config = Config.from_env()
# Reads SKILL_SERVICE_API_KEY and optionally SKILL_SERVICE_BASE_URL
```

## APIError

Exception raised for API errors.

```python
class APIError(Exception):
    message: str                    # Error message
    status_code: Optional[int]      # HTTP status code
    response: Optional[Dict]        # Full response data
```

## SkillServiceClient

Main client class for interacting with the Skill as a Service API.

### Constructor

```python
client = SkillServiceClient(
    api_key: str = None,        # Optional API key (uses env if not provided)
    base_url: str = None        # Optional base URL
)
```

### Methods

#### Skills

| Method | HTTP | Endpoint | Description |
|--------|------|----------|-------------|
| `list_skills()` | GET | /v1/skills | List available skills |
| `get_skill_details()` | GET | /v1/skills/{skill_id} | Get skill details |

#### Agents

| Method | HTTP | Endpoint | Description |
|--------|------|----------|-------------|
| `spawn_agent()` | POST | /v1/agents | Create new agent |
| `list_agents()` | GET | /v1/agents | List all agents |
| `get_agent_info()` | GET | /v1/agents/{agent_id} | Get agent details |
| `terminate_agent()` | DELETE | /v1/agents/{agent_id} | Stop agent |

#### Tasks

| Method | HTTP | Endpoint | Description |
|--------|------|----------|-------------|
| `run_task()` | POST | /v1/agents/{agent_id}/tasks | Execute task |
| `get_task_status()` | GET | /v1/tasks/{task_id} | Check status |
| `wait_for_task()` | GET | /v1/tasks/{task_id} | Poll until done |
| `cancel_task()` | POST | /v1/tasks/{task_id}/cancel | Cancel task |

## Response Formats

### List Skills Response

```json
{
  "skills": [
    {
      "id": "anthropics-pdf",
      "name": "anthropics-pdf",
      "description": "Process PDF files...",
      "category": "document"
    }
  ],
  "total": 50,
  "limit": 20
}
```

### Spawn Agent Response

```json
{
  "agent_id": "agent_abc123",
  "name": "my-agent",
  "status": "running",
  "skills": ["anthropics-pdf", "anthropics-docx"],
  "created_at": "2025-01-15T10:30:00Z"
}
```

### Task Status Response

```json
{
  "task_id": "task_xyz789",
  "status": "completed",
  "result": {"output": "..."},
  "started_at": "2025-01-15T10:30:00Z",
  "completed_at": "2025-01-15T10:30:45Z"
}
```

## Status Values

### Agent Status
- `pending` - Agent is being created
- `running` - Agent is active and ready
- `stopped` - Agent has been stopped
- `error` - Agent encountered an error

### Task Status
- `pending` - Task is queued
- `running` - Task is executing
- `completed` - Task finished successfully
- `failed` - Task encountered an error
- `cancelled` - Task was cancelled
