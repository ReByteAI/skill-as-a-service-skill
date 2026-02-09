# Examples

All examples use `curl` and assume `REBYTE_API_KEY` is set.

## Simplest: Create and Return URL

```bash
TASK=$(curl -s -X POST https://api.rebyte.ai/v1/tasks \
  -H "API_KEY: $REBYTE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Analyze this codebase for security issues", "skills": ["deep-research"]}')

echo "Watch here: $(echo $TASK | jq -r '.url')"
```

## Upload File and Create Task

```bash
# 1. Get signed upload URL
FILE_RESP=$(curl -s -X POST https://api.rebyte.ai/v1/files \
  -H "API_KEY: $REBYTE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"filename": "report.pdf"}')

UPLOAD_URL=$(echo "$FILE_RESP" | jq -r '.uploadUrl')
FILE_ID=$(echo "$FILE_RESP" | jq -r '.id')
FILE_NAME=$(echo "$FILE_RESP" | jq -r '.filename')

# 2. Upload file content
curl -s -X PUT "$UPLOAD_URL" \
  -H "Content-Type: application/octet-stream" \
  --data-binary @report.pdf

# 3. Create task with the file
TASK=$(curl -s -X POST https://api.rebyte.ai/v1/tasks \
  -H "API_KEY: $REBYTE_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"prompt\": \"Summarize this PDF and extract key findings\",
    \"skills\": [\"pdf\"],
    \"files\": [{\"id\": \"$FILE_ID\", \"filename\": \"$FILE_NAME\"}]
  }")

echo "Watch here: $(echo $TASK | jq -r '.url')"
```

## Upload Multiple Files

```bash
# Upload each file
for FILE_PATH in data.csv notes.pdf config.json; do
  RESP=$(curl -s -X POST https://api.rebyte.ai/v1/files \
    -H "API_KEY: $REBYTE_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"filename\": \"$FILE_PATH\"}")

  curl -s -X PUT "$(echo $RESP | jq -r '.uploadUrl')" \
    -H "Content-Type: application/octet-stream" \
    --data-binary @"$FILE_PATH"

  echo "Uploaded: $(echo $RESP | jq -r '.filename')"
  # Save file info for task creation
  FILES="$FILES{\"id\": $(echo $RESP | jq '.id'), \"filename\": $(echo $RESP | jq '.filename')},"
done

# Remove trailing comma and create task
FILES="[${FILES%,}]"
curl -s -X POST https://api.rebyte.ai/v1/tasks \
  -H "API_KEY: $REBYTE_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"prompt\": \"Analyze all these files and create a summary report\",
    \"skills\": [\"data-analysis\", \"pdf\"],
    \"files\": $FILES
  }"
```

## Create Task with GitHub Repo

```bash
TASK=$(curl -s -X POST https://api.rebyte.ai/v1/tasks \
  -H "API_KEY: $REBYTE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Add unit tests for the auth module",
    "githubUrl": "my-org/my-repo",
    "branchName": "main"
  }')

echo "Task: $(echo $TASK | jq -r '.url')"
```

## Create and Share Publicly

```bash
# Create the task
TASK=$(curl -s -X POST https://api.rebyte.ai/v1/tasks \
  -H "API_KEY: $REBYTE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Generate a Q4 sales report", "skills": ["data-analysis"]}')
TASK_ID=$(echo $TASK | jq -r '.id')

# Make it public
SHARE=$(curl -s -X PATCH "https://api.rebyte.ai/v1/tasks/$TASK_ID/visibility" \
  -H "API_KEY: $REBYTE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"visibility": "public"}')

echo "Share this link: $(echo $SHARE | jq -r '.shareUrl')"
```

## Poll Until Complete

```bash
TASK_ID="your-task-id"
while true; do
  STATUS=$(curl -s "https://api.rebyte.ai/v1/tasks/$TASK_ID" \
    -H "API_KEY: $REBYTE_API_KEY" | jq -r '.status')
  echo "Status: $STATUS"
  [[ "$STATUS" == "completed" || "$STATUS" == "failed" || "$STATUS" == "canceled" ]] && break
  sleep 5
done
```

## Follow-Up Prompts

