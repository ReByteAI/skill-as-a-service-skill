#!/usr/bin/env python3
"""
Rebyte CLI - Command-line interface for the Rebyte v1 API.

Usage:
  python3 scripts/rebyte_cli.py create --prompt "..." [--skills skill1 skill2] [--executor opencode]
  python3 scripts/rebyte_cli.py get TASK_ID
  python3 scripts/rebyte_cli.py follow-up TASK_ID --prompt "..."
  python3 scripts/rebyte_cli.py list [--limit 50]
  python3 scripts/rebyte_cli.py delete TASK_ID
"""

import sys
import json
import argparse
from rebyte_client import RebyteClient, APIError


def main():
    parser = argparse.ArgumentParser(description="Rebyte CLI")
    sub = parser.add_subparsers(dest="command")

    # create
    p_create = sub.add_parser("create", help="Create a new task")
    p_create.add_argument("--prompt", required=True, help="Task prompt")
    p_create.add_argument("--executor", help="Executor (opencode, claude, gemini, codex)")
    p_create.add_argument("--model", help="Model tier")
    p_create.add_argument("--skills", nargs="+", help="Skill slugs")
    p_create.add_argument("--github-url", help="GitHub repo (owner/repo)")
    p_create.add_argument("--branch", help="Branch name")
    p_create.add_argument("--wait", action="store_true", help="Wait for completion")

    # get
    p_get = sub.add_parser("get", help="Get task details")
    p_get.add_argument("task_id", help="Task ID")

    # follow-up
    p_follow = sub.add_parser("follow-up", help="Send follow-up prompt")
    p_follow.add_argument("task_id", help="Task ID")
    p_follow.add_argument("--prompt", required=True, help="Follow-up prompt")
    p_follow.add_argument("--skills", nargs="+", help="Skill slugs")

    # list
    p_list = sub.add_parser("list", help="List tasks")
    p_list.add_argument("--limit", type=int, default=50, help="Max results")
    p_list.add_argument("--offset", type=int, default=0, help="Offset")

    # delete
    p_delete = sub.add_parser("delete", help="Delete a task")
    p_delete.add_argument("task_id", help="Task ID")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    try:
        client = RebyteClient()

        if args.command == "create":
            task = client.create_task(
                prompt=args.prompt,
                executor=args.executor,
                model=args.model,
                skills=args.skills,
                github_url=args.github_url,
                branch_name=args.branch,
            )
            print(json.dumps(task, indent=2))
            if args.wait:
                print("Waiting for completion...")
                result = client.wait_for_task(task["id"])
                print(json.dumps(result, indent=2))

        elif args.command == "get":
            result = client.get_task(args.task_id)
            print(json.dumps(result, indent=2))

        elif args.command == "follow-up":
            result = client.follow_up(args.task_id, prompt=args.prompt, skills=args.skills)
            print(json.dumps(result, indent=2))

        elif args.command == "list":
            result = client.list_tasks(limit=args.limit, offset=args.offset)
            print(json.dumps(result, indent=2))

        elif args.command == "delete":
            client.delete_task(args.task_id)
            print(f"Task {args.task_id} deleted.")

    except APIError as e:
        print(f"API Error: {e.message}", file=sys.stderr)
        if e.status_code:
            print(f"HTTP {e.status_code}", file=sys.stderr)
        sys.exit(1)
    except TimeoutError as e:
        print(f"Timeout: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
