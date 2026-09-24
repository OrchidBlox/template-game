"""Upload Blender exports to Roblox with the Open Cloud Assets API.

Create an API key at create.roblox.com > Open Cloud > API Keys, grant it
Assets read and write access, and allow your IP address (or 0.0.0.0/0). Put
the key in a repo-root .env file as ROBLOX_API_KEY=... and set exactly one of
ROBLOX_CREATOR_USER_ID or ROBLOX_CREATOR_GROUP_ID. The .env file is ignored by
Git. Use --dry-run to inspect files without credentials or network requests.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import sys
import time
import urllib.error
import urllib.request
import uuid


API_ROOT = "https://apis.roblox.com/assets/v1"
# Shown on each uploaded asset; set ROBLOX_ASSET_DESCRIPTION to override.
DESCRIPTION = os.environ.get("ROBLOX_ASSET_DESCRIPTION", "Game asset")
# FBX files named <Model>_<one of these> hold only an animation and are skipped
# unless --include-animations is passed.
ANIMATIONS = {"Idle", "Walk", "Run", "Attack", "Hit"}
POLL_INTERVAL_SECONDS = 2
POLL_TIMEOUT_SECONDS = 120
MAX_429_RETRIES = 5
ASSET_TYPES = {".fbx": "Model", ".png": "Image", ".rbxmx": "Animation"}
CONTENT_TYPES = {".fbx": "model/fbx", ".png": "image/png", ".rbxmx": "model/x-rbxm"}

def load_dotenv(path: Path) -> dict[str, str]:
    """Read simple KEY=VALUE entries without overriding the environment."""
    values: dict[str, str] = {}
    if not path.is_file():
        return values
    for line_number, raw_line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise ValueError(f"Invalid .env line {line_number}: expected KEY=VALUE")
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        values[key] = value
    return values

def configuration(repo_root: Path, dry_run: bool) -> tuple[str, dict[str, str]]:
    dotenv = load_dotenv(repo_root / ".env")

    def setting(name: str) -> str:
        return os.environ.get(name, dotenv.get(name, "")).strip()

    api_key = setting("ROBLOX_API_KEY")
    user_id = setting("ROBLOX_CREATOR_USER_ID")
    group_id = setting("ROBLOX_CREATOR_GROUP_ID")
    creator_error = (
        "Set exactly one of ROBLOX_CREATOR_USER_ID or ROBLOX_CREATOR_GROUP_ID"
    )
    if user_id and group_id:
        raise ValueError(creator_error)
    if not dry_run and not api_key:
        raise ValueError("ROBLOX_API_KEY is required unless --dry-run is used")
    if not dry_run and not (user_id or group_id):
        raise ValueError(creator_error)
    creator = {"userId": user_id} if user_id else {"groupId": group_id}
    return api_key, creator

def discover_files(
    repo_root: Path, model: str, include_animations: bool, only: str | None
) -> list[Path]:
    export_dir = repo_root / "blender" / "export"
    files = list(export_dir.glob(f"{model}_*.fbx"))
    files += list((export_dir / "textures").glob(f"{model}_*.png"))
    # KeyframeSequences written by scripts/export_animations.py.
    files += list((export_dir / "animations").glob(f"{model}_*.rbxmx"))
    animation_stems = {f"{model}_{name}" for name in ANIMATIONS}
    selected = []
    for path in files:
        if not path.is_file():
            continue
        if (not include_animations and path.suffix.lower() == ".fbx"
                and path.stem in animation_stems):
            continue
        relative = path.relative_to(repo_root).as_posix()
        if only and not (
            PurePosixPath(relative).match(only) or PurePosixPath(path.name).match(only)
        ):
            continue
        selected.append(path)
    return sorted(selected, key=lambda item: item.as_posix().lower())

def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

def load_cache(path: Path) -> dict[str, dict[str, object]]:
    if not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Cache must contain a JSON object: {path}")
    return data

def save_cache(path: Path, cache: dict[str, dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(cache, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)

def multipart_body(path: Path, request_data: dict[str, object]) -> tuple[bytes, str]:
    boundary = f"----RobloxAssetUpload{uuid.uuid4().hex}"
    request_json = json.dumps(request_data, separators=(",", ":")).encode("utf-8")
    content_type = CONTENT_TYPES[path.suffix.lower()]
    chunks = [
        (f"--{boundary}\r\nContent-Disposition: form-data; name=\"request\"\r\n"
         "Content-Type: application/json\r\n\r\n").encode(),
        request_json,
        b"\r\n",
        (f"--{boundary}\r\nContent-Disposition: form-data; name=\"fileContent\"; "
         f"filename=\"{path.name}\"\r\nContent-Type: {content_type}\r\n\r\n").encode(),
        path.read_bytes(),
        b"\r\n",
        f"--{boundary}--\r\n".encode(),
    ]
    return b"".join(chunks), f"multipart/form-data; boundary={boundary}"

def request_json(request: urllib.request.Request) -> dict[str, object]:
    retries = 0
    while True:
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            body = error.read().decode("utf-8", errors="replace")
            print(f"HTTP {error.code}: {body}", file=sys.stderr)
            if error.code != 429 or retries >= MAX_429_RETRIES:
                raise
            retry_after = error.headers.get("Retry-After")
            try:
                delay = float(retry_after) if retry_after else 2 ** retries
            except ValueError:
                delay = 2 ** retries
            retries += 1
            time.sleep(min(max(delay, 0), 30))

def operation_url(operation: dict[str, object]) -> str:
    path = operation.get("path")
    if not isinstance(path, str) or not path:
        raise RuntimeError(f"Upload response has no operation path: {operation}")
    clean_path = path.lstrip("/")
    if clean_path.startswith("operations/"):
        return f"{API_ROOT}/{clean_path}"
    return f"{API_ROOT}/operations/{clean_path}"

def upload(path: Path, asset_type: str, creator: dict[str, str], api_key: str) -> object:
    metadata = {
        "assetType": asset_type,
        "displayName": path.stem,
        "description": DESCRIPTION,
        "creationContext": {"creator": creator},
    }
    body, content_type = multipart_body(path, metadata)
    operation = request_json(
        urllib.request.Request(
            f"{API_ROOT}/assets",
            data=body,
            method="POST",
            headers={"x-api-key": api_key, "Content-Type": content_type},
        )
    )
    poll_url = operation_url(operation)
    deadline = time.monotonic() + POLL_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        time.sleep(POLL_INTERVAL_SECONDS)
        operation = request_json(
            urllib.request.Request(poll_url, headers={"x-api-key": api_key})
        )
        if operation.get("done") is True:
            if operation.get("error"):
                raise RuntimeError(f"Asset operation failed: {operation['error']}")
            response = operation.get("response")
            if isinstance(response, dict) and response.get("assetId") is not None:
                return response["assetId"]
            raise RuntimeError(f"Completed operation has no assetId: {operation}")
    raise TimeoutError(f"Asset operation did not finish within {POLL_TIMEOUT_SECONDS}s")

def print_summary(rows: list[tuple[str, str, object]]) -> None:
    print(f"{'STATUS':<8}  {'ASSET ID':<20}  FILE")
    print(f"{'-' * 8}  {'-' * 20}  {'-' * 40}")
    for status, path, asset_id in rows:
        shown_id = str(asset_id) if asset_id is not None else "-"
        print(f"{status:<8}  {shown_id:<20}  {path}")

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("model", metavar="Model", help="file prefix, e.g. Crate for Crate_*.fbx")
    parser.add_argument("--dry-run", action="store_true", help="discover and hash only")
    parser.add_argument("--force", action="store_true", help="upload even when cached")
    parser.add_argument("--only", metavar="GLOB", help="only include matching paths")
    parser.add_argument("--include-animations", action="store_true")
    parser.add_argument("--json", action="store_true", help="print only the final JSON")
    return parser.parse_args()

def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parent.parent
    try:
        api_key, creator = configuration(repo_root, args.dry_run)
        files = discover_files(
            repo_root, args.model, args.include_animations, args.only
        )
        cache_path = repo_root / "scripts" / "asset_ids.json"
        cache = load_cache(cache_path)
        rows: list[tuple[str, str, object]] = []
        ids: dict[str, object] = {}
        for path in files:
            relative = path.relative_to(repo_root).as_posix()
            asset_type = ASSET_TYPES[path.suffix.lower()]
            digest = sha256_file(path)
            cached = cache.get(relative)
            if (not args.force and isinstance(cached, dict)
                    and cached.get("sha256") == digest
                    and cached.get("assetId") is not None):
                asset_id = cached.get("assetId")
                ids[relative] = asset_id
                rows.append(("cached", relative, asset_id))
                continue
            if args.dry_run:
                rows.append(("dry-run", relative, None))
                continue
            asset_id = upload(path, asset_type, creator, api_key)
            cache[relative] = {
                "assetId": asset_id,
                "assetType": asset_type,
                "sha256": digest,
                "uploadedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }
            save_cache(cache_path, cache)
            ids[relative] = asset_id
            rows.append(("uploaded", relative, asset_id))
        if not args.json:
            print_summary(rows)
        print(json.dumps(ids, indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError, RuntimeError, TimeoutError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
