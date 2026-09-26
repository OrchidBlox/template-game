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

- `src/client` → `StarterPlayer.StarterPlayerScripts.Client`
- `src/server` → `ServerScriptService.Server`
- `src/shared` → `ReplicatedStorage.Shared`

Each maps to a child folder, not the service itself, so Rojo never removes things built in Studio (for example `ReplicatedStorage.Assets`). `init.server.luau` / `init.client.luau` become the `Server` / `Client` scripts; their subfolders become children.

- **Server:** `init.server.luau` requires each module in `Services/` in `SERVICE_ORDER`, calls every `Init()` (setup only, no calls into other services), then every `Start()` (connect events, begin work). One service per system.
- **Client:** `init.client.luau` starts each module in `Controllers/` in `CONTROLLER_ORDER`. Controllers display state and send requests only.
- **Remotes:** `src/shared/Remotes.luau` names every RemoteEvent and documents its payload. The server creates them; clients wait for them.
- **Saving:** there is no DataService yet on purpose. When a game needs saving, port the tested one from Grow & Battle (`src/server/Services/DataService.luau` in grow-a-seed-fighter: session locking, data repair, versioned migrations, save on leave and shutdown) in that game's first milestone, and playtest it there, rather than writing saving code from scratch.

Claude Code can inspect and interact with a running Roblox Studio session through the `Roblox_Studio` MCP server defined in `.mcp.json` (checked into the repo, so it works for any clone). This requires Roblox Studio to be open; on first load Claude Code will prompt to trust the project's `.mcp.json`. The `blender` MCP server in the same file lets Claude inspect Blender when it is open with the MCP addon connected.

## AI roles

Each AI answers a different question. The human owner makes every final decision.

| Who | Answers | Does |
| --- | --- | --- |
| **Owner (human)** | "Is this worth building?" | Creative direction, playtesting, feedback, approving systems, deciding what gets built next and when to release. |
| **ChatGPT (chat)** | "What should we build and why?" | Game design, mechanics, progression, balance tables, content names, player-experience questions, marketing ideas. Produces designs, not code. |
| **Codex (ChatGPT Codex CLI)** | "Build this spec." | Writes **big code changes** (new systems, multi-file milestones) from a spec Claude writes. Builds **3D models, rigs, and animations in Blender** through the Blender MCP. Never decides design or architecture. |
| **Claude (Claude Code)** | "How should we technically build it?" | Architecture and technical plans, specs for Codex, **reviewing and fixing** Codex's work, **small code fixes directly** (a few lines up to a couple of files), debugging, Studio setup and testing through the Roblox Studio MCP, docs, and git. |
| **Roblox AI generators / Studio AI** | "How can we quickly make this in Studio?" | Generating map props from short prompts (Claude or Codex call the generator through the Studio MCP and place the props with a script), quick property edits, simple objects. |

### Claude and Codex split

- **Big code change** → Claude writes a spec → Codex implements → Claude reviews the diff, fixes problems, runs `rojo build`, and playtests through the Studio MCP.
- **Small fix** → Claude makes it directly. A spec and review round trip costs about as much as the fix.
- **3D model or animation** → Claude writes a Blender brief → Codex builds it in Blender → Claude checks the report and exports → Claude uploads through Open Cloud, places the model, converts and uploads its animations, and wires them into code ([docs/asset-pipeline.md](docs/asset-pipeline.md)). A manual Import 3D by the owner is the fallback.
- **Map and scenery** → Roblox's AI generators make the props and Claude or Codex place them with one script per area, following [docs/ai-map-building-workflow.md](docs/ai-map-building-workflow.md). Never move or delete the named anchors code depends on; the owner reviews each area.
- **Use Roblox Cube 3D for props (owner's choice, it gives a much cleaner look).** Generate detailed props with the Studio MCP's `generate_mesh` tool (Cube 3D): torii gates, lanterns, fences, rocks, signs, statues. Prompt for a "stylized low-poly cartoon game prop, clean chunky shapes, bright simple colours", pass a `size` that matches the object it replaces, `segmentation: "none"` and a modest `maxTriangles` (about 800 for repeated pieces like fence sections, 4000 for one-offs). Show the owner one test piece next to the old one first; then swap every copy in one ChangeHistoryService recording, keeping each object's name and attributes, and move the old ones to `ServerStorage.PolishOld` so it can be undone. Keep a master copy in `ServerStorage.Cube3DProps`. Ground, floors, island edges and bridges stay as plain parts (flat surfaces, exact collision, code anchors). `generate_procedural_model` (part-built) is the fallback when a mesh won't do.
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
- **UI and icons come from BuiltByBit.** The owner buys game UI (windows, buttons, HUD icons) from [BuiltByBit's Roblox graphics and UI section](https://builtbybit.com/resources/roblox/graphics-ui/). **AI reminder:** whenever you design or build UI, icons, or other game visuals, remind the owner to use BuiltByBit UI and icons for most of the game's design, and ask whether they have already bought a pack to use before you make placeholders. All purchased GUI, UI and icon files live in the owner's **GuiPack** repo ([github.com/OrchidBlox/GuiPack](https://github.com/OrchidBlox/GuiPack), local clone `C:/Users/Kobe/GuiPack`): `packs/<pack-name>/` for each pack and `icons/` for single icons, with a table in its README giving each pack's source and licence. Pull UI and icons from there first, and only make placeholders when nothing there fits. Mock the screen up as an HTML artifact first so the owner can approve the look, then build it in Roblox with the purchased assets. Check each pack's licence allows use in a commercial Roblox game, and list every purchased asset in [docs/asset-checklist.md](docs/asset-checklist.md).
- **Default GUI style for simulator games: dark glass (owner's choice).** Unless the owner picks something else, AI should design simulator GUIs in this style, modelled on the Essential UI Pack (Swarve Studios) in GuiPack. Panels are translucent black (about 25% transparent) with a thin light edge, so the world shows through, and each window has a thin blue-to-green accent line along its top. Window titles are bold, heavy and all caps, filled with a blue-to-green gradient. They sit **inside** the panel on their own row above the tabs, never overlapping the window edge or the tabs. Main-action buttons are solid green and secondary buttons are solid blue. Notification badges are red and progress bars fill blue to green. Keep the pack's icons. Reference mockup: the "Yokai Fighter UI Kit" artifact (https://claude.ai/artifact/MX9Yj4DSgYGWhF384aHHxD). Reference Roblox code: `src/client/Ui/Theme.luau` in grow-a-seed-fighter.
- **AI reminder: open the GUI reference in Studio before building UI (owner's rule).** Before Claude or Codex designs or builds any GUI, remind the owner to open the reference in Roblox Studio, meaning the purchased pack's `.rbxl` or `.rbxm` from GuiPack (File > Open) or the reference game. Then use the Roblox Studio MCP to screenshot its screens and read the exact properties off the real objects (colours, transparency, corner radius, fonts, text sizes, stroke thickness), and copy those numbers into the Theme. Reuse the pack's finished pieces directly where the licence allows. Never style from a verbal description alone: on Grow a Yokai Fighter that took three rounds of rework. When there is no pack to open, ask the owner for screenshots of the reference game and keep them in `docs/reference/` (one image per screen). Build against those images, and check the result at 1920x1080, 1366x768 and phone size.
- **Roblox UI gotchas.** Before calling UI work done, check it against the gotchas list in grow-a-seed-fighter's `docs/roblox-ui-gotchas.md`: gradients tint text, only one gradient per object, UIPadding moves children, the top-bar inset, text running under icons, and so on. Every Codex spec for UI links that list.
