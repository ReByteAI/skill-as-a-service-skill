"""
Rebyte API Client

Simple client for the Rebyte v1 API:
- Create tasks with skills
- Poll for task completion
- Send follow-up prompts
- List and delete tasks
"""

import os
import json
import time
import urllib.request
import urllib.error
from typing import Any, Dict, List, Optional


class APIError(Exception):
    """Exception raised for API errors."""
    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[Dict] = None):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)


class RebyteClient:
    """Client for the Rebyte v1 API."""

    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.rebyte.ai"):
        self.api_key = api_key or os.environ.get("REBYTE_API_KEY")
        if not self.api_key:
            raise ValueError("REBYTE_API_KEY environment variable is not set")
        self.base_url = base_url.rstrip("/")

    def _request(self, method: str, path: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make an API request using only stdlib (no requests dependency)."""
        url = f"{self.base_url}{path}"
        if params:
            query = "&".join(f"{k}={v}" for k, v in params.items() if v is not None)
            if query:
                url = f"{url}?{query}"

        body = json.dumps(data).encode() if data else None
        req = urllib.request.Request(url, data=body, method=method)
        req.add_header("API_KEY", self.api_key)
        req.add_header("Content-Type", "application/json")

        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                if resp.status == 204:
                    return {}
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            try:
                resp_data = json.loads(e.read().decode())
            except Exception:
                resp_data = {"raw": e.reason}
            error_msg = resp_data.get("error", {}).get("message", str(resp_data))
            raise APIError(message=error_msg, status_code=e.code, response=resp_data)
        except urllib.error.URLError as e:
            raise APIError(f"Network error: {e.reason}")

    # ---- Tasks ----

    def create_task(
        self,
        prompt: str,
        executor: Optional[str] = None,
        model: Optional[str] = None,
        skills: Optional[List[str]] = None,
        github_url: Optional[str] = None,
        branch_name: Optional[str] = None,
        workspace_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new task. Blocks until the VM is ready and the first prompt is sent."""
        data: Dict[str, Any] = {"prompt": prompt}
        if executor:
            data["executor"] = executor
        if model:
            data["model"] = model
        if skills:
            data["skills"] = skills
        if github_url:
            data["githubUrl"] = github_url
        if branch_name:
            data["branchName"] = branch_name
        if workspace_id:
            data["workspaceId"] = workspace_id
        return self._request("POST", "/v1/tasks", data=data)

    def get_task(self, task_id: str) -> Dict[str, Any]:
        """Get task details with derived status and prompts."""
        return self._request("GET", f"/v1/tasks/{task_id}")

    def list_tasks(self, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """List API-created tasks."""
        return self._request("GET", "/v1/tasks", params={"limit": limit, "offset": offset})

    def delete_task(self, task_id: str) -> None:
        """Soft-delete a task."""
        self._request("DELETE", f"/v1/tasks/{task_id}")

    # ---- Follow-ups ----

    def follow_up(self, task_id: str, prompt: str, skills: Optional[List[str]] = None) -> Dict[str, Any]:
        """Send a follow-up prompt to an existing task."""
        data: Dict[str, Any] = {"prompt": prompt}
        if skills:
            data["skills"] = skills
        return self._request("POST", f"/v1/tasks/{task_id}/prompts", data=data)

    # ---- Polling ----

    def wait_for_task(self, task_id: str, timeout_seconds: int = 600, poll_interval: float = 3.0) -> Dict[str, Any]:
        """Poll until task reaches a terminal status."""
        start = time.time()
        while True:
            if time.time() - start > timeout_seconds:
                raise TimeoutError(f"Task {task_id} timed out after {timeout_seconds}s")

            result = self.get_task(task_id)
            status = result.get("status", "")

            if status in ("completed", "failed", "canceled"):
                return result

            time.sleep(poll_interval)
