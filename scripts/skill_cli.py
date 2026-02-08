#!/usr/bin/env python3
"""
CLI for Skill as a Service.

Usage:
  python3 scripts/skill_cli.py list-skills [--search SEARCH] [--category CATEGORY]
  python3 scripts/skill_cli.py spawn-agent --name NAME --skills SKILLS... [--prompt PROMPT]
  python3 scripts/skill_cli.py run-task --agent-id AGENT_ID --task TASK [--input INPUT_JSON]
  python3 scripts/skill_cli.py list-agents [--status STATUS]
  python3 scripts/skill_cli.py terminate-agent --agent-id AGENT_ID
"""

import sys
import json
import argparse
from scripts.skill_service import SkillServiceClient, APIError


def main():
    parser = argparse.ArgumentParser(description="Skill as a Service CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # List Skills
    list_skills_parser = subparsers.add_parser("list-skills", help="List available skills")
    list_skills_parser.add_argument("--search", help="Search keyword")
    list_skills_parser.add_argument("--category", help="Filter by category")

    # Spawn Agent
    spawn_parser = subparsers.add_parser("spawn-agent", help="Spawn a cloud agent")
    spawn_parser.add_argument("--name", required=True, help="Agent name")
    spawn_parser.add_argument("--skills", required=True, nargs="+", help="List of skills")
    spawn_parser.add_argument("--prompt", help="Initial prompt for the agent")

    # Run Task
    run_parser = subparsers.add_parser("run-task", help="Run a task on an agent")
    run_parser.add_argument("--agent-id", required=True, help="Agent ID")
    run_parser.add_argument("--task", required=True, help="Task description")
    run_parser.add_argument("--input", help="Input data as JSON string")

    # List Agents
    list_agents_parser = subparsers.add_parser("list-agents", help="List all agents")
    list_agents_parser.add_argument("--status", help="Filter by status")

    # Terminate Agent
    terminate_parser = subparsers.add_parser("terminate-agent", help="Terminate an agent")
    terminate_parser.add_argument("--agent-id", required=True, help="Agent ID")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        client = SkillServiceClient()
        
        if args.command == "list-skills":
            result = client.list_skills(search=args.search, category=args.category)
            print(json.dumps(result, indent=2))
        
        elif args.command == "spawn-agent":
            result = client.spawn_agent(agent_name=args.name, skills=args.skills, prompt=args.prompt)
            print(f"Agent spawned successfully. Agent ID: {result.get('agent_id')}")
            print(json.dumps(result, indent=2))
            
        elif args.command == "run-task":
            input_data = json.loads(args.input) if args.input else None
            result = client.run_task(agent_id=args.agent_id, task_description=args.task, input_data=input_data)
            print(f"Task completed. Status: {result.get('status')}")
            print(json.dumps(result, indent=2))
            
        elif args.command == "list-agents":
            result = client.list_agents(status=args.status)
            print(json.dumps(result, indent=2))
            
        elif args.command == "terminate-agent":
            result = client.terminate_agent(agent_id=args.agent_id)
            print(f"Agent {args.agent_id} terminated: {result.get('success', True)}")

    except APIError as e:
        print(f"API Error: {e.message}", file=sys.stderr)
        if e.status_code:
            print(f"Status Code: {e.status_code}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError:
        print("Error: Input must be a valid JSON string", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
