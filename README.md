# template-game

This repository is a reusable Roblox starter template. The project name is intentionally still `template-game` so the template remains clear and easy to copy.

When you start a real game project, you should change the values that are project-specific, such as:

* the GitHub repo name
* the folder/project name
* the Roblox project name inside `default.project.json`
* the README title and setup text
* any example strings or printed output used for testing

This template is meant to be a clean base, not a finished game.

**Setting up a new computer?** Follow [docs/new-computer-setup.md](docs/new-computer-setup.md): installs, sign-ins, MCP setup, and the files to copy from the old computer.

## What to change when starting a new game

Before using this repo for a real project, update these items:

1. Rename the folder if needed.
2. Rename the GitHub repository to match the new game.
3. Update the `name` field in `default.project.json`.
4. Update the project title in this README.
5. Replace example scripts and print statements with your real game code.
6. Change any placeholder references to `template-game`.

A quick example:

```powershell
./scripts/rename-template.ps1 -ProjectName "Time-of-Adventure"
```

This script updates the project metadata to match the new name automatically.

## Required Software

* [ ] Roblox Studio

  * Used to build and test the Roblox game.

* [ ] Visual Studio Code

  * Main code editor.

* [ ] Claude Code

  * AI coding assistant used with VS Code.

* [ ] Git

  * Source control and version management.

* [ ] GitHub account

  * Stores the remote repository.

* [ ] Aftman

  * Manages Roblox development tools.
  * Used to install the version of Rojo specified in `aftman.toml`.

* [ ] Rojo

  * Syncs Luau source files from the VS Code project into Roblox Studio.
  * Managed through Aftman.

## VS Code Extensions

* [ ] Roblox LSP (NightrainsRbx)

  * Provides Luau syntax highlighting, autocomplete, errors, and other development features.

* [ ] Rojo

  * Rojo integration inside VS Code.

* [ ] Claude Code

  * Provides Claude Code directly inside VS Code.
  * Used for developing and managing game systems and Luau code.

## Roblox Studio

* [ ] Rojo Plugin

  * Connects Roblox Studio to the Rojo project.

* [ ] Roblox Studio MCP

  * Allows Claude Code to interact with and inspect Roblox Studio.
  * Must be configured locally for the Claude Code VS Code extension.
  * Roblox Studio should be open when using the MCP connection.

## AI Tools (optional, for the AI workflow)

* [ ] ChatGPT VS Code extension (includes Codex)

  * Codex writes big code changes and builds Blender models. See [docs/codex-workflow.md](docs/codex-workflow.md).

* [ ] Blender 4.x or later, with the Blender MCP addon

  * Codex builds 3D models here. Setup: [blender/README.md](blender/README.md).

* [ ] uv (for `uvx`)

  * Runs the Blender MCP server (`mcp-for-blender`). Install it so `%USERPROFILE%\.local\bin\uvx.exe` exists.

## Project Structure

```text
template-game/
├── src/
│   ├── client/               # -> StarterPlayerScripts.Client
│   │   ├── init.client.luau  # starts each controller in order
│   │   └── Controllers/      # one controller per UI/system (NotificationController example)
│   ├── server/               # -> ServerScriptService.Server
│   │   ├── init.server.luau  # loads services, runs Init then Start
│   │   └── Services/         # one service per system (PlayerService example)
│   └── shared/               # -> ReplicatedStorage.Shared
│       └── Remotes.luau      # every RemoteEvent, created by the server
├── docs/
│   ├── game-design.md        # the design from ChatGPT
│   ├── codex-workflow.md     # how Claude runs Codex, spec templates, review checklist
│   ├── asset-checklist.md    # every asset and the anchors code needs
│   ├── asset-pipeline.md     # Blender -> Open Cloud uploads and animations
│   ├── animations.md         # published animation IDs
│   └── new-computer-setup.md # setting up a new computer
├── blender/
│   └── README.md             # Blender + Codex model workflow and build rules
├── scripts/
│   └── rename-template.ps1
├── .claude/settings.json     # Claude Code permissions for read-only MCP tools
├── .mcp.json                 # Roblox Studio and Blender MCP servers
├── aftman.toml
├── default.project.json
├── selene.toml
├── CLAUDE.md                 # AI roles, phases, and conventions
└── README.md
```

## AI Workflow

This template is set up for a team of AIs, each with a different job. The full rules are in [CLAUDE.md](CLAUDE.md).

| Who | Job |
| --- | --- |
| **You** | Creative director: decide what gets built, playtest, approve. |
| **ChatGPT** | Designs the game: mechanics, progression, balance, names. Paste its design into [docs/game-design.md](docs/game-design.md). |
| **Codex** | Writes big code changes from Claude's specs, and builds 3D models in Blender through the Blender MCP. |
| **Claude Code** | Plans the architecture, writes specs, reviews and fixes Codex's work, makes small fixes directly, and tests in Studio through the Studio MCP. |
| **Roblox AI generators** | Generate map props (buildings, trees, lanterns, fence sections) from short prompts; Claude or Codex place them with a script. See [docs/ai-map-building-workflow.md](docs/ai-map-building-workflow.md). The Studio Assistant still handles quick manual edits. |

