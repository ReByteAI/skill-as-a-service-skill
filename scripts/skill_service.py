"""
Skill as a Service API Client

Provides methods for:
- Listing and searching skills from a skill store
- Spawning cloud code agents with specialized skills
- Running tasks on deployed agents
- Managing agent lifecycle
"""

import os
import json
import time
import requests
from typing import Any, Dict, List, Optional
from dataclasses import dataclass


@dataclass
class Config:
    """Configuration for Skill Service API client."""
    api_key: str
    base_url: str = "https://api.rebyte.ai"

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        api_key = os.environ.get("SKILL_SERVICE_API_KEY")
        if not api_key:
            raise ValueError("SKILL_SERVICE_API_KEY environment variable is not set")
        return cls(
            api_key=api_key,
            base_url=os.environ.get("SKILL_SERVICE_BASE_URL", "https://api.rebyte.ai")
        )


class APIError(Exception):
    """Exception raised for API errors."""
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response: Optional[Dict] = None
    ):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(self.message)


class SkillServiceClient:
    """Client for interacting with the Skill as a Service API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        """
        Initialize the Skill Service API client.

        Args:
            api_key: API key. If not provided, loads from SKILL_SERVICE_API_KEY env var.
            base_url: Base URL for the API. Defaults to production API.
        """
        if api_key is None:
            config = Config.from_env()
            self.api_key = config.api_key
            self.base_url = config.base_url
        else:
            self.api_key = api_key
            self.base_url = base_url or "https://api.rebyte.ai"

        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "SkillServiceClient/1.0"
        })

    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make an API request."""
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"

        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=30
            )

            try:
                response_data = response.json()
            except json.JSONDecodeError:
                response_data = {"raw_response": response.text}

            if not response.ok:
                raise APIError(
                    message=response_data.get("message", response_data.get("error", "Unknown error")),
                    status_code=response.status_code,
                    response=response_data
                )

            return response_data

        except requests.exceptions.RequestException as e:
            raise APIError(f"Network error: {str(e)}")

    # ============ SKILLS ============

    def list_skills(
        self,
        search: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 20
    ) -> Dict[str, Any]:
        """List available skills from the skill store."""
        params = {"limit": limit}
        if search:
            params["search"] = search
        if category:
            params["category"] = category
        return self._request("GET", "/v1/skills", params=params)

    def get_skill_details(self, skill_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific skill."""
        return self._request("GET", f"/v1/skills/{skill_id}")

    # ============ AGENTS ============

    def spawn_agent(
        self,
        agent_name: str,
        skills: List[str],
        prompt: Optional[str] = None,
        max_iterations: int = 100
    ) -> Dict[str, Any]:
        """Spawn a cloud code agent with specified skills."""
        data = {
            "name": agent_name,
            "skills": skills,
            "max_iterations": max_iterations
        }
        if prompt:
            data["prompt"] = prompt
        return self._request("POST", "/v1/agents", data=data)

    def list_agents(
        self,
        status: Optional[str] = None,
        limit: int = 20
    ) -> Dict[str, Any]:
        """List all deployed cloud agents."""
        params = {"limit": limit}
        if status:
            params["status"] = status
        return self._request("GET", "/v1/agents", params=params)

    def get_agent_info(self, agent_id: str) -> Dict[str, Any]:
        """Get information about a deployed agent."""
        return self._request("GET", f"/v1/agents/{agent_id}")

    def terminate_agent(self, agent_id: str) -> Dict[str, Any]:
        """Terminate a running cloud agent."""
        return self._request("DELETE", f"/v1/agents/{agent_id}")

    # ============ TASKS ============

    def run_task(
        self,
        agent_id: str,
        task_description: str,
        input_data: Optional[Dict] = None,
        wait_for_completion: bool = True,
        timeout_seconds: int = 300
    ) -> Dict[str, Any]:
        """Run a task on a cloud agent."""
        data = {
            "description": task_description,
            "input": input_data or {}
        }

        response = self._request("POST", f"/v1/agents/{agent_id}/tasks", data=data)

        if wait_for_completion:
            task_id = response.get("task_id") or response.get("id")
            return self.wait_for_task(task_id, timeout_seconds)

        return response

    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get the status of a running task."""
        return self._request("GET", f"/v1/tasks/{task_id}")

    def wait_for_task(
        self,
        task_id: str,
        timeout_seconds: int = 300,
        poll_interval: float = 2.0
    ) -> Dict[str, Any]:
        """Wait for a task to complete."""
        start_time = time.time()

        while True:
            if time.time() - start_time > timeout_seconds:
                raise APIError(f"Task {task_id} timed out after {timeout_seconds}s")

            status = self.get_task_status(task_id)
            task_status = status.get("status", "").lower()

            if task_status in ("completed", "success", "done"):
                return status
            elif task_status in ("failed", "error", "cancelled"):
                error_msg = status.get("error", status.get("message", "Task failed"))
                raise APIError(f"Task {task_id} failed: {error_msg}")

            time.sleep(poll_interval)

    def cancel_task(self, task_id: str) -> Dict[str, Any]:
        """Cancel a running task."""
        return self._request("POST", f"/v1/tasks/{task_id}/cancel")


# Convenience functions

def get_client() -> SkillServiceClient:
    """Get an initialized Skill Service API client."""
    return SkillServiceClient()


def list_skills(search: str = None, category: str = None, limit: int = 20) -> Dict[str, Any]:
    """List available skills from the skill store."""
    client = get_client()
    return client.list_skills(search=search, category=category, limit=limit)


def spawn_agent(
    agent_name: str,
    skills: List[str],
    prompt: str = None,
    max_iterations: int = 100
) -> Dict[str, Any]:
    """Spawn a cloud code agent with specified skills."""
    client = get_client()
    return client.spawn_agent(
        agent_name=agent_name,
        skills=skills,
        prompt=prompt,
        max_iterations=max_iterations
    )


def run_task(
    agent_id: str,
    task_description: str,
    input_data: Dict = None,
    wait_for_completion: bool = True,
    timeout_seconds: int = 300
) -> Dict[str, Any]:
    """Run a task on a cloud agent."""
    client = get_client()
    return client.run_task(
        agent_id=agent_id,
        task_description=task_description,
        input_data=input_data,
        wait_for_completion=wait_for_completion,
        timeout_seconds=timeout_seconds
    )
