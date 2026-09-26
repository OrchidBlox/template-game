#!/usr/bin/env bash
# Runs ChatGPT Codex non-interactively on a spec file and logs the run.
#
#   scripts/codex-run.sh <spec.md> [model] [reasoning]
#
# - Finds codex.exe inside the ChatGPT VS Code extension (its version folder
#   changes on every extension update, so it is never hard-coded).
# - --approve-for-me: approval requests (Roblox Studio / Blender MCP tools,
#   commands) go to Codex's automatic reviewer instead of being rejected, so
#   Codex can test its own work in Studio. Files stay limited to the project
#   (workspace-write sandbox). Owner approved this on 2026-09-26.
# - Every spec should link docs/roblox-ui-gotchas.md.
set -euo pipefail

spec="${1:?usage: scripts/codex-run.sh <spec.md> [model] [reasoning]}"
model="${2:-gpt-5.6-sol}"   # code changes; Blender model builds use gpt-6-astra
reasoning="${3:-medium}"

root="$(cd "$(dirname "$0")/.." && pwd)"
codex="$(ls -d "$USERPROFILE"/.vscode/extensions/openai.chatgpt-*/bin/windows-x86_64/codex.exe 2>/dev/null | sort -V | tail -1)"
if [ -z "$codex" ]; then
	echo "codex.exe not found - is the ChatGPT VS Code extension installed?" >&2
	exit 1
fi

mkdir -p "$root/.codex-tmp/logs"
log="$root/.codex-tmp/logs/$(date +%Y%m%d-%H%M%S)-$(basename "$spec" .md).log"
echo "Codex: $codex"
echo "Model: $model ($reasoning) - log: $log"

cd "$root"
"$codex" exec -m "$model" -c model_reasoning_effort="$reasoning" --approve-for-me \
	"Read $spec and implement it. Follow docs/roblox-ui-gotchas.md. You may use the Roblox Studio MCP to test your changes in Play mode." \
	>"$log" 2>&1
status=$?
tail -40 "$log"
exit $status
