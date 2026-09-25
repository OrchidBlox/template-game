# AI Map-Building Workflow (reusable)

How to build polished blocky maps with Roblox's AI generators plus Claude or Codex placing the pieces. In a side-by-side test (the same area built three ways: Claude hand-placing parts through the Studio MCP, Roblox's AI generators plus a placement script, and the Studio Assistant chat), the generator approach looked best and was the fastest and cheapest.

## Who does what

| Step | Tool | Who runs it |
|---|---|---|
| Decide the look (theme, palette, props list) | Concept art / artifact, design doc | Owner, with ChatGPT or Claude |
| Generate each prop (gate, lantern, tree, fence section…) | Studio MCP tool `generate_procedural_model`, or the Studio Assistant ("generate a …") | Claude or Codex through the Studio MCP; or the owner in the Assistant panel |
| Keep props as reusable templates | `ServerStorage.AIProps` | Whoever generated them |
| Place and arrange props around an area | One short Luau script per area, written for that game, run through the Studio MCP (`execute_luau`) | Claude or Codex |
| Review and approve | Screenshots, then playtest | Owner |

The Studio Assistant chat panel can't be driven by Claude or Codex, and it is slow (several minutes per prompt). The generator tool itself is fast (about a minute for five props in parallel) and can be called from the MCP.

## Step by step

1. **Save the place** (Ctrl+S) so any step can be undone.
2. **Generate the props in parallel.** One prompt per prop, short and concrete, with the style words every time:
   > A blocky low-poly stone lantern, about 6 studs tall, grey stone base, glowing warm yellow light box, stepped roof. Chunky Roblox simulator style, flat colours.

   Through the MCP: call `generate_procedural_model` with `async: true` for every prop at once, then `wait_job_finished` for each. Results appear in Workspace as ProceduralModels named after the prop; move them into `ServerStorage.AIProps`.
3. **Place them with a script**, not by hand: one short `execute_luau` script per area that clones props from `ServerStorage.AIProps` and sets where each goes, its facing and scale. Writing positions relative to the area's pivot lets the same script work on repeated areas (like identical player plots).
4. **Screenshot** from the player's approach angle (`screen_capture` with a camera position) and adjust scale and spacing.
5. **Park, don't delete**, anything you replace: move old decoration into `ServerStorage.<Area>OldDecor_<Name>` so it can come back.

## Rules that keep gameplay safe

- Never move, rename, or delete the parts game code depends on. Each project lists them in [asset-checklist.md](asset-checklist.md) (named anchor parts and attributes).
- Put nothing on floors or paths that gameplay uses.
- Keep decoration in its own Model (e.g. `Decor`) so it can be swapped as one piece.
- Record each ChangeHistoryService step (`TryBeginRecording` / `FinishRecording`) so Ctrl+Z undoes a whole build.
- Map objects built this way live in the place file, not in Rojo; save the place in Studio after each area.

## Prompt tips for the generators

- Always include: size in studs, "blocky low-poly", "chunky Roblox simulator style", "flat colours", and the 2–3 main colours.
- One object per prompt. Ask for sections (a fence *section*, a bridge *segment*) and repeat them with the placement script rather than generating long pieces.
- Regenerate a single prop if it comes out odd; the placement script re-runs in seconds.
