# API Reference

## Authentication

All requests require the `API_KEY` header:

```
API_KEY: rbk_your_api_key
```

Get your key at [app.rebyte.ai/settings/api-keys](https://app.rebyte.ai/settings/api-keys).

## Endpoints

### POST /v1/tasks

Create a new task. Blocks until the VM is provisioned and the first prompt is sent.

**Request:**
```json
{
  "prompt": "Build a REST API with Express",
  "executor": "opencode",
  "model": "lite",
  "skills": ["deep-research", "pdf"],
  "githubUrl": "owner/repo",
  "branchName": "main",
  "workspaceId": "optional-uuid-to-reuse-vm"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| prompt | string | Yes | Task description (max 100,000 chars) |
| executor | string | No | `opencode` (default), `claude`, `gemini`, `codex` |
| model | string | No | Model tier (default: `lite`) |
| skills | string[] | No | Skill slugs |
| githubUrl | string | No | GitHub repo (`owner/repo`) |
| branchName | string | No | Branch (default: `main`) |
| workspaceId | string | No | Reuse an existing workspace UUID. Skips provisioning, reuses VM and git state. |

**Response (201):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "workspaceId": "660e8400-e29b-41d4-a716-446655440001",
  "url": "https://app.rebyte.ai/run/550e8400-e29b-41d4-a716-446655440000",
  "status": "running",
  "createdAt": "2026-02-09T10:30:00.000Z"
}
```

Save `workspaceId` to create subsequent tasks in the same VM.

---

### GET /v1/tasks

List API-created tasks, newest first.

**Query Parameters:**

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| limit | number | 50 | Results per page (max 100) |
| offset | number | 0 | Offset for pagination |

**Response:**
```json
{
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "url": "https://app.rebyte.ai/run/550e8400-...",
      "title": "Build REST API with Express",
      "executor": "opencode",
      "model": "lite",
      "createdAt": "2026-02-09T10:30:00.000Z",
      "completedAt": "2026-02-09T10:32:00.000Z"
    }
  ],
  "total": 42,
  "limit": 50,
  "offset": 0
}
```

---

### GET /v1/tasks/:id

Get a task with derived status and prompts array.

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "url": "https://app.rebyte.ai/run/550e8400-...",
  "status": "completed",
  "title": "Build REST API with Express",
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

---

### POST /v1/tasks/:id/prompts

Send a follow-up prompt to an existing task. The VM is resumed if stopped.

**Request:**
```json
{
  "prompt": "Now add authentication",
  "skills": ["pdf"]
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| prompt | string | Yes | Follow-up prompt (max 100,000 chars) |
| skills | string[] | No | Skill slugs for this prompt |

**Response (201):**
```json
{
  "promptId": "660e8400-e29b-41d4-a716-446655440001"
}
```

---

### DELETE /v1/tasks/:id

Soft-delete a task.

**Response:** `204 No Content`

---

## Task Status Values

| Status | Condition |
|--------|-----------|
| `running` | Any prompt is `pending` or `running` |
| `completed` | All prompts terminal, latest is `succeeded` |
| `failed` | All prompts terminal, latest is `failed` |
| `canceled` | All prompts terminal, latest is `canceled` |

## Error Format

```json
{
  "error": {
    "code": "validation_error",
    "message": "Invalid request body"
  }
}
```

Error codes: `validation_error`, `not_found`, `unauthorized`, `limit_exceeded`, `internal_error`