Flow: design (ChatGPT) → plan (Claude) → build (Codex or Claude) → review and test (Claude) → playtest (you) → feedback → repeat.

**Maps:** generate props with Roblox's AI (the Studio MCP tool `generate_procedural_model`, several at once), keep them in `ServerStorage.AIProps`, and have Claude or Codex place them with one short script per area. Screenshot, review and playtest each area, and save the place after each one. Full steps and safety rules: [docs/ai-map-building-workflow.md](docs/ai-map-building-workflow.md).

Track the project as **NOW / NEXT / FUTURE** in CLAUDE.md. Only NOW gets built.

## Starting a New Game

1. Create the new repo from this template and run `./scripts/rename-template.ps1 -ProjectName "YourGame"`.
2. Fill in the NOW / NEXT / FUTURE section of [CLAUDE.md](CLAUDE.md) and paste the design into [docs/game-design.md](docs/game-design.md).
3. Decide who owns the experience (your account or a group) **before** publishing animations or products. Animations must be published under the same owner as the game.
4. Publish the place, then turn on **Game Settings → Security → Enable Studio Access to API Services**, so DataStores work in Studio.
5. Before outside playtests, publish a separate **Dev experience** so testers never touch the real game's save data.
6. Set `Workspace.StreamingEnabled` on purpose. If it's on, tell Codex in every spec so client code looks up map objects lazily.

## Project Setup

### 1. Clone the Repository

Clone the template repository and open the folder in VS Code.

### 2. Install Aftman

Make sure Aftman is installed on your computer.

Aftman should be available in your system PATH so it can be used from PowerShell.

If PowerShell cannot find Aftman, add the Aftman folder to your user PATH:

```powershell
[Environment]::SetEnvironmentVariable("Path", [Environment]::GetEnvironmentVariable("Path", "User") + ";$env:USERPROFILE\.aftman\bin", "User")
```

Close PowerShell and open a new PowerShell window after running the command.

Verify Aftman:

```powershell
aftman --version
```

### 3. Install Project Tools

From the project folder, run:

```powershell
aftman install
```

This installs the tools listed in `aftman.toml`: Rojo and Selene (the Luau linter), at the pinned versions.

### 4. Verify Rojo

Run:

```powershell
rojo --version
```

Make sure Rojo is installed and working. Check Selene the same way with `selene --version`.

### 5. Install the Rojo Studio Plugin

Run:

```powershell
rojo plugin install
```

Restart Roblox Studio after the plugin is installed.

### 6. Start Rojo

From the project folder, run:

```powershell
rojo serve
```

Rojo uses its default port, 34872. Keep this terminal window running while developing.

Rojo must remain connected for changes made to Rojo-managed source files to sync into Roblox Studio.

### 7. Connect Roblox Studio to Rojo

Open Roblox Studio and use the Rojo plugin to connect to the Rojo server.

Once connected, the project files should appear in the Roblox Studio Explorer.

### 8. Configure Roblox Studio MCP

The `Roblox_Studio` MCP server is already defined in [`.mcp.json`](.mcp.json) at the repo root, so it's set up automatically when you open this project in Claude Code — no manual configuration needed.

The first time it loads, Claude Code will prompt you to approve (trust) the project's `.mcp.json` server. Approve it to enable the connection.

Restart VS Code or the Claude Code extension after cloning if the MCP tools aren't showing up.

Roblox Studio should be open and running when using the MCP connection.

The same file also defines a `blender` MCP server, so Claude can inspect Blender when it is open with the MCP addon connected. It needs uv installed (see AI Tools above).

### 9. Test the Connection

The template includes basic test scripts so you can verify the VS Code → Rojo → Roblox Studio flow.

The server and client entry points print a line when they start, and the example `PlayerService` sends a welcome message that `NotificationController` shows as a notification.

Start Rojo:

```powershell
rojo serve
```

Connect Roblox Studio to Rojo and press Play.

Check the Output window.

You should see:

```text
[Server] template-game server started
[Client] template-game client started
```

and a "Welcome" notification in the corner of the game view. If both messages appear, the VS Code → Rojo → Roblox Studio workflow is working correctly.

## Rojo Script Sync

Rojo is responsible for syncing source code between the project and Roblox Studio.

Development workflow:

```text
Claude Code
     ↓
VS Code
     ↓
Luau Source Files
     ↓
Rojo
     ↓
Roblox Studio
     ↓
Test
```

When working on Rojo-managed scripts:

