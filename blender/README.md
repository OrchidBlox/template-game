# Blender + Codex (MCP) workflow

This folder holds the 3D models for this game, built by ChatGPT Codex in Blender through the Blender MCP.

- `<Name>.blend`: the Blender source file for each model
- `export/`: the FBX files you import into Roblox Studio
- `design/`: design references (design sheets or concept art for each model)

Codex's job here is **models only**: meshes, rigs, animations, and exports. Game code, Studio edits, and docs belong to Claude.

## 1. MCP setup (template)

Add the Blender MCP server to Codex's config at `%USERPROFILE%\.codex\config.toml`:

```toml
[mcp_servers.blender]
command = 'C:\Users\<you>\.local\bin\uvx.exe'   # path to uvx (install uv first)
args = ["--python", "3.11", "mcp-for-blender"]
startup_timeout_sec = 60
```

In Blender:

1. Install and enable the MCP addon that matches the server (Edit → Preferences → Add-ons → Install from Disk).
2. In the 3D Viewport sidebar (press N), open the MCP tab and click **Connect** or **Start Server**.
3. Keep Blender open while Codex runs. If Codex reports that it can't reach Blender, reconnect the addon and run again.

Check the connection with `codex mcp list`. `blender` should be listed.

## 2. Running Codex

Codex ships inside the ChatGPT VS Code extension. The version folder changes when the extension updates:

```
%USERPROFILE%\.vscode\extensions\openai.chatgpt-<version>-win32-x64\bin\windows-x86_64\codex.exe
```

Run a spec file from the repo root:

```bash
codex.exe exec -m <model> -c model_reasoning_effort="medium" -s workspace-write -c 'mcp_servers.blender.default_tools_approval_mode="approve"' -C . - < spec.txt
```

- `mcp_servers.blender.default_tools_approval_mode="approve"`: required. A non-interactive run has no way to approve tool calls, so without this setting every Blender MCP call fails with "requires approval, but approval policy is never".

- `-m`: pick the model per run (for example `gpt-5.6-sol`, or `gpt-6-astra` for heavy model work). Don't change the default in `config.toml`.
- `-s workspace-write`: Codex can write files in the repo only. The old `--full-auto` flag no longer exists.
- `- < spec.txt`: the prompt is read from a file. Build the file from the template below.

## 3. Spec template

Put a scope block at the top of every spec, then the model brief:

```
TASK SCOPE (strictly enforced):
- Your ONLY job: build <asset name and forms> in Blender using the Blender MCP tools.
- Do NOT edit src/, docs/, default.project.json, or any Roblox/Studio files. Do NOT use the Roblox_Studio MCP. Do not write Luau.
- Write files only under blender/: save the source to blender/<Name>.blend and exports to blender/export/.
- Visual reference: blender/design/<file>. Match its shapes, proportions, and colours.
- After each step, take a viewport screenshot and fix obvious problems before moving on.
- Final report: objects, triangle count per form, bones, actions, export paths, and what to check by eye.

THE BRIEF:
<paste the asset brief>
```

## 4. Build rules for Codex

These rules apply to every asset. Roblox and the game code depend on them.

**Scale and placement**
- 1 Blender unit = 1 Roblox stud.
- The model stands on Z = 0, centred on X = 0, Y = 0, and faces −Y.
- The object origin is at the bottom centre between the feet. Apply all transforms before export.

**Geometry**
- Low-poly Roblox style: flat colours from simple Principled BSDF materials, no image textures.
- Aim for 1,500–4,000 triangles per form, and never more than 10,000 (Roblox's mesh limit per part).
- Build from simple primitives, join them into one mesh per form, and apply every modifier.
- No n-gons with holes. Triangulating on export is fine.
- Glowing parts use emission in the same colour as the base, strength 2–3.

**Naming**
- Meshes are named `<Fighter>_<Form>` (for example `Frog_Evolved`).
- Forms or evolutions of one model share one armature: same bone names, same hierarchy, same rest pose.
- Action names match the names the game code uses exactly (for example `Idle`, `Attack`, `Hit`).

**Rigging and animation**
- Keep the bone count small and fixed per fighter family. Rigid parts (eyes, head pieces) get weight 1.0 on their bone.
- 30 fps. Looping actions start and end on the same pose.
- Only `Root` moves. Every other bone only rotates or scales.

**Scripts and safety**
- Every script can be run again: first delete the objects it made earlier, by name.
- Work in small steps and check each step visually before the next.
- Save the `.blend` often. Never overwrite exports from another fighter.

**Export (FBX)**
- Selected Objects only (the mesh plus its armature). Apply Scalings: FBX All. Forward: −Y. Up: Z. Apply Unit on.
- Add Leaf Bones off. Bake Animation on with All Actions on. NLA Strips off. Key All Bones on.
- File names: `<Fighter>_<Form>.fbx`, plus one `<Fighter>_<Action>.fbx` per animation if Roblox needs them separately.

## 5. After Codex finishes

1. Claude reviews the report and the exports: triangle counts, names, facing, and scale.
2. Claude uploads them with `scripts/upload_assets.py`, inserts them through the Studio MCP, checks the orientation, and places them where the code expects (for example `ReplicatedStorage.Assets.<Kind>.<Model>.<Form>`). Manual Import 3D still works as a fallback.
3. Claude converts and uploads the animations with `scripts/export_animations.py`, then connects the IDs in the game. See `docs/asset-pipeline.md`.

Keep a list of every asset the game expects, and the names it needs, in the repo docs.
