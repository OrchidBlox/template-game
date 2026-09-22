# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A reusable Roblox + Rojo starter template (Luau). The project is intentionally still named `template-game`; it is not a finished game. See README.md for the full setup walkthrough.

## Commands

- Install toolchain (Rojo, pinned in `aftman.toml`): `aftman install`
- Install the Rojo Studio plugin: `rojo plugin install`
- Start the sync server (must stay running while editing so changes push into Studio): `rojo serve`
- Lint Luau (`selene.toml` sets `std = "roblox"`): `selene src`
- Rename the template for a new project (updates `name` in `default.project.json` and replaces `template-game` in README.md): `./scripts/rename-template.ps1 -ProjectName "YourGameName"` — with no `-ProjectName`, it infers the name from the git remote or folder name.

There is no build step or automated test suite. Verifying behavior means: run `rojo serve`, connect Roblox Studio to it via the Rojo plugin, press Play, and check the Output window.

## Architecture

`default.project.json` is the Rojo sync map and is the source of truth for how `src/` becomes the Roblox DataModel:

- `src/client` → `StarterPlayer.StarterPlayerScripts`
- `src/server` → `ServerScriptService`
- `src/shared` → `ReplicatedStorage`

Within each mapped folder, `init.client.luau` / `init.server.luau` at the folder root becomes the script for that Roblox instance itself (Rojo convention); any subfolder becomes a nested child Instance under it. For example, `src/server/ServerScriptService/GameManager.luau` syncs into `ServerScriptService.ServerScriptService.GameManager`.

Claude Code can inspect and interact with a running Roblox Studio session through the `Roblox_Studio` MCP server defined in `.mcp.json` (checked into the repo, so it works for any clone). This requires Roblox Studio to be open and connected via Rojo; on first load Claude Code will prompt to trust the project's `.mcp.json`.
