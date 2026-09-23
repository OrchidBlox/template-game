# template-game

This repository is a reusable Roblox starter template. The project name is intentionally still `template-game` so the template remains clear and easy to copy.

When you start a real game project, you should change the values that are project-specific, such as:

* the GitHub repo name
* the folder/project name
* the Roblox project name inside `default.project.json`
* the README title and setup text
* any example strings or printed output used for testing

This template is meant to be a clean base, not a finished game.

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

* [ ] Luau Language Server

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

## Project Structure

```text
template-game/
├── src/
│   ├── client/
│   │   └── init.client.luau
│   ├── server/
│   │   ├── init.server.luau
│   │   └── ServerScriptService/
│   │       ├── GameManager.luau
│   │       ├── HelloScript.legacy.luau
│   │       └── HowAreYou.luau
│   └── shared/
│       └── Hello.luau
├── scripts/
│   └── rename-template.ps1
├── assets/
├── aftman.toml
├── default.project.json
├── .gitignore
├── .mcp.json
├── selene.toml
└── README.md
```

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

This installs the tools listed in `aftman.toml`.

### 4. Verify Rojo

Run:

```powershell
rojo --version
```

Make sure Rojo is installed and working.

### 5. Install the Rojo Studio Plugin

Run:

```powershell
rojo plugin install
```

Restart Roblox Studio after the plugin is installed.

### 6. Start Rojo

From the project folder, run:

```powershell
rojo serve --port 34567
```

Keep this terminal window running while developing.

Rojo must remain connected for changes made to Rojo-managed source files to sync into Roblox Studio.

### 7. Connect Roblox Studio to Rojo

Open Roblox Studio and use the Rojo plugin to connect to the Rojo server.

Once connected, the project files should appear in the Roblox Studio Explorer.

### 8. Configure Roblox Studio MCP

The `Roblox_Studio` MCP server is already defined in [`.mcp.json`](.mcp.json) at the repo root, so it's set up automatically when you open this project in Claude Code — no manual configuration needed.

The first time it loads, Claude Code will prompt you to approve (trust) the project's `.mcp.json` server. Approve it to enable the connection.

Restart VS Code or the Claude Code extension after cloning if the MCP tools aren't showing up.

Roblox Studio should be open and running when using the MCP connection.

### 9. Test the Connection

The template includes basic test scripts so you can verify the VS Code → Rojo → Roblox Studio flow.

Client:

```lua
print("template-game client started!")
```

Server:

```lua
print("template-game server started!")
```

Start Rojo:

```powershell
rojo serve
```

Connect Roblox Studio to Rojo and press Play.

Check the Output window.

You should see:

```text
template-game client started!
template-game server started!
```

If both messages appear, the VS Code → Rojo → Roblox Studio workflow is working correctly.

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

## Notes for New Games

This template is intentionally minimal and should be treated as a starting point.

You will usually replace or remove:

* the basic `Hello` example files
* the placeholder `GameManager` script
* the test prints
* the generic `template-game` naming

That is expected. The point of the template is to give you a working Roblox + Rojo structure, then let you build the actual game on top of it.

The real project should evolve beyond the template once your systems, gameplay, and game name are defined.
