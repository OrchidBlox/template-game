-- Server entry point.
-- Loads each service in SERVICE_ORDER, runs every Init (setup only, no calls
-- into other services), then every Start (connect events, begin work).
-- Add a service here only when the current phase needs it. Order matters when
-- one service's Start relies on another being ready.

local Services = script:WaitForChild("Services")

local SERVICE_ORDER = {
	"DataService",
	"PlayerService",
}

local loaded = {}
for _, name in SERVICE_ORDER do
	loaded[name] = require(Services:WaitForChild(name))
end

for _, name in SERVICE_ORDER do
	local service = loaded[name]
	if service.Init then
		service.Init()
	end
end

for _, name in SERVICE_ORDER do
	local service = loaded[name]
	if service.Start then
		service.Start()
	end
end

print("[Server] template-game server started")
