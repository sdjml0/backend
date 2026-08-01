---
name: agent-skill-documentation
description: Guidelines and instructions for creating, documenting, and maintaining agent skills within this project workspace.
---

# Agent Skill Documentation

This skill provides guidelines and standards for creating, documenting, and managing AI agent skills in this repository.

## Overview

Agent skills are modular packages of instructions, workflows, and supporting resources that customize and extend the behavior of AI coding assistants working in this codebase.

## Folder Structure

Skills are stored in the workspace under the `.agents/skills/` directory:

```
.agents/
└── skills/
    └── <skill-name>/
        ├── SKILL.md           # Required: Main instructions with YAML frontmatter
        ├── scripts/           # Optional: Utility and automation scripts
        ├── examples/          # Optional: Reference implementations and usage patterns
        ├── resources/         # Optional: Configuration templates or static assets
        └── references/        # Optional: Detailed reference docs (for >500 line guides)
```

## Required `SKILL.md` Structure

Every skill MUST contain a `SKILL.md` file formatted with YAML frontmatter at the top:

```markdown
---
name: your-skill-name
description: Clear, actionable summary of when this skill should trigger and what it accomplishes.
---

# Skill Title

## Purpose & Scope
High-level explanation of what this skill enables.

## Instructions & Workflow
1. Step 1: Pre-execution checks.
2. Step 2: Implementation procedure.
3. Step 3: Verification steps.
```

## Rules & Best Practices

1. **Naming Conventions**: Use kebab-case for skill directory names and the `name` frontmatter property (e.g., `api-endpoint-generator`, `database-migration`).
2. **Actionable Frontmatter**: The `description` in the YAML frontmatter is used for automatic trigger matching. Keep it clear, descriptive, and focused on user intents.
3. **Length Management**: Keep `SKILL.md` concise (under 500 lines). If extensive background or API specs are needed, store them in `references/` and link to them.
4. **Auto-Discovery**: Skills placed in `.agents/skills/` are automatically discovered by the workspace agent framework.
