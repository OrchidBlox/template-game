-- Client entry point.
-- Starts each controller in CONTROLLER_ORDER. Controllers only display state
-- and send requests; the server decides every outcome.

local Controllers = script:WaitForChild("Controllers")

local CONTROLLER_ORDER = {
	"NotificationController",
}

for _, name in CONTROLLER_ORDER do
	local controller = require(Controllers:WaitForChild(name))
	if controller.Start then
		controller.Start()
	end
end

print("[Client] template-game client started")
