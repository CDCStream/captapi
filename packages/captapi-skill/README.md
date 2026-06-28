# Captapi Agent Skill

An [Agent Skill](https://docs.claude.com/en/docs/agents-and-tools/agent-skills) that teaches AI coding agents how to use the **Captapi** API — endpoint selection, parameters, credit costs, and platform gotchas for YouTube, TikTok, Instagram, Facebook, X (Twitter), Reddit, Threads, Bluesky, Pinterest, LinkedIn, and Rumble.

The skill complements the MCP server: the MCP server gives the agent **access** to the API; this skill teaches it **how to use it well** (which endpoint to pick, how to handle params/pagination/credits, what the errors mean). Use either or both.

## Install

```bash
npx skills add captapi/agent-skills
```

Works with Claude Code, Cursor, Codex, GitHub Copilot, Gemini CLI, Windsurf, and other agents that support the Agent Skills format. Or download `SKILL.md` and add it to your agent manually.

## What it covers

- Step 0: getting the API key (the agent asks the human — sign-up can't be automated).
- How to call Captapi over REST or via the MCP tools.
- Endpoint selection guidance per platform.
- Parameter rules (`url`, `q`, `limit`, `language`, `comment_id`) and gotchas.
- Credits, caching, and error handling (401/402/422/429).
- A full table of all 180 endpoints (tool name, REST path, params, credits).

## Publishing

`npx skills add captapi/agent-skills` reads `SKILL.md` from the **root** of the public GitHub repo `captapi/agent-skills`. To publish:

1. Create a public repo `captapi/agent-skills` on GitHub.
2. Copy `SKILL.md` (and this `README.md`) to its root and push.

## Regenerating SKILL.md

`SKILL.md` is generated from the shared endpoint catalog so it never drifts from the API/MCP server. After changing `packages/captapi-mcp/src/catalog.ts`:

```bash
cd packages/captapi-mcp && npm run build   # refresh dist/
cd ../captapi-skill && node generate.mjs    # rewrite SKILL.md
```

Do not edit `SKILL.md` by hand.
