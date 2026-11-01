---
name: update-memory
description: >-
  Read and update the project memory file. Use when the user asks to remember,
  forget, save to memory, update memory, add to memory, store in memory, or
  change MEMORY.md.
---

# Update memory

Persist durable facts in `.cursor/memory/MEMORY.md`. Do not store secrets, tokens, passwords, or one-off chat noise.

## File

Path (workspace-relative): `.cursor/memory/MEMORY.md`

If the file is missing, create it with this skeleton before writing facts:

```markdown
# Project memory

Last updated: YYYY-MM-DD

## Preferences

## User / environment

## Project

## Decisions

## Do not forget
```

## When to run

- User says remember, save this, put this in memory, update memory, forget, or similar.
- User corrects a stored fact.

Do **not** write memory unless the user asked to store or change it.

## Workflow

1. **Read** `.cursor/memory/MEMORY.md` first.
2. **Decide the edit**: add, replace, or delete. Prefer a single surgical change over rewriting the whole file.
3. **Keep structure.** Put items under the matching heading. Add a heading only if none fits.
4. **Deduplicate.** If a newer fact contradicts an old one, replace the old one; do not leave both.
5. **Be durable.** Store stable preferences, decisions, environment facts, and constraints. Skip temporary task status unless the user insists.
6. **Stamp** `Last updated:` with today's date (`YYYY-MM-DD`).
7. **Confirm** in the reply: what was added, changed, or removed. Quote the saved line(s). Do not dump the entire file unless asked.

## Edit rules

- Bullet facts: short, specific, present tense.
- One idea per bullet.
- Never invent facts the user did not state.
- Never delete unrelated sections.
- For "forget X", remove only X.

## Examples

User: `remember I prefer pytest`

Add under Preferences: `- Test runner: pytest`

User: `forget that I'm on the free plan`

Remove that bullet from User / environment; leave everything else.
