---
name: agent-skills-creator
description: Guide for creating effective agent skills. Covers skill structure, YAML frontmatter, description writing, trigger patterns, and testing methodology. Use when creating new skills for Claude Code or other AI agents. 597 installs on skills.sh.
source: mblode/agent-skills
---

# Agent Skills Creator

A systematic guide to creating high-quality agent skills.

## Skill Structure

```
skill-name/
├── SKILL.md          # Main skill definition (required)
├── references/       # Supporting docs loaded on demand
│   ├── guide.md
│   └── examples.md
├── scripts/          # Executable helpers
│   └── helper.py
└── templates/        # File templates
    └── template.md
```

## SKILL.md Anatomy

### Required Frontmatter
```yaml
---
name: skill-name
description: One-line summary of what this skill does (used in skill picker)
---
```

### Recommended Frontmatter
```yaml
---
name: skill-name
description: What and when to use
triggers: keyword triggers for automatic invocation
args:
  - name: param
    description: Parameter description
    required: false
---
```

## Writing Guidelines

### Description (most critical)
- Start with a verb: "Create...", "Generate...", "Help..."
- Be specific about when to use: "Use when building X or working with Y"
- Keep under 60 chars if possible

### Triggers
- List keywords that should auto-trigger this skill
- Think about how users naturally phrase requests
- Include Chinese equivalents if targeting bilingual users

### Instructions
- Use imperative mood: "Do this", "Check that"
- Break into numbered steps or clear sections
- Reference sub-files with `references/` for deep content
- Keep main file lean; offload details to references

## Testing Your Skill

1. **Invoke directly** — Call with explicit skill name
2. **Trigger naturally** — Use trigger phrases in conversation
3. **Edge cases** — Test with unusual inputs
4. **Iterate** — Refine based on actual usage patterns

## Common Mistakes

1. Description too vague ("Helps with stuff")
2. No triggers defined (skill never auto-loads)
3. Too much content in SKILL.md (use references/)
4. Missing actionable output format
