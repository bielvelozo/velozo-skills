Skills are organized into bucket folders under `skills/`:

- `engineering/`: daily code work
- `productivity/`: daily non-code workflow tools
- `in-progress/`: beta, public on purpose, not shipped in the plugin
- `deprecated/`: no longer used

Every skill in `engineering/` or `productivity/` (the **promoted** buckets) must have an entry in the top-level `README.md` and an entry in the `skills` array of `.claude-plugin/plugin.json` (the Claude Code plugin ships exactly the promoted set). Skills in `in-progress/` and `deprecated/` appear in neither.

Each bucket folder has a `README.md` that lists every skill in the bucket with a one-line description, the skill name linked to its `SKILL.md`. The promoted buckets' `README.md`s and the top-level `README.md` group entries into **User-invoked** and **Model-invoked**; the other buckets use a flat list.

Each promoted skill also has a human-facing docs page at `docs/<bucket>/<skill>.md`, with the sections **What it does**, **When to reach for it**, **Common questions** and **It's working if**. When a promoted skill is added, renamed, or changes behaviour, create or re-sync its page.

Every `SKILL.md` is either user-invoked (`disable-model-invocation: true` in the frontmatter and `policy.allow_implicit_invocation: false` in `agents/openai.yaml`) or model-invoked (rich trigger phrasing in the description and `allow_implicit_invocation: true`).

`.claude-plugin/marketplace.json` is the repo's own marketplace. After touching either manifest, run `claude plugin validate . --strict`.

To (re)link every skill outside `deprecated/` into the local skill directories (`~/.claude/skills`, `~/.agents/skills`), run `scripts/link-skills.sh`. Each entry is a symlink into this repo; re-run the script after adding, removing, or renaming a skill.

Repo prose (README, docs, CLAUDE.md, CHANGELOG), skill arguments (`fast`, for example) and file names are in English. The text inside the skills themselves (`SKILL.md`, references, prompts) is in Portuguese.
