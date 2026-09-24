-- NotificationController
-- Example controller: shows server messages (Remotes.Notify) as a Roblox
-- system notification. Replace it with the game's own UI when there is one.

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local StarterGui = game:GetService("StarterGui")

local Remotes = require(ReplicatedStorage:WaitForChild("Shared"):WaitForChild("Remotes"))

local NotificationController = {}

function NotificationController.Start()
	Remotes.Notify.OnClientEvent:Connect(function(message: any)
		if type(message) ~= "string" then
			return
		end
		pcall(function()
			StarterGui:SetCore("SendNotification", { Title = "Notice", Text = message, Duration = 4 })
		end)
	end)
end

return NotificationController
