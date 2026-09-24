# Codex workflow

How Claude hands work to ChatGPT Codex. Codex writes **big code changes** and builds **Blender models**; Claude writes the spec, then reviews, fixes, and tests the result. Small fixes are made by Claude directly.

## Finding Codex

Codex is not on PATH. It ships inside the ChatGPT VS Code extension, and the version folder changes when the extension updates, so search for it instead of hard-coding it:

```
%USERPROFILE%\.vscode\extensions\openai.chatgpt-<version>-win32-x64\bin\windows-x86_64\codex.exe
```

## Running a spec

Write the spec to a file, then run it from the repo root:

```bash
codex.exe exec -m <model> -c model_reasoning_effort="medium" -s workspace-write -C . - < spec.txt > codex.log 2>&1
```

- `-m <model>`: choose per run. Use the cheaper default model unless the owner asks for a stronger one, and don't edit `~/.codex/config.toml` to change it.
- `-s workspace-write`: Codex can write only inside the repo. (`--full-auto` no longer exists.)
- For Blender work, also pass `-c 'mcp_servers.blender.default_tools_approval_mode="approve"'`. A non-interactive run can't approve tool calls, so without it every Blender MCP call fails with "requires approval, but approval policy is never".
- Run it in the background and read the end of `codex.log` when it finishes.

## Code spec template

```
<Game name> (Roblox, Rojo, Luau). <One-line goal>.

CONSTRAINTS
- Do NOT edit: <map files, default.project.json, unrelated services, docs/>.
- Match the surrounding code style (naming, comment density, module API style).
- Workspace.StreamingEnabled is on: client code must look up map objects lazily.
- Server authority: the server decides outcomes; validate every remote.

DATA
<config tables to add, with exact values>

FILES
<each file to create or change, the functions, and the rules they follow>

EDGE CASES
<leaving mid-action, respawn, duplicate requests, missing models>

After editing, run `rojo build -o <temp path>.rbxlx` and fix any errors. Report the files changed and a short summary.
```

## Blender spec template

```
TASK SCOPE (strictly enforced):
- Your ONLY job: build <asset> in Blender using the Blender MCP tools.
- Do NOT edit src/, docs/, default.project.json, or Roblox/Studio files. Do NOT use the Roblox_Studio MCP.
- Write files only under blender/. Follow the build rules in blender/README.md.
- Visual reference: blender/design/<file>.
- After each step, take a viewport screenshot and fix obvious problems.
- Report: objects, triangle counts, bones, actions, export paths, what to check by eye.

THE BRIEF:
<the asset brief>
```

## Claude's review checklist

1. Read the whole diff, not only Codex's summary.
2. Check the scope: nothing outside the allowed files changed.
3. Look for client/server mistakes: trusting the client, unvalidated remotes, missing cleanup on leave or destroy.
4. Look for Roblox pitfalls: instances used before they are parented (animations won't load), StreamingEnabled lookups, yields in hot loops.
5. Fix small problems directly; send big ones back to Codex with a focused follow-up spec.
6. Run `rojo build`, sync, playtest through the Studio MCP, and check Output for errors.
7. Commit with a message that says what was built and what was tested.
