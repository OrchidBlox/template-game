# New computer setup

A checklist for setting up a new Windows computer for Roblox development with the AI workflow. Work top to bottom. Each step ends with a check.

## 1. Copy from the old computer first

Do this **before** wiping or returning the old computer. These files exist only on that computer.

| What | Old location | Why |
| --- | --- | --- |
| Claude's saved notes (memory) | `%USERPROFILE%\.claude\projects\` (each project has a `memory` folder) | Your standing preferences for Claude: the Codex rules, map-building rules, and reminders. Copy the whole `projects` folder to the same place on the new computer. |
| Codex config | `%USERPROFILE%\.codex\config.toml` | Registers the Roblox Studio and Blender MCP servers for Codex. Copy it, then fix the paths (step 5). |
| Codex global instructions | `%USERPROFILE%\.codex\AGENTS.md` | Only if you've written instructions in it. |
| Blender files not in git | Anything outside a repo's `blender/` folder | Everything inside `blender/` is already on GitHub. |

**Don't copy** `%USERPROFILE%\.codex\auth.json` or other sign-in files. Sign in again instead.

Already safe in the cloud: your GitHub repos, the Roblox places, and published assets and animations.

## 2. Install the software

| Tool | Get it | Check |
| --- | --- | --- |
| Git | https://git-scm.com/download/win (keep the default options) | `git --version` |
| Visual Studio Code | https://code.visualstudio.com | Opens |
| Roblox Studio | https://create.roblox.com → Start Creating | Opens and signs in |
| Aftman | https://github.com/LPGhatguy/aftman/releases → download the Windows zip, run `aftman self-install` | `aftman --version` |
| uv (for the Blender MCP) | PowerShell: `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 \| iex"` | `%USERPROFILE%\.local\bin\uvx.exe` exists |
| Blender (4.x or later) | https://www.blender.org/download | Opens |
| GitHub CLI (required for the AI workflow) | PowerShell: `winget install --id GitHub.cli -e` (or https://cli.github.com) | `gh --version`, then `gh auth status` |

If PowerShell can't find `aftman` after installing, add it to your PATH (the README's setup step 2 has the command), then open a new terminal.

## 3. VS Code extensions

Install these from the Extensions panel:

- **Claude Code** (Anthropic): Claude inside VS Code
- **ChatGPT** (OpenAI): includes Codex
- **Roblox LSP** (NightrainsRbx): Luau autocomplete and errors for Roblox
- **Rojo** (evaera): Rojo inside VS Code
- **Selene** (Kampfkarren): shows lint warnings in the editor
- Optional: **GitLens**, **GitHub Pull Requests**

## 4. Sign in

- [ ] **GitHub:** run `gh auth login` in a new terminal (GitHub.com, HTTPS, login with a web browser). Claude and Codex use `gh` to check repo privacy, open pull requests and read issues, so don't skip it. Set your name and email: `git config --global user.name "Your Name"` and `git config --global user.email "you@example.com"`.
- [ ] **Roblox Studio:** sign in with the account that has access to your games (and the group, if the game is group-owned).
- [ ] **Claude Code:** open the Claude panel in VS Code and sign in.
- [ ] **ChatGPT/Codex:** open the ChatGPT panel in VS Code and sign in.

## 5. Connect the AI tools (MCP)

### Roblox Studio MCP

This one comes with Roblox Studio; there is nothing to download. `StudioMCP.exe` is part of Studio's install, and Studio creates `%LOCALAPPDATA%\Roblox\mcp.bat` when you turn on its MCP server in Studio's settings. The project's `.mcp.json` and Codex's config both run that `mcp.bat`. Studio's menus change often, so if you can't find the setting, search the Roblox Creator Docs for "Studio MCP".

Check: `%LOCALAPPDATA%\Roblox\mcp.bat` exists.

### Blender MCP

The Blender MCP has two halves:

- **The server** is the PyPI package [`mcp-for-blender`](https://pypi.org/project/mcp-for-blender/). You don't install it by hand: `uvx` downloads it from PyPI the first time Claude or Codex starts it.
- **The Blender addon** runs inside Blender and receives the commands. Install it once:
  1. Download the project from its GitHub page (linked from the PyPI page). You need `addon.py`.
  2. In Blender: **Edit → Preferences → Add-ons → Install from Disk**, pick `addon.py`, and enable it.
  3. In the 3D Viewport, press **N**, open the **MCP** tab, and click **Connect**.

### Codex config

Open `%USERPROFILE%\.codex\config.toml` (copied in step 1, or create it) and make sure it has:

```toml
[mcp_servers.Roblox_Studio]
command = "cmd.exe"
args = ["/c", 'cd /d %LOCALAPPDATA%\Roblox && .\mcp.bat']

[mcp_servers.blender]
command = 'C:\Users\<you>\.local\bin\uvx.exe'
args = ["--python", "3.11", "mcp-for-blender"]
startup_timeout_sec = 60
```

Replace `<you>` with the new computer's Windows user name. Also remove any `[projects.'c:\users\...']` entries that point to old folders.

## 6. Get your projects

For each game (and this template):

```powershell
git clone https://github.com/<you>/<repo>.git
cd <repo>
aftman install
rojo plugin install
```

`aftman install` installs Rojo and Selene. When Aftman asks whether to trust a tool, answer yes.

## 7. Check that everything connects

Open a project in VS Code and go through these:

- [ ] **Rojo:** `rojo serve`, then connect from the Rojo plugin in Studio. Press Play and see the startup messages in Output.
- [ ] **Selene:** `selene src` shows 0 errors.
- [ ] **Claude and Studio:** ask Claude to "list the connected Roblox Studios". The first time, approve the project's `.mcp.json` servers.
- [ ] **Claude and Blender** (optional): with Blender open and the addon connected, ask Claude to "get the Blender scene info".
- [ ] **Codex:** in PowerShell, find `codex.exe` under `%USERPROFILE%\.vscode\extensions\openai.chatgpt-*\bin\windows-x86_64\` and run `codex.exe mcp list`. Both `Roblox_Studio` and `blender` should appear.
- [ ] **Codex and Blender:** ask Claude to run a one-line Codex test that reads the Blender scene (see [codex-workflow.md](codex-workflow.md)).
- [ ] **Claude's notes:** ask Claude what it remembers about the project's Codex rules. If it doesn't know, the memory folder from step 1 is in the wrong place.

Once all of these pass, the new computer is ready.
