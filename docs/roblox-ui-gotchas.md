# Roblox UI gotchas

Every problem on this list cost at least one round trip while building the dark glass UI. Specs for Codex link this file; check a change against it before calling UI work done.

## Gradients and strokes
- **A UIGradient also tints an object's text.** A coloured gradient on a TextButton turns white text into the button colour ("hollow" text). Put the colour in `BackgroundColor3` and keep the gradient between white and light grey, or put the gradient on a child frame.
- **An object uses only one UIGradient.** If a button already has one (for example a glass background), a second one for the title is ignored. Reuse the existing gradient (`Theme.headline` does this).
- `UIStroke` with `ApplyStrokeMode.Contextual` outlines text, and `Border` outlines the frame. Use the one you mean.

## Layout
- **UIPadding moves children too.** An icon parented to a padded button shifts with the padding. Offset the icon back, or parent it outside the padded area.
- **Top-bar inset.** A ScreenGui without `IgnoreGuiInset` is shorter than `Camera.ViewportSize`. Size full-screen layers with `UDim2.fromScale`, not from the viewport in pixels, or bottom-anchored buttons end up off screen.
- **`Camera.ViewportSize` reads 1x1 while the camera starts.** Ignore sizes under about 200 px and listen for `ViewportSize` changes.
- **Icons beside text.** Give the text a left inset at least as wide as the icon, and let long text shrink (`TextScaled` plus `UITextSizeConstraint`) instead of running under the icon or clipping.
- **UIListLayout sorts by name by default.** Set `SortOrder = LayoutOrder` whenever the order matters.
- **Titles never overlap window edges or tabs.** Give them their own row inside the panel.
- **Check at 1920x1080, 1366x768 and a phone size (about 844x390).** Nothing may overlap the HUD, and windows stay within about 70% of the screen.

## World labels (BillboardGui)
- Size them in studs (`Size` scale) or set `MaxDistance`, or they fill the screen close up.
- `AlwaysOnTop = false` lets the model hide them. Use it for labels above Yokai.
- Hide a follow card while a battle nameplate is showing, so the two don't stack.

## Streaming and models
- `Workspace.StreamingEnabled` is on. The client must look up map objects lazily (`WaitForChild` with a timeout, `ChildAdded`) and cope with them streaming out.
- 3D ViewportFrames don't show in MCP screen captures. A blank tile in a capture isn't a bug on its own.

## Style rules (dark glass)
- Use `Theme` helpers only: `bubbleize` (glass, or `solid = true` for action buttons), `headline`, `accentLine`, `iconPill`, `window`.
- Never use dark ink text on glass, pastel fills or FredokaOne.
