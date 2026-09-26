--[[
UI screenshot sheet helper for the Roblox Studio MCP. Run it with execute_luau
in the Client datamodel during Play, then take one screen_capture per screen.

  SCREEN = "list"     -> returns every screen it can open (ScreenGuis with a
                         "Window", plus pop-ups listed in EXTRA)
  SCREEN = "<name>"   -> hides all windows and pop-ups, then shows that one
  SCREEN = "none"     -> hides everything (for a clean HUD shot)

Claude's screenshot pass: run "list", then for each name run it and capture,
and compare the captures with docs/reference/. Studio's viewport size can't be
changed from a script, so check phone/laptop sizes with Studio's Device
emulator (Test tab) when a screen needs it.
]]

local SCREEN = "list"

local pg = game:GetService("Players").LocalPlayer:WaitForChild("PlayerGui")

-- Pop-ups that aren't a ScreenGui.Window: name -> path under PlayerGui.
local EXTRA = {
	Welcome = { "Notifications", "WelcomeBack" },
}

local function find(path: { string }): GuiObject?
	local node: Instance? = pg
	for _, name in path do
		node = node and node:FindFirstChild(name)
	end
	return if node and node:IsA("GuiObject") then node else nil
end

local screens: { [string]: () -> () } = {}
for _, gui in pg:GetChildren() do
	local window = gui:FindFirstChild("Window")
	if gui:IsA("ScreenGui") and window and window:IsA("GuiObject") then
		screens[gui.Name] = function()
			gui.Enabled = true
			window.Visible = true
		end
	end
end
for name, path in EXTRA do
	local popup = find(path)
	if popup then
		screens[name] = function()
			popup.Visible = true
		end
	end
end

local function hideAll()
	for _, gui in pg:GetChildren() do
		local window = gui:FindFirstChild("Window")
		if window and window:IsA("GuiObject") then
			window.Visible = false
		end
	end
	for _, path in EXTRA do
		local popup = find(path)
		if popup then
			popup.Visible = false
		end
	end
end

if SCREEN == "list" then
	local names = {}
	for name in screens do
		table.insert(names, name)
	end
	table.sort(names)
	return table.concat(names, ", ")
end
hideAll()
if SCREEN == "none" then
	return "all windows hidden"
end
local open = screens[SCREEN]
assert(open, `Unknown screen {SCREEN}; run with SCREEN = "list"`)
open()
return `showing {SCREEN}`
