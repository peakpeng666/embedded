#!/usr/bin/env python3
"""Check the file inventory included in an extracted handoff archive."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()
    manifest = json.loads((root / "HANDOFF_MANIFEST.json").read_text(encoding="utf-8"))
    failed = []
    for item in manifest["entries"]:
        relative = PurePosixPath(item["path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("Unsafe inventory path")
        path = root.joinpath(*relative.parts)
        if item["type"] == "directory":
            ok = path.is_dir() and not path.is_symlink()
        elif item["type"] == "symlink":
            ok = path.is_symlink() and os.readlink(path) == item["target"]
        else:
            ok = path.is_file() and not path.is_symlink()
            if ok:
                digest = hashlib.sha256()
                with path.open("rb") as stream:
                    for part in iter(lambda: stream.read(1024 * 1024), b""):
                        digest.update(part)
                ok = path.stat().st_size == item["bytes"] and digest.hexdigest() == item["sha256"]
        if not ok:
            failed.append(item["path"])
    if failed:
        raise SystemExit("Verification failed: " + ", ".join(failed[:20]))
    print(f"Verified {len(manifest['entries'])} inventory entries.")


if __name__ == "__main__":
    main()
