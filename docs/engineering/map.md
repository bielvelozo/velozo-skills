## What it does

`map` draws a living map of the project you are in: a single self-contained HTML page in `.project-map/` that opens with a double click. At the top, always: the next milestone and how much is left to reach it, the suggested next step, what changed since the last update, and the decisions that need you, each with a suggested default. Below that, the project split into a few main parts (4 to 8), each marked done, in progress, not started or blocked; a blocked part says what it is waiting on and from whom.

The drawing is done by a subagent, `project-map`, that only reads the project (code, `git log`, planning docs, issues and PRs) and writes only inside `.project-map/`. Next to the page it keeps `.project-map/estado.json`, a structured snapshot used to compare against on the next update. Status comes from evidence: when it is not sure, it says "não confirmado" instead of inventing progress.

## When to reach for it

Type `/map`, or say "desenha o mapa", "atualiza o mapa" or "onde estamos?".

| Situation | What to do |
|---|---|
| First time in a project, or you lost track of where it stands | `/map`: draws the map from scratch and proposes milestones if there are none |
| You just finished a chunk of work | `/map`: updates the map with what was done in the session and highlights what changed |
| You only want to know the current state | "onde estamos?": answers from `estado.json`, with its date, and offers an update if there are newer commits |

## Prerequisites

- Claude Code: the map is drawn by the `project-map` subagent, which ships in this plugin's `agents/` folder. Other agents get the skill but not the subagent.
- The subagent lists the `impeccable` skill to polish the page; install it, or remove the `skills:` entry from `agents/project-map.md`.

## Common questions

**Where does the map live? Does it go into git?**
In `.project-map/` at the project root. The skill adds that folder to the `.gitignore` when the project is a git repository, without committing just for that.

**Can I change the look?**
Yes. The first time, the skill asks for a theme (light or dark) and an accent colour and saves them in the subagent's memory (`~/.claude/agent-memory/project-map/MEMORY.md`). Every project after that uses the same style. Edit that file to change it.

**The milestones are wrong.**
When a project has no milestones, the subagent proposes a first version marked "proposta — edite". Tell the agent the right ones and run `/map` again; milestones you defined are passed along on every update.

**I installed it as a plugin and the subagent is not found, or the style is not remembered.**
Plugin subagents can be registered under a namespaced name (for example `velozo-skills:project-map`), and their memory folder may follow that name. The skill calls `project-map` and reads `~/.claude/agent-memory/project-map/`, which is what a clone linked with `scripts/link-skills.sh` gives you. If your install differs, point the skill at the name and path your Claude Code shows.

## It's working if

- You open `.project-map/index.html` and know the next step in a few seconds, without reading the code.
- Every part's status points to something you can check (a file, a commit, a doc), and the doubtful ones say "não confirmado".
- After a work session, the "what changed" block shows exactly what you did.
- The decisions waiting on you are on the map, each with a default you can just accept.
