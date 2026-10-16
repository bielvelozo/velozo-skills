# Engineering

Skills for code work.

## User-invoked

Reachable only when you type them (Claude Code: `disable-model-invocation: true`; Codex: `policy.allow_implicit_invocation: false` in `agents/openai.yaml`).

None yet.

## Model-invoked

Model- or user-reachable (rich trigger phrasing so the model can reach for them).

- **[map](./map/SKILL.md)**: Draws and updates a living map of the project as an HTML page: the main parts and their status, what is blocked and on whom, the next milestone, the next step, what changed since last time, and the decisions waiting on you. Claude Code only (uses the `project-map` subagent).
- **[tech-walkthrough](./tech-walkthrough/SKILL.md)**: Explains the technical side of an already-decided plan on an Excalidraw board: before and after, glossary, architecture map, backstage, database diagram and migrations, performance and risks. Three agents debate the best implementation before anything is drawn. `fast` skips the debate.
