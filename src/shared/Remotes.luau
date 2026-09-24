-- Remotes
-- Names every RemoteEvent in one place. The server creates them at startup;
-- clients wait for them. Add a name (and a line describing its payload) when a
-- feature needs a new remote. Validate every client -> server payload on the
-- server: type, range, ownership, and whether the action is allowed right now.
--
-- Notify (server -> client): message: string, a short message for the player.

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local FOLDER_NAME = "Remotes"
local REMOTE_NAMES = {
	"Notify",
}

local Remotes = {}

if RunService:IsServer() then
	local folder = Instance.new("Folder")
	folder.Name = FOLDER_NAME
	for _, name in REMOTE_NAMES do
		local remote = Instance.new("RemoteEvent")
		remote.Name = name
		remote.Parent = folder
		Remotes[name] = remote
	end
	folder.Parent = ReplicatedStorage
else
	local folder = ReplicatedStorage:WaitForChild(FOLDER_NAME)
	for _, name in REMOTE_NAMES do
		Remotes[name] = folder:WaitForChild(name)
	end
end

return Remotes