```bash
# Create initial task
TASK=$(curl -s -X POST https://api.rebyte.ai/v1/tasks \
  -H "API_KEY: $REBYTE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Build a REST API with Express"}')
TASK_ID=$(echo $TASK | jq -r '.id')

# Wait for completion, then follow up
# ... (poll or just wait) ...

curl -s -X POST "https://api.rebyte.ai/v1/tasks/$TASK_ID/prompts" \
  -H "API_KEY: $REBYTE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Now add authentication with JWT"}'

# Another follow-up
curl -s -X POST "https://api.rebyte.ai/v1/tasks/$TASK_ID/prompts" \
  -H "API_KEY: $REBYTE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Add rate limiting"}'
```

## Reuse Workspace (Faster Subsequent Tasks)

```bash
# First task provisions a new VM
TASK1=$(curl -s -X POST https://api.rebyte.ai/v1/tasks \
  -H "API_KEY: $REBYTE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Set up the project", "githubUrl": "owner/repo"}')
WS_ID=$(echo $TASK1 | jq -r '.workspaceId')

# Second task reuses the same VM — no provisioning delay
TASK2=$(curl -s -X POST https://api.rebyte.ai/v1/tasks \
  -H "API_KEY: $REBYTE_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"prompt\": \"Now add tests\", \"workspaceId\": \"$WS_ID\"}")

echo "Task 2: $(echo $TASK2 | jq -r '.url')"
```

## List and Delete Tasks

```bash
# List recent tasks
curl -s "https://api.rebyte.ai/v1/tasks?limit=10" \
  -H "API_KEY: $REBYTE_API_KEY" | jq '.data[] | {id, title, status: .completedAt}'

# Delete a task
curl -s -X DELETE "https://api.rebyte.ai/v1/tasks/$TASK_ID" \
  -H "API_KEY: $REBYTE_API_KEY" -w "HTTP %{http_code}\n"
```

## Batch: Run Multiple Tasks Concurrently

```bash
# Launch 3 tasks in parallel
for PROMPT in \
  "Analyze auth module for security issues" \
  "Generate API documentation" \
  "Write integration tests for payments"; do

  curl -s -X POST https://api.rebyte.ai/v1/tasks \
    -H "API_KEY: $REBYTE_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"prompt\": \"$PROMPT\", \"githubUrl\": \"my-org/my-repo\"}" &
done
wait
echo "All tasks launched"
```

---

## Python Examples

The skill includes a Python client at `scripts/rebyte_client.py`. To use it:

```bash
# Find the skill directory
SKILL_DIR=$(find ~/.skills -maxdepth 1 -name '*skill-as-a-service*' -type d | head -1)
```

### Using the Python Client

```python
import sys, os

# Add skill scripts to Python path
skill_dir = next(
    (d for d in os.listdir(os.path.expanduser('~/.skills'))
     if 'skill-as-a-service' in d),
    None
)
if skill_dir:
    sys.path.insert(0, os.path.expanduser(f'~/.skills/{skill_dir}/scripts'))

from rebyte_client import RebyteClient

client = RebyteClient()  # reads REBYTE_API_KEY from env

# Create a task
task = client.create_task(
    prompt="Analyze this repo",
    skills=["deep-research"],
    github_url="my-org/my-repo"
)
print(f"Watch here: {task['url']}")

# Upload a file and create task
file_info = client.upload_file("report.pdf")
task = client.create_task(
    prompt="Summarize this PDF",
    skills=["pdf"],
    files=[file_info]
)
print(f"Watch here: {task['url']}")

# Share publicly
vis = client.set_visibility(task["id"], "public")
print(f"Share: {vis['shareUrl']}")

# Wait for completion (optional)
result = client.wait_for_task(task["id"])
print(f"Status: {result['status']}")

# Follow up
client.follow_up(task["id"], prompt="Fix the issues found")
```

### Using the CLI

```bash
SKILL_DIR=$(find ~/.skills -maxdepth 1 -name '*skill-as-a-service*' -type d | head -1)

python3 "$SKILL_DIR/scripts/rebyte_cli.py" create --prompt "Hello world"
python3 "$SKILL_DIR/scripts/rebyte_cli.py" get TASK_ID
python3 "$SKILL_DIR/scripts/rebyte_cli.py" follow-up TASK_ID --prompt "Add tests"
python3 "$SKILL_DIR/scripts/rebyte_cli.py" list --limit 10
python3 "$SKILL_DIR/scripts/rebyte_cli.py" delete TASK_ID
```
