# API Reference

## Authentication

All requests require the `API_KEY` header:

```
API_KEY: rbk_your_api_key
```

Get your key at [app.rebyte.ai/settings/api-keys](https://app.rebyte.ai/settings/api-keys).

## Endpoints

### POST /v1/files

Get a signed URL for uploading a file. After uploading, pass `{id, filename}` to the task creation endpoint.

**Request:**
```json
{
  "filename": "data.csv",
  "contentType": "application/octet-stream"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| filename | string | Yes | Original filename (max 255 chars) |
| contentType | string | No | MIME type (default: `application/octet-stream`) |

**Response (201):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "data-550e.csv",
  "uploadUrl": "https://storage.googleapis.com/..."
}
```

The `filename` is a unique version of your original filename (with a short ID suffix). Use this `filename` (not your original) when passing to task creation.

Upload the file content to `uploadUrl` with a PUT request:
```bash
curl -X PUT "$UPLOAD_URL" \
  -H "Content-Type: application/octet-stream" \
  --data-binary @yourfile.csv
```

Upload URLs expire in 1 hour.

---

### POST /v1/tasks

Create a new task. Blocks until the VM is provisioned and the first prompt is sent.

**Request:**
```json
{
  "prompt": "Build a REST API with Express",
  "executor": "opencode",
  "model": "lite",
  "skills": ["deep-research", "pdf"],
  "files": [{"id": "550e8400-...", "filename": "data-550e.csv"}],
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
| files | object[] | No | Files from POST /v1/files. Each: `{"id": "...", "filename": "..."}` |
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

### PATCH /v1/tasks/:id/visibility

Change task visibility. Tasks default to `shared` (org members). Set to `public` to get a shareable link anyone can view.

**Request:**
```json
{
  "visibility": "public"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| visibility | string | Yes | `private`, `shared`, or `public` |

**Response:**
```json
{
  "visibility": "public",
  "shareUrl": "https://app.rebyte.ai/share/550e8400-e29b-41d4-a716-446655440000"
}
```

`shareUrl` is only returned when visibility is `public`.

| Level | Who can view |
|-------|-------------|
| `private` | Only the API key owner |
| `shared` | All organization members (default) |
| `public` | Anyone with the link (read-only) |

---

### DELETE /v1/tasks/:id

Soft-delete a task.

**Response:** `204 No Content`

---

## Task Status Values

| Status | Condition |
|--------|----------|
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
