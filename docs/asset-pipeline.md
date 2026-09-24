# Asset pipeline: Blender to Roblox without manual imports

Blender models and their animations go into the game with a few commands, not by hand in Studio. This is the concept and the lessons from the first game that used it (Grow & Battle). Adapt the details to each game, and build the pipeline once the first model is ready. It's not needed on day one.

```
Blender (.blend)
  ├─ FBX export ─────────────► upload_assets.py ─► Model assets ─► Studio MCP: insert, fix, place
  └─ export_animations.py ──► .rbxmx ─► upload_assets.py ─► Animation assets ─► IDs in config
                  ▲
                  └─ scripts/rigs/roblox_rest.json (bone rest data dumped from Studio)
```

## Pieces

| File | What it does |
| --- | --- |
| `scripts/upload_assets.py` | Uploads `blender/export/<Model>_*.fbx` (Model), `textures/<Model>_*.png` (Image) and `animations/<Model>_*.rbxmx` (Animation) through the Open Cloud Assets API. Records IDs and file hashes in `scripts/asset_ids.json`, and skips unchanged files. `--dry-run`, `--force`, `--only "<glob>"`. Standard library only. |
| `scripts/export_animations.py` | Runs inside headless Blender. Turns each action into a Roblox KeyframeSequence (`.rbxmx`). |
| `scripts/rigs/roblox_rest.json` | Each rig's bone rest `WorldCFrame`s and MeshPart CFrame, dumped from Studio after the model is placed. |
| `.env` (git-ignored) | `ROBLOX_API_KEY=...` plus one of `ROBLOX_CREATOR_GROUP_ID=...` or `ROBLOX_CREATOR_USER_ID=...`. |

## One-time setup

1. **API key.** Create it on create.roblox.com → Open Cloud → API Keys, **owned by whoever owns the experience**. For a group game, switch the owner to the group before creating it. Give it **Assets read and write** only, your public IP (from "what is my IP", not a 192.168.x.x address), and an expiry date. Never paste it into a chat or commit it.
2. **`.env`.** Put the key in `.env` in the repo root. If the experience is group-owned, use `ROBLOX_CREATOR_GROUP_ID` with the group ID. Putting a group ID on the `USER_ID` line gives "403 User not authenticated".
3. **Blender export settings** (in `blender/README.md`): Forward −Y, Up Z, Apply Unit, and **Bake Animation on with All Actions and Key All Bones**. Every bone needs some vertex weights, or Roblox drops it on import.

## Per model

1. `python scripts/upload_assets.py <Model> --only "*.fbx"`. Uploads the forms.
2. Claude inserts each asset through the Studio MCP (`insert_asset`), removes the PackageLink, and checks it **from the side, with a marker at −Z**:
   - Open Cloud imports have come in lying on their side. The fix: set the MeshPart's rotation to identity, rotate the **Root bone +90° on X**, and move the part so Root sits at the model pivot. A skinned mesh follows its bones and Studio doesn't redraw it after the part alone moves, so judge by a fresh clone.
   - **Rename the MeshPart to the Blender armature name** (for example `FoxRig`) in every form. Animations match their top-level Pose to the MeshPart name. With the wrong name, child bones still move but Root movement (hops, jumps) is silently dropped.
   - Place it where the code expects (for example `ReplicatedStorage.Assets.<Kind>.<Model>.<Form>`) and set a `SourceAssetId` attribute.
3. Claude dumps the rig's rest data into `roblox_rest.json` (the snippet below).
4. `blender -b blender/<Model>.blend --python scripts/export_animations.py -- --rig <Armature> --model <Model>`. The script fits the Blender-to-Roblox mapping from the bone positions and stops if they don't match, so it works for any import orientation.
5. `python scripts/upload_assets.py <Model> --only "*.rbxmx"`, then put the IDs in the game config.
6. Playtest: the tracks load, bones move, and Root lifts in a hop.

Rest-data dump (run through the Studio MCP in Edit mode; paste the result into `roblox_rest.json` under the model's key):

```lua
local m = game.ReplicatedStorage.Assets.<Kind>.<Model>.Base
local function cf(c) local t = {} for i, v in {c:GetComponents()} do t[i] = math.round(v * 1e6) / 1e6 end return t end
local bones = {}
for _, b in m.PrimaryPart:GetDescendants() do
	if b:IsA("Bone") then
		bones[b.Name] = { p = b.Parent:IsA("Bone") and b.Parent.Name or "", w = cf(b.WorldCFrame) }
	end
end
return game:GetService("HttpService"):JSONEncode({ part = cf(m.PrimaryPart.CFrame), bones = bones })
```

## Checks that caught real problems

- **Validate the animation converter against something known.** The first game compared its output with an animation published by hand in the Animation Editor (same Root lift, legs within about 1°) before trusting it.
- **Asset owner = experience owner.** Assets uploaded under a personal account may not load in a group game. Re-upload under the group before release.
- **Hand-imported models** keep their animations in `ServerStorage.RBX_ANIMSAVES`. Open Cloud imports don't, which is why the converter exists.
- `.rbxmx` files are git-ignored. They rebuild from the `.blend` with one command.
