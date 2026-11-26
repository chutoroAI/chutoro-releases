"""Build a reproducible archive of the public Claude client from a source checkout."""
import argparse
import hashlib
from pathlib import Path
import re
import tarfile


def package(source, output, version):
    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", version):
        raise ValueError("version must be MAJOR.MINOR.PATCH")
    prefix = f"chutoro-claude-{version}"
    output.mkdir(parents=True, exist_ok=True)
    artifact = output / f"{prefix}.tar"
    with tarfile.open(artifact, "w", format=tarfile.USTAR_FORMAT) as archive:
        for name in ("claude_install.py", "claude_launch.py", "claude_channel_bridge.py", "claude_session_hook.py"):
            data = source / "scripts" / name
            info = tarfile.TarInfo(f"{prefix}/{name}")
            info.size = data.stat().st_size
            with data.open("rb") as handle:
                archive.addfile(info, handle)
    digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
    (output / "SHA256SUMS").write_text(f"{digest}  {artifact.name}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("version")
    args = parser.parse_args()
    package(args.source, args.output, args.version)
