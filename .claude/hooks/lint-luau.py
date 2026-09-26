"""PostToolUse hook: lint a Luau file with Selene right after Claude edits it.

Reads the hook JSON on stdin. For .luau/.lua files under src/ (third-party
src/server/Packages is skipped), runs `selene <file>`. If Selene reports
anything, its output goes to stderr with exit code 2, which Claude Code feeds
back to Claude so the problem is fixed straight away. Otherwise it is silent.
"""
import json
import os
import subprocess
import sys

try:
    payload = json.load(sys.stdin)
except Exception:
    sys.exit(0)

tool_input = payload.get("tool_input") or {}
path = tool_input.get("file_path") or ""
norm = path.replace("\\", "/")
if not norm.endswith((".luau", ".lua")) or "/src/" not in norm or "/Packages/" in norm:
    sys.exit(0)
if not os.path.exists(path):
    sys.exit(0)

project = norm[: norm.index("/src/")]
try:
    result = subprocess.run(["selene", path], cwd=project, capture_output=True, text=True, timeout=60)
except (OSError, subprocess.TimeoutExpired):
    sys.exit(0)  # Selene missing or slow: never block editing

output = (result.stdout or "") + (result.stderr or "")
if "0 errors\n0 warnings" in output.replace("\r", ""):
    sys.exit(0)
sys.stderr.write(f"Selene found problems in {os.path.basename(path)}:\n{output}")
sys.exit(2)
