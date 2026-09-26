--[[
UI screenshot helper for the Roblox Studio MCP (run with execute_luau in the
Client datamodel during Play). It shows one screen at a time so a single
screen_capture after each call gives a full set of screenshots to compare with
the reference images in docs/reference/.

Set SCREEN to one of the names in the list below, run the script, then capture.
Every other window is hidden first, so screens never stack.
]]

local SCREEN = "Pets" -- Pets | Rewards | Welcome | none

local pg = game:GetService("Players").LocalPlayer:WaitForChild("PlayerGui")

-- Hide every window and pop-up.
for _, gui in pg:GetChildren() do
	local window = gui:FindFirstChild("Window")
	if window and window:IsA("GuiObject") then
		window.Visible = false
	end
end
local notes = pg:FindFirstChild("Notifications")
local welcome = notes and notes:FindFirstChild("WelcomeBack")
if welcome then
	welcome.Visible = false
end

local screens = {
	Pets = function()
		pg.PetsMenu.Enabled = true
		pg.PetsMenu.Window.Visible = true
	end,
	Rewards = function()
		pg.Rewards.Enabled = true
		pg.Rewards.Window.Visible = true
	end,
	Welcome = function()
		if welcome then
			welcome.Visible = true
		end
	end,
	none = function() end,
}

local open = screens[SCREEN]
assert(open, `Unknown screen {SCREEN}`)
open()
return `showing {SCREEN}`
