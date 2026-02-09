# Examples

## Basic: Create and Poll

```python
from scripts.rebyte_client import RebyteClient

client = RebyteClient()

# Create a task
task = client.create_task(prompt="Say hello world")
print(f"Task running: {task['url']}")

# Wait for completion
result = client.wait_for_task(task["id"])
print(f"Done! Status: {result['status']}")
print(f"View results: {result['url']}")
```

## Create with Skills

```python
task = client.create_task(
    prompt="Research the latest trends in AI agents",
    skills=["deep-research"]
)
result = client.wait_for_task(task["id"])
```

## Create with GitHub Repo

```python
task = client.create_task(
    prompt="Add unit tests for the auth module",
    skills=["pdf"],
    github_url="my-org/my-repo",
    branch_name="main"
)
result = client.wait_for_task(task["id"])
```

## Reuse a Workspace

Pass `workspaceId` from a previous task to run in the same VM. Skips provisioning and is much faster.

```python
# First task provisions a new VM
task1 = client.create_task(
    prompt="Set up the project structure",
    github_url="my-org/my-repo"
)
result1 = client.wait_for_task(task1["id"])

# Second task reuses the same VM — no provisioning delay
task2 = client.create_task(
    prompt="Now add authentication",
    workspace_id=task1["workspaceId"]
)
result2 = client.wait_for_task(task2["id"])

# Third task, same workspace
task3 = client.create_task(
    prompt="Add rate limiting",
    workspace_id=task1["workspaceId"]
)
result3 = client.wait_for_task(task3["id"])
```

## Follow-Up Prompts

```python
# Create initial task
task = client.create_task(prompt="Build a REST API with Express")
result = client.wait_for_task(task["id"])

# Send follow-up
client.follow_up(task["id"], prompt="Now add authentication with JWT")
result = client.wait_for_task(task["id"])

# Another follow-up
client.follow_up(task["id"], prompt="Add rate limiting")
result = client.wait_for_task(task["id"])

print(f"View all results: {result['url']}")
```

## List and Manage Tasks

```python
# List recent tasks
tasks = client.list_tasks(limit=10)
for t in tasks["data"]:
    print(f"{t['id']}: {t['title']}")

# Delete a task
client.delete_task(task["id"])
```

## Batch Processing

```python
import concurrent.futures

client = RebyteClient()

prompts = [
    "Analyze auth module for security issues",
    "Generate API documentation",
    "Write integration tests for payments",
]

def run_task(prompt):
    task = client.create_task(
        prompt=prompt,
        github_url="my-org/my-repo"
    )
    return client.wait_for_task(task["id"])

# Run all tasks concurrently
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(run_task, prompts))

for r in results:
    print(f"{r['title']}: {r['status']} - {r['url']}")
```

## Sequential Tasks in Same Workspace

```python
client = RebyteClient()

# First task provisions the VM
task = client.create_task(
    prompt="Clone and analyze the repo",
    github_url="my-org/my-repo"
)
result = client.wait_for_task(task["id"])
ws_id = task["workspaceId"]

# Run a sequence of tasks in the same workspace
for step in ["Fix linting errors", "Add missing tests", "Update README"]:
    t = client.create_task(prompt=step, workspace_id=ws_id)
    r = client.wait_for_task(t["id"])
    print(f"{r['title']}: {r['status']}")
```

## Error Handling

```python
from scripts.rebyte_client import RebyteClient, APIError

client = RebyteClient()

try:
    task = client.create_task(prompt="Do something")
    result = client.wait_for_task(task["id"], timeout_seconds=120)
except APIError as e:
    print(f"API Error: {e.message} (HTTP {e.status_code})")
except TimeoutError as e:
    print(f"Task timed out: {e}")
```

## CLI Examples

```bash
# Create a task
python3 scripts/rebyte_cli.py create --prompt "Analyze this repo" --skills deep-research

# Get task details
python3 scripts/rebyte_cli.py get TASK_ID

# Send follow-up
python3 scripts/rebyte_cli.py follow-up TASK_ID --prompt "Fix the issues"

# List all tasks
python3 scripts/rebyte_cli.py list --limit 20

# Delete a task
python3 scripts/rebyte_cli.py delete TASK_ID
```
