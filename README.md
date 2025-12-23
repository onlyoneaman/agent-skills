# Agent Skills

A minimal implementation of [agent skills](https://agentskills.io) - a lightweight, open format for extending AI agents with specialized capabilities.

## What Are Agent Skills?

Agent skills are markdown files (`SKILL.md`) that give AI agents specialized knowledge and workflows. Each skill contains:

- **YAML frontmatter**: Name, description, metadata
- **Markdown instructions**: Detailed guidelines for the agent

When a user's task matches a skill, the agent automatically activates it to provide expert assistance.

## Quick Start

```bash
# Install
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Add your OPENAI_API_KEY to .env

# Run
python -m agent.chat
```

Or use the run script:
```bash
./run.sh
```

## Included Skills

- **code-review**: Reviews code for bugs, security issues, and best practices
- **git-helper**: Git workflows, commit messages, and troubleshooting
- **file-organizer**: Intelligent file organization strategies
- **api-tester**: Makes actual HTTP requests to APIs and analyzes responses (GET, POST, PUT, PATCH, DELETE)

## How It Works

1. **Discovery**: Scans `skills/` directory for `SKILL.md` files
2. **Loading**: Parses YAML frontmatter (name, description)
3. **Activation**: When user's task matches, loads full skill instructions
4. **Execution**: Agent follows skill guidelines to complete task

## Creating Your Own Skill

```bash
mkdir -p skills/my-skill
```

Create `skills/my-skill/SKILL.md`:

```markdown
---
name: my-skill
description: What this skill does
version: 1.0.0
---

# My Skill

You are an expert at [skill domain].

## Guidelines

1. Step one
2. Step two
3. Step three

## Examples

Show examples of using this skill effectively.
```

That's it! The skill will be automatically discovered.

## Project Structure

```
agent-skills/
├── agent/
│   ├── skills_manager.py    # Skill discovery & loading
│   ├── llm_client.py         # OpenAI client
│   ├── chat.py               # Terminal interface
│   └── code_executor.py      # Code execution for skills
├── skills/                   # Skills directory
│   ├── code-review/
│   ├── git-helper/
│   ├── file-organizer/
│   └── api-tester/
├── requirements.txt
└── run.sh
```

## Resources

- **[AgentSkills.io](https://agentskills.io)** - Official standard and documentation
- **[Claude Skills](https://github.com/anthropics/claude-skills)** - Anthropic's skill examples
- **[Open Agent Skills](https://github.com/samuelint/open-agent-skills)** - Community skill collection

## Learn More

**Tutorial**: [Building Agent Skills from Scratch](https://amankumar.ai/blogs/implementing-agent-skills) - Detailed guide on how this implementation works

**Repository**: [github.com/onlyoneaman/agent-skills](https://github.com/onlyoneaman/agent-skills)

## License

MIT
