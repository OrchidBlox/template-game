-- PlayerService
-- Example service showing the Init/Start pattern and a server-to-client remote.
-- Replace or delete it once the game has real services.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Remotes = require(ReplicatedStorage.Shared.Remotes)

local PlayerService = {}

local function onPlayerAdded(player: Player)
	Remotes.Notify:FireClient(player, `Welcome, {player.DisplayName}!`)
end

function PlayerService.Start()
	Players.PlayerAdded:Connect(onPlayerAdded)
	-- Players who joined before Start ran (common in Studio playtests).
	for _, player in Players:GetPlayers() do
		task.spawn(onPlayerAdded, player)
	end
end

return PlayerService
