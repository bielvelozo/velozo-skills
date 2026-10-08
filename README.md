# Velozo Skills

Skills I use every day with coding agents (Claude Code, Codex and friends), straight from my skills directory.

They are small, easy to adapt, and composable with [Matt Pocock's skills](https://github.com/mattpocock/skills): I plan with `/grill-me` or `/grill-with-docs`, and once the business decisions are settled I use the skills here to see the technical side before implementing. Hack around with them. Make them your own.

## Installation

A plugin updates itself. [skills.sh](https://skills.sh/bielvelozo/velozo-skills) copies editable files into your project, and you update them by hand. Pick one per agent, because installing both gives you every skill twice.

### 1. Get the skills

<details>
<summary><strong>Claude Code</strong></summary>

```bash
claude plugin marketplace add bielvelozo/velozo-skills
```

```bash
claude plugin install velozo-skills@velozo
```

Updates itself.

</details>

<details>
<summary><strong>Codex</strong></summary>

```bash
codex plugin marketplace add bielvelozo/velozo-skills
```

```bash
codex plugin add velozo-skills@velozo
```

Updates itself at startup.

</details>

<details>
<summary><strong>Any other agent, or editable files</strong> (manual updates)</summary>

```bash
npx skills@latest add bielvelozo/velozo-skills -a <agent>  # cursor, opencode, windsurf, amp; omit -a to choose
```

To update, run `npx skills@latest update`.

</details>

<details>
<summary><strong>Cloning the repo</strong> (if you want to edit the skills)</summary>

```bash
git clone https://github.com/bielvelozo/velozo-skills.git && cd velozo-skills && scripts/link-skills.sh
```

Symlinks every skill into `~/.claude/skills` and `~/.agents/skills`; a `git pull` keeps them current.

</details>

### 2. Prerequisites

- **Python 3** on your PATH: `tech-walkthrough` builds the Excalidraw board with a script.
- Claude Code with the **Artifact** tool, to publish the board as a link. Without it, the skill delivers only the `.excalidraw` file.

### 3. Done.

## Why these skills exist

### The plan is clear, the implementation is not

**The problem.** A `/grill-me` session leaves the business decisions well defined. But the technical side (which route is born, which queue is reused, whether there is a migration and why, what runs in the background) ends up scattered across paragraphs, and I don't hold the whole codebase in my head to follow along.

**The fix.** One Excalidraw board, one infinite canvas, with the before and after of each flow, the map of the systems that talk to each other, the backstage (queues, workers, retries), the migration with its why, the performance verdict, and the risks that remain. Every piece of code is introduced by what it does, with the technical name after it. The implementation it explains comes out of a debate between three agents (minimal, robust, performance), not the first idea that works.

That's `/tech-walkthrough`.

## Reference

These split on one axis: who can invoke them. **User-invoked** skills run only when you type them. **Model-invoked** skills can be typed or reached for automatically by the agent when the task fits.

### Engineering

Skills for code work.

#### Model-invoked

- **[tech-walkthrough](./skills/engineering/tech-walkthrough/SKILL.md)**: Explains the technical side of an already-decided plan on an Excalidraw board: before and after, architecture map, backstage, migrations, performance and risks. Three agents debate the best implementation before anything is drawn. `fast` skips the debate.

The skill's own instructions (`SKILL.md`) are written in Portuguese; the agent reads them fine either way, and the board comes out in the language of your plan.

## License

MIT.
