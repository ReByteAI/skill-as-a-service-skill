#!/usr/bin/env python3
"""Rebyte API client -- stdlib only (no requests dependency)."""

import json
import os
import time
import urllib.request
import urllib.error
from typing import Any, Dict, List, Optional


class APIError(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(f"HTTP {status_code}: {message}")


class RebyteClient:
    """Minimal client for the Rebyte v1 API."""

    BASE_URL = "https://api.rebyte.ai/v1"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("REBYTE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key required. Set REBYTE_API_KEY env var or pass api_key="
            )

    # ── helpers ──────────────────────────────────────────────

    def _request(
        self,
        method: str,
        path: str,
        body: Optional[dict] = None,
        params: Optional[dict] = None,
    ) -> Any:
        url = f"{self.BASE_URL}{path}"
        if params:
            qs = "&".join(f"{k}={v}" for k, v in params.items() if v is not None)
            if qs:
                url = f"{url}?{qs}"

        data = json.dumps(body).encode() if body else None
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("API_KEY", self.api_key)
        if body:
            req.add_header("Content-Type", "application/json")

        try:
            with urllib.request.urlopen(req) as resp:
                if resp.status == 204:
                    return None
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            body_text = e.read().decode() if e.fp else ""
            try:
                err = json.loads(body_text)
                msg = err.get("error", {}).get("message", body_text)
            except json.JSONDecodeError:
                msg = body_text
            raise APIError(e.code, msg)

    # ── public API ───────────────────────────────────────────

    def upload_file(
        self,
        file_path: str,
        *,
        content_type: str = "application/octet-stream",
    ) -> Dict[str, str]:
        """Upload a file for use in tasks.

        Returns {"id": "...", "filename": "..."} ready to pass to create_task(files=...).
        """
        filename = os.path.basename(file_path)

        # 1. Get signed upload URL
        resp = self._request(
            "POST",
            "/files",
            body={"filename": filename, "contentType": content_type},
        )

        # 2. Upload file content to signed URL
        with open(file_path, "rb") as f:
            file_data = f.read()

        upload_req = urllib.request.Request(
            resp["uploadUrl"], data=file_data, method="PUT"
        )
        upload_req.add_header("Content-Type", content_type)
        urllib.request.urlopen(upload_req)

        return {"id": resp["id"], "filename": resp["filename"]}

    def create_task(
        self,
        prompt: str,
        *,
        executor: Optional[str] = None,
        model: Optional[str] = None,
        skills: Optional[List[str]] = None,
        files: Optional[List[Dict[str, str]]] = None,
        github_url: Optional[str] = None,
        branch_name: Optional[str] = None,
        workspace_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a task. Blocks until running.

        files: list of {"id": "...", "filename": "..."} from upload_file().
        """
        body: Dict[str, Any] = {"prompt": prompt}
        if executor:
            body["executor"] = executor
        if model:
            body["model"] = model
        if skills:
            body["skills"] = skills
        if files:
            body["files"] = files
        if github_url:
            body["githubUrl"] = github_url
        if branch_name:
            body["branchName"] = branch_name
        if workspace_id:
            body["workspaceId"] = workspace_id
        return self._request("POST", "/tasks", body=body)

    def get_task(self, task_id: str) -> Dict[str, Any]:
        """Get task with derived status and prompts."""
        return self._request("GET", f"/tasks/{task_id}")

    def list_tasks(
        self, *, limit: int = 50, offset: int = 0
    ) -> Dict[str, Any]:
        """List API-created tasks."""
        return self._request(
            "GET", "/tasks", params={"limit": limit, "offset": offset}
        )

    def follow_up(
        self,
        task_id: str,
        prompt: str,
        *,
        skills: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Send a follow-up prompt."""
        body: Dict[str, Any] = {"prompt": prompt}
        if skills:
            body["skills"] = skills
        return self._request("POST", f"/tasks/{task_id}/prompts", body=body)

    def set_visibility(
        self, task_id: str, visibility: str
    ) -> Dict[str, Any]:
        """Change task visibility. Returns shareUrl when set to 'public'."""
        return self._request(
            "PATCH",
            f"/tasks/{task_id}/visibility",
            body={"visibility": visibility},
        )

    def delete_task(self, task_id: str) -> None:
        """Soft-delete a task."""
        self._request("DELETE", f"/tasks/{task_id}")

    def wait_for_task(
        self,
        task_id: str,
        *,
        poll_interval: float = 5.0,
        timeout_seconds: float = 600.0,
    ) -> Dict[str, Any]:
        """Poll until task reaches a terminal state."""
        deadline = time.time() + timeout_seconds
        while time.time() < deadline:
            task = self.get_task(task_id)
            if task["status"] in ("completed", "failed", "canceled"):
                return task
            time.sleep(poll_interval)
        raise TimeoutError(
            f"Task {task_id} did not complete within {timeout_seconds}s"
        )
