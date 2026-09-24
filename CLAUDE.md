# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A reusable Roblox + Rojo starter template (Luau). The project is intentionally still named `template-game`; it is not a finished game. See README.md for the full setup walkthrough.

## Commands

- Install toolchain (Rojo, pinned in `aftman.toml`): `aftman install`
- Install the Rojo Studio plugin: `rojo plugin install`
- Start the sync server (must stay running while editing so changes push into Studio): `rojo serve` (default port 34872)
- Lint Luau (`selene.toml` sets `std = "roblox"`): `selene src`
- Rename the template for a new project (updates `name` in `default.project.json` and replaces `template-game` in README.md): `./scripts/rename-template.ps1 -ProjectName "YourGameName"` — with no `-ProjectName`, it infers the name from the git remote or folder name.

There is no build step or automated test suite. Verifying behavior means: run `rojo serve`, connect Roblox Studio to it via the Rojo plugin, press Play, and check the Output window.

## Architecture

`default.project.json` is the Rojo sync map and is the source of truth for how `src/` becomes the Roblox DataModel:

- `src/client` → `StarterPlayer.StarterPlayerScripts`
- `src/server` → `ServerScriptService`
- `src/shared` → `ReplicatedStorage`

Within each mapped folder, `init.client.luau` / `init.server.luau` at the folder root becomes the script for that Roblox instance itself (Rojo convention); any subfolder becomes a nested child Instance under it. For example, `src/server/ServerScriptService/GameManager.luau` syncs into `ServerScriptService.ServerScriptService.GameManager`.

Claude Code can inspect and interact with a running Roblox Studio session through the `Roblox_Studio` MCP server defined in `.mcp.json` (checked into the repo, so it works for any clone). This requires Roblox Studio to be open; on first load Claude Code will prompt to trust the project's `.mcp.json`. The `blender` MCP server in the same file lets Claude inspect Blender when it is open with the MCP addon connected.

## AI roles

Each AI answers a different question. The human owner makes every final decision.

| Who | Answers | Does |
| --- | --- | --- |
| **Owner (human)** | "Is this worth building?" | Creative direction, playtesting, feedback, approving systems, deciding what gets built next and when to release. |
| **ChatGPT (chat)** | "What should we build and why?" | Game design, mechanics, progression, balance tables, content names, player-experience questions, marketing ideas. Produces designs, not code. |
| **Codex (ChatGPT Codex CLI)** | "Build this spec." | Writes **big code changes** (new systems, multi-file milestones) from a spec Claude writes. Builds **3D models, rigs, and animations in Blender** through the Blender MCP. Never decides design or architecture. |
| **Claude (Claude Code)** | "How should we technically build it?" | Architecture and technical plans, specs for Codex, **reviewing and fixing** Codex's work, **small code fixes directly** (a few lines up to a couple of files), debugging, Studio setup and testing through the Roblox Studio MCP, docs, and git. |
| **Roblox Studio AI** | "How can we quickly change this in Studio?" | Environment and map building (terrain, scenery, layout), quick property edits, simple objects. |

### Claude and Codex split

- **Big code change** → Claude writes a spec → Codex implements → Claude reviews the diff, fixes problems, runs `rojo build`, and playtests through the Studio MCP.
- **Small fix** → Claude makes it directly. A spec and review round trip costs about as much as the fix.
- **3D model or animation** → Claude writes a Blender brief → Codex builds it in Blender → Claude checks the report and exports → the owner imports into Studio → Claude places it, fixes pivots, and wires it into code.
- **Map and scenery** → the owner uses Roblox Studio AI. Claude only documents the named anchors code depends on and may make small placeholder tweaks when a feature needs them.
- Pick the Codex model per run with `-m` (use the cheaper default unless the owner asks for a stronger one). How to run Codex: [docs/codex-workflow.md](docs/codex-workflow.md).

### Handoff process

Design (ChatGPT) → technical plan (Claude) → build (Codex or Claude) → review and test (Claude) → playtest (owner) → feedback (owner + ChatGPT) → repeat.

## Development phases

Track work as NOW / NEXT / FUTURE. Only NOW gets significant development time. Ideas go to NEXT or FUTURE unless the owner moves them. The master design describes the destination; the current phase decides what gets built.

- **NOW:** _(current phase and its checklist)_
- **NEXT:** _(what gets built if NOW succeeds)_
- **FUTURE:** _(ideas, not commitments)_

Before building anything, ask: Does it make the core loop more fun? Improve retention or clarity? Is it necessary right now? If not, wait.

Check off a task only after it is verified, and say when Studio testing is still pending.

## Project conventions

- **Server authority:** the server decides ownership, rewards, currency, and outcomes. The client only displays and requests; validate every remote.
- **Modular code:** one service or controller per system; no giant scripts. Only build the modules the current phase needs.
- **Assets:** code depends only on documented anchors (a named part or attribute), never on how a model looks, so swapping in custom assets never breaks gameplay. Track every asset in [docs/asset-checklist.md](docs/asset-checklist.md) and every animation ID in [docs/animations.md](docs/animations.md).
- **Workspace.StreamingEnabled:** if it is on, client code must look up map objects lazily.
- **Game design** lives in [docs/game-design.md](docs/game-design.md).
