# template-game

## Project Overview
template-game is a Roblox game project built with Luau, using Rojo for syncing code between VS Code and Roblox Studio.

## Tech Stack
- **Language:** Luau (Roblox scripting language)
- **Build System:** Rojo (syncs VS Code files ↔ Roblox Studio)
- **Version Control:** Git + GitHub
- **Code Editor:** VS Code

## Project Structure
```
template-game/
├── src/
│   ├── client/          # Client-side code (runs on player's computer)
│   │   └── init.client.luau
│   ├── server/          # Server-side code (runs on game server)
│   │   ├── init.server.luau
│   │   └── ServerScriptService/  # Server scripts
│   │       ├── HelloScript.legacy.luau
│   │       ├── HowAreYou.luau
│   │       └── GameManager.luau
│   └── shared/          # Shared code (both client & server)
├── aftman.toml          # Tool version management
├── default.project.json # Rojo configuration
├── .gitignore           # Git ignore file
└── README.md            # Project documentation
```

## Key Features
- **HelloScript:** Prints "Hello" to the output console
- **HowAreYou:** Prints "How are you" to the output console
- **GameManager:** Core game management module (TBD)

## Getting Started
1. **Clone the repository** to your local machine.
2. **Install Aftman** for tool version management.
3. **Install Rojo** for syncing files between VS Code and Roblox Studio.
4. **Open Roblox Studio** and connect the Rojo plugin to see changes live.
5. **Run Rojo** (`rojo serve`) to sync changes.
6. **Test** in Roblox Studio's play mode.

## Development Tips
- Use the Rojo plugin in Roblox Studio to sync changes in real-time.
- Check the Output window in Roblox Studio to see script print statements.
- Server scripts run in ServerScriptService.
- Client scripts run in StarterPlayer > StarterCharacterScripts or similar.