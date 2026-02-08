# Skill as a Service Skill 🧠☁️

![Status](https://img.shields.io/badge/status-active-success.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Rebyte](https://img.shields.io/badge/platform-Rebyte.ai-purple)

> **The Meta-Skill:** Empower your AI agents to spawn, orchestrate, and utilize *other* specialized cloud agents.

## 📖 Overview

**Skill as a Service** is a foundational capability for the Rebyte ecosystem. It allows an AI agent (like Claude, Gemini, or a local script) to dynamically provision specialized "worker" agents in the cloud, each equipped with specific skills (e.g., PDF processing, data analysis, web scraping).

Instead of trying to be a "jack of all trades," your main agent can simply:
1.  **Search** the skill store for the right tool.
2.  **Spawn** a dedicated worker agent with that skill.
3.  **Delegate** the task.
4.  **Retrieve** the results.

## ✨ Features

- **🔎 Skill Discovery**: Search and list available skills from the managed Skill Store.
- **🚀 Agent Spawning**: Create ephemeral, specialized cloud agents on demand.
- **⚡ Remote Execution**: dispatch tasks to agents and await results asynchronously or synchronously.
- **🛠️ Full Lifecycle Management**: List, inspect, and terminate agents via API or CLI.

## 🚀 Quick Start

### Prerequisites

You need a Rebyte API key to orchestrate cloud agents.
[**Get your API Key**](https://rebyte.ai/settings/api-keys)

```bash
export SKILL_SERVICE_API_KEY="your_api_key_here"
```

### 🖥️ CLI Usage

This repository includes a powerful CLI for manual interaction or testing.

```bash
# 1. Search for skills (e.g., PDF related)
python3 scripts/skill_cli.py list-skills --search pdf

# 2. Spawn a specialized worker
python3 scripts/skill_cli.py spawn-agent --name "doc-bot" --skills "anthropics-pdf"

# 3. Delegate a task
python3 scripts/skill_cli.py run-task 
  --agent-id <AGENT_ID> 
  --task "Extract the summary from this contract" 
  --input '{"file_url": "https://example.com/contract.pdf"}'
```

### 🐍 Python SDK Usage

Integrate agent orchestration into your own Python applications.

```python
from scripts.skill_service import get_client

client = get_client()

# Spawn a worker with specific skills
worker = client.spawn_agent(
    agent_name="analyst-01",
    skills=["rebyteai-data-scraper", "anthropics-xlsx"]
)

# Run a complex task
result = client.run_task(
    agent_id=worker["agent_id"],
    task_description="Scrape the stock prices and save to Excel",
    input_data={"ticker": "AAPL"}
)

print(f"Task Result: {result['result']}")

# Cleanup
client.terminate_agent(worker["agent_id"])
```

## 📂 Repository Structure

- **`SKILL.md`**: The instruction file for AI agents. Defines how and when the LLM should use this skill.
- **`scripts/`**: Executable code for the skill.
    - `skill_service.py`: The core Python API client.
    - `skill_cli.py`: Command-line interface wrapper.
- **`references/`**: Detailed documentation for the LLM context.
    - `api.md`: Full API specification.
    - `examples.md`: Advanced usage patterns.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

*Powered by [Rebyte.ai](https://rebyte.ai)*
