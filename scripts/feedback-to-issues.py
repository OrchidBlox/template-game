"""Turn a playtest feedback list into GitHub issues, one per item.

Usage:
    python scripts/feedback-to-issues.py feedback.md [--dry-run]

feedback.md is a plain list; each line starting with "-", "*" or "1." becomes
one issue (indented lines under an item are added to its body). Issues get the
"playtest" label (created if missing) and today's date. Needs the GitHub CLI,
logged in (`gh auth login`).

Screenshots: the GitHub CLI can't upload images, so put the image's file name
in the item (e.g. "coop sign overlaps (shot-3.png)") and drag the image onto
the issue on github.com afterwards if it's needed.
"""
import datetime
import re
import shutil
import subprocess
import sys

GH = shutil.which("gh") or r"C:\Program Files\GitHub CLI\gh.exe"
ITEM = re.compile(r"^\s{0,3}(?:[-*]|\d+[.)])\s+(.*\S)")


def parse(text: str):
    items = []
    for line in text.splitlines():
        match = ITEM.match(line)
        if match:
            items.append([match.group(1)])
        elif items and line.strip():
            items[-1].append(line.strip())
    return items


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    dry = "--dry-run" in sys.argv
    with open(sys.argv[1], encoding="utf8") as f:
        items = parse(f.read())
    if not items:
        print("No list items found.")
        return
    today = datetime.date.today().isoformat()
    if not dry:
        subprocess.run([GH, "label", "create", "playtest", "--color", "5CC8FF",
                        "--description", "Owner playtest feedback"], capture_output=True)
    for lines in items:
        title = lines[0] if len(lines[0]) <= 80 else lines[0][:77] + "..."
        body = "\n".join(lines) + f"\n\n_From the owner's playtest on {today}._"
        if dry:
            print(f"[dry run] {title}")
            continue
        result = subprocess.run([GH, "issue", "create", "--title", title, "--body", body, "--label", "playtest"],
                                capture_output=True, text=True)
        print(result.stdout.strip() or result.stderr.strip())


if __name__ == "__main__":
    main()
