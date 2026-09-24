-- This file serves as the entry point for the server-side code.
-- It initializes the server environment and may include setup for game services or other server-related configurations.

-- Example of initializing a basic server environment
local Players = game:GetService("Players")

print("template-game server started!")

-- Function to handle player joining
local function onPlayerAdded(player)
    print(player.Name .. " has joined the game.")
end

-- Connect the player added event
Players.PlayerAdded:Connect(onPlayerAdded)

-- Additional server setup can be added here as needed.