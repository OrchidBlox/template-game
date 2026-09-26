-- DataService
-- Saves each player's data with ProfileStore (by loleris,
-- src/server/Packages/ProfileStore.luau): one server at a time per save
-- (session locking), autosave, and saves on leave and server shutdown.
--
-- Usage from other services:
--   DataService.OnProfileLoaded(function(player, data) ... end) -- in Init
--   local data = DataService.GetData(player) -- the live table; change it freely
--
-- Put every saved field in TEMPLATE. New fields are filled in automatically
-- for existing players (Reconcile). When a field's format changes, bump
-- DATA_VERSION and migrate old saves in `migrate`.
--
-- Studio without API access: ProfileStore uses a mock store, so progress
-- doesn't save (Game Settings > Security > Enable Studio Access to API
-- Services). A live player whose save can't load is kicked to rejoin, never
-- given a blank save.

local Players = game:GetService("Players")
local RunService = game:GetService("RunService")

local ProfileStore = require(script.Parent.Parent.Packages.ProfileStore)

local DataService = {}

-- Change STORE_NAME per game. Changing it later starts everyone fresh.
local STORE_NAME = "PlayerData"
local DATA_VERSION = 1

local TEMPLATE = {
	version = DATA_VERSION,
	coins = 0,
	lastSeen = 0,
}

local profileStore
local profiles: { [Player]: any } = {} -- player -> Profile
local loadedCallbacks: { (Player, any) -> () } = {}

-- Upgrades an older save to DATA_VERSION. Add a step per version bump.
local function migrate(data)
	-- Example:
	-- if data.version < 2 then
	-- 	data.gems = data.coins // 100
	-- 	data.version = 2
	-- end
	data.version = DATA_VERSION
end

local function loadProfile(player: Player)
	local profile = profileStore:StartSessionAsync(`Player_{player.UserId}`, {
		Cancel = function()
			return player.Parent ~= Players
		end,
	})
	if profile == nil then
		if player.Parent == Players then
			player:Kick("We couldn't load your save data. Please rejoin in a moment.")
		end
		return
	end
	profile:AddUserId(player.UserId) -- GDPR: links the save to the player
	profile:Reconcile() -- fills in fields added to TEMPLATE since the last save
	profile.OnSessionEnd:Connect(function()
		profiles[player] = nil
		if player.Parent == Players then
			player:Kick("Your save was opened on another server. Please rejoin.")
		end
	end)
	if player.Parent ~= Players then
		profile:EndSession()
		return
	end

	migrate(profile.Data)
	profiles[player] = profile
	if RunService:IsStudio() and ProfileStore.DataStoreState ~= "Access" then
		warn("[DataService] Progress will NOT save in this Studio session. "
			.. "Enable it in Game Settings > Security > Enable Studio Access to API Services.")
	end
	for _, callback in loadedCallbacks do
		task.spawn(callback, player, profile.Data)
	end
end

-- The player's live data table, or nil while it is still loading.
function DataService.GetData(player: Player): any
	local profile = profiles[player]
	return profile and profile.Data
end

-- Runs callback(player, data) whenever a player's data finishes loading.
-- Register during Init so no player is missed.
function DataService.OnProfileLoaded(callback: (Player, any) -> ())
	table.insert(loadedCallbacks, callback)
end

function DataService.Init()
	profileStore = ProfileStore.New(STORE_NAME, TEMPLATE)
end

function DataService.Start()
	Players.PlayerAdded:Connect(loadProfile)
	for _, player in Players:GetPlayers() do
		task.spawn(loadProfile, player)
	end
	Players.PlayerRemoving:Connect(function(player)
		local profile = profiles[player]
		if profile then
			profile.Data.lastSeen = os.time()
			profile:EndSession() -- saves and releases the session lock
		end
		profiles[player] = nil
	end)
end

return DataService