* Keep `rojo serve` running.
* Keep Roblox Studio connected to Rojo.
* Make code changes in VS Code.
* Allow Rojo to sync the changes into Studio.
* Test the changes in Studio.
* Avoid making permanent edits to Rojo-managed scripts directly in Studio.

## Auto-Rename Script

When creating a real project from this template, run:

```powershell
./scripts/rename-template.ps1 -ProjectName "Time-of-Adventure"
```

This updates the project metadata to match the new project name automatically.

If you do not pass a project name, the script will try to infer it from the Git remote or the current folder name.

## Saving Player Data (ProfileStore)

Player saves use **ProfileStore** by loleris (`src/server/Packages/ProfileStore.luau`), the community-standard library for Roblox saves. It keeps each save open on only one server at a time (session locking, which prevents item duplication and lost progress), autosaves, and saves when a player leaves or the server shuts down.

Use it through `src/server/Services/DataService.luau`:

- Put every saved field in `TEMPLATE`. New fields reach existing players automatically.
- Other services call `DataService.GetData(player)` and change the returned table directly. Register `DataService.OnProfileLoaded(callback)` in `Init` to set a player up once their data loads.
- When a field's format changes, bump `DATA_VERSION` and add a step to `migrate`. Never rename `STORE_NAME` after launch, because everyone would start fresh.
- To test saving in Studio, turn on **Game Settings > Security > Enable Studio Access to API Services**. Without it, ProfileStore uses a mock store and nothing saves.

Update ProfileStore by copying the latest `ProfileStore.luau` from https://github.com/MadStudioRoblox/ProfileStore. Selene skips `src/server/Packages` (third-party code).

## Linting (Selene)

Selene checks all Luau code for mistakes such as unused variables, shadowed names and wrong Roblox API use. The rules come from `selene.toml` (`std = "roblox"`), and the version is pinned in `aftman.toml`, so Claude, Codex and you all lint the same way.

Run it from the project folder:

```powershell
selene src
```

Aim for **0 errors and 0 warnings** before every commit. The **Selene** VS Code extension shows the same warnings in the editor as you type.

For the AI workflow, Claude and Codex run `selene src` together with `rojo build -o build.rbxlx` after every change, and fix anything it reports before committing. Codex specs should include "Selene clean" in their done-when checklist.

## AI Workflow Helpers

- **Lint after every edit (hook):** `.claude/hooks/lint-luau.py` runs Selene on each Luau file Claude edits and hands any warnings straight back to Claude to fix. Needs Python and Selene (`aftman install`).
- **Commit reminder (hook):** `.claude/hooks/commit-reminder.py` shows a reminder when Claude finishes with uncommitted files. It never blocks.
- **Playtest feedback to issues:** write your playtest notes as a list in a file, then run `python scripts/feedback-to-issues.py notes.md` (add `--dry-run` to preview). Each item becomes a GitHub issue labelled `playtest`. Needs `gh auth login`.
- **Screenshot pass:** `scripts/ui-screens.luau` opens each game window in turn during Play so Claude can capture a full set of screenshots and compare them with `docs/reference/`. Add pop-ups that aren't a window to its `EXTRA` table.
- **Place backups:** Roblox keeps every published or saved version of the place (File > Version History), so map edits can be restored there. Add a Git LFS place backup (see grow-a-seed-fighter's `scripts/backup-place.sh`) only if you need copies outside Roblox; GitHub's free LFS space fills quickly with large places.

## Git Workflow

Use this template like any other Git project.

Check your branch:

```powershell
git branch
```

Save your changes:

```powershell
git add .
git commit -m "Describe your changes"
git push
```

For new projects, it is common to work on a `development` branch before merging into `main`.

## UI and Icons

Game UI (windows, buttons, HUD icons) is bought from [BuiltByBit](https://builtbybit.com/resources/roblox/graphics-ui/) rather than drawn from scratch. All downloaded GUI, UI and icon files are kept in the [GuiPack repo](https://github.com/OrchidBlox/GuiPack) (local: `C:/Users/Kobe/GuiPack`), and games pull their UI and icons from there. Use BuiltByBit packs for most of each game's design, check the licence allows a commercial Roblox game, and record each pack in `docs/asset-checklist.md`. The AI assistants are told (in `CLAUDE.md`) to remind you of this whenever UI work comes up.

## Notes for New Games

This template is intentionally minimal and should be treated as a starting point.

You will usually replace or remove:

* the example `PlayerService` and `NotificationController` (keep the loader pattern in `init.server.luau` and `init.client.luau`)
* the `Notify` remote, if the game doesn't need it
* the generic `template-game` naming

That is expected. The point of the template is to give you a working Roblox + Rojo structure, then let you build the actual game on top of it.

The real project should evolve beyond the template once your systems, gameplay, and game name are defined.
