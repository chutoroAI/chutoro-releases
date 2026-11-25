"""Publisher-only build step: produce the manifest for explicit Hub approval."""

import argparse
import hashlib
import json
from pathlib import Path
import re


def build_manifest(version, directory):
    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", version):
        raise ValueError("version must be MAJOR.MINOR.PATCH")
    names = {
        f"chutoro-delivery-{version}-{system}-{arch}" + (".exe" if system == "windows" else "")
        for system in ("darwin", "linux", "windows") for arch in ("amd64", "arm64")
    }
    binaries = {path.name for path in directory.glob("chutoro-delivery-*")}
    if binaries != names:
        raise ValueError("release must contain exactly the six binaries for this version")
    hashes = {}
    for name in sorted(names):
        path = directory / name
        if path.is_symlink() or not path.is_file() or path.stat().st_size == 0:
            raise ValueError("release artifacts must be nonempty regular files")
        digest = hashlib.sha256()
        with path.open("rb") as source:
            for chunk in iter(lambda: source.read(1024 * 1024), b""):
                digest.update(chunk)
        hashes[name] = digest.hexdigest()
    return {"version": version, "sha256": hashes}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version")
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    manifest = build_manifest(args.version, args.directory)
    (args.directory / "release-manifest.json").write_text(json.dumps(manifest, sort_keys=True) + "\n")
    (args.directory / "SHA256SUMS").write_text("".join(
        f"{digest}  {name}\n" for name, digest in manifest["sha256"].items()))


if __name__ == "__main__":
    main()
