# velozo-skills

## Unreleased

- Adds the `leaks` mod (`plugins/leaks`, installed as `leaks@velozo`): a fork of davekiss/mods leaks with a desktop-app fallback for "compact now" and a new `/compact-at` command for a per-session auto-compact point.

## 0.2.0

- Adds `map`: draws and updates a living map of the project as an HTML page in `.project-map/` (parts and status, blockers, next milestone and step, what changed, pending decisions), drawn by the new `project-map` subagent in `agents/`.
- `scripts/link-skills.sh` also links the subagents in `agents/` into `~/.claude/agents`.

## 0.1.0

- First release. Adds `tech-walkthrough`: explains the technical side of a plan on an Excalidraw board (before and after, glossary, architecture map, backstage, database diagram and migrations, performance, risks), with a three-agent debate before drawing and a `fast` mode.
