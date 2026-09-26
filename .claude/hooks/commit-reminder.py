"""Stop hook: warn when Claude finishes a turn with uncommitted changes.

Shows a one-line message in the Claude Code UI listing how many files are
uncommitted. It never blocks: half-finished work is sometimes intentional.
"""
import json
import subprocess
import sys

try:
    result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, timeout=20)
except (OSError, subprocess.TimeoutExpired):
    sys.exit(0)

changed = [line for line in result.stdout.splitlines() if line.strip()]
if changed:
    print(json.dumps({"systemMessage": f"Reminder: {len(changed)} uncommitted file(s) in this repo. Commit and push when the work is verified."}))
sys.exit(0)
