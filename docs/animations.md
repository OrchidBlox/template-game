# Animations

The published animation IDs the game uses.

**Publish every animation under the experience's owner.** If the game belongs to a group, publish under the group. Roblox won't play animations owned by a different account, and they fail silently.

## How to publish

1. Import the model FBX into Studio (Import 3D). Its actions land in `ServerStorage → RBX_ANIMSAVES → <Model>`.
2. Right-click an action → **Save to Roblox…** → name it `<Model>_<Action>` → choose the owner (group or account).
3. Paste the ID below and tell Claude.

Forms that share one skeleton share one set of animations, so publish only the base form's.

## <Model name>

Rig: `<rig name>` (<n> bones). Source: `blender/export/<Model>_<Action>.fbx`. 30 fps.

| Action | Frames | Loop | Used for | Asset ID | Status |
| --- | ---: | --- | --- | --- | --- |
| Idle | | yes | standing | | Not published |

Code status: not wired.
