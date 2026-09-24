# Asset checklist

Every model, visual, and map object the game uses. Code depends only on the anchors listed here (names and attributes), so assets can be swapped without breaking gameplay. Update this file whenever a feature adds or changes an asset.

`ReplicatedStorage.Assets`, `Workspace.Map`, and Terrain are not managed by Rojo, so anything added there in Studio is kept.

| Asset | Where it goes | What the code needs | Required? | Status |
| --- | --- | --- | --- | --- |
| _Example: Hero model_ | `ReplicatedStorage.Assets.Characters.Hero` | A Model with its pivot at the bottom centre, facing the pivot's LookVector | Optional (placeholder block) | Not started |

## Imported model rules

- Pivot at the bottom centre between the feet, facing -Z (the pivot's LookVector).
- Set the pivot through `PrimaryPart.PivotOffset`: setting `WorldPivot` and then `PrimaryPart` switches to the part's own pivot.
- FBX imports can arrive rotated 90°; check that the mesh part is upright before fixing the pivot.
- Colours only survive import as a texture (a palette PNG embedded in the FBX), not as Blender material colours.
