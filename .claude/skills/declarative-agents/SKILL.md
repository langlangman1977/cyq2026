---
name: declarative-agents
description: Build declarative, intent-driven agents for GitHub Copilot. Learn patterns for agent definition files, tool selection strategies, prompt engineering, and multi-agent orchestration. Use when building AI agents, defining agent behaviors, or structuring agent workflows. 8.6K installs on skills.sh.
source: github/awesome-copilot
---

# Declarative Agents

Build intent-driven AI agents using declarative definitions, not imperative code.

## Core Concepts

### Agent Definition
- **Intent-driven**: Declare what the agent should do, not how
- **Tool-aware**: Define available tools and when to use them
- **Context-rich**: Provide domain knowledge via structured prompts

### Key Patterns

1. **Agent File Structure** — YAML/JSON definition with name, description, tools, instructions
2. **Tool Selection** — Declare tool permissions and usage rules
3. **Prompt Engineering** — System prompts, task decomposition, output formatting
4. **Multi-Agent Design** — Orchestration patterns, message routing, context sharing

## When to Use

- Building a new AI agent or coding assistant
- Defining agent behavior and capabilities
- Structuring complex multi-step workflows
- Creating domain-specific coding agents
- Setting up team-based agent collaboration

## Agent Anatomy

```yaml
name: my-agent
description: What this agent does
tools:
  - read_file
  - write_file
  - search_code
instructions: |
  You are a specialized agent that...
  Follow these rules...
  Output format should be...
```

## Best Practices

1. **Be specific** — narrow scope beats broad capability
2. **Test iteratively** — start minimal, add complexity gradually
3. **Design for failure** — handle edge cases explicitly
4. **Document decisions** — why this agent exists and what it optimizes for
