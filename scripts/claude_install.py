"""One-time shell setup for automatic Chutoro delivery on new Claude sessions."""

import argparse
import os
from pathlib import Path
import re
import shlex
import shutil
import sys

from claude_channel_bridge import HubError, private_file


START = "# BEGIN Chutoro Claude integration"
END = "# END Chutoro Claude integration"


def install(shell, *, remove=False):
    if shell not in {"bash", "zsh"}:
        raise HubError("Shell integration currently supports bash and zsh.")
    home = Path.home()
    directory = Path(os.environ.get("ZDOTDIR", str(home))) if shell == "zsh" else home
    rc = directory / (".zshrc" if shell == "zsh" else ".bashrc")
    original = rc.read_text() if rc.exists() else ""
    block = re.compile(r"(?m)^" + re.escape(START) + r"\n.*?^" + re.escape(END) + r"\n?", re.S)
    stripped = block.sub("", original)
    if START in stripped or END in stripped:
        raise HubError(f"Incomplete Chutoro integration block in {rc}; repair it before retrying.")
    if remove:
        updated = stripped
    else:
        if not shutil.which("claude"):
            raise HubError("Install Claude Code before enabling Chutoro shell integration.")
        if re.search(r"(?m)^\s*(?:alias\s+claude=|(?:function\s+)?claude\s*\(\s*\))", stripped):
            raise HubError(f"An existing claude alias or function is defined in {rc}; reconcile it before installing.")
        executable = Path(__file__).resolve().with_name("claude_launch.py")
        command = shlex.join([sys.executable, str(executable)])
        integration = f'{START}\nclaude() {{\n  {command} "$@"\n}}\n{END}\n'
        updated = stripped + ("" if not stripped or stripped.endswith("\n") else "\n") + integration
    if updated != original:
        rc.parent.mkdir(parents=True, exist_ok=True)
        # Keep the original on the first change. Do not replace symlinked rc
        # files: opening the existing path preserves the user's dotfile layout.
        backup = rc.with_name(rc.name + ".pre-chutoro")
        if rc.exists() and not backup.exists():
            with open(backup, "x", opener=private_file) as handle:
                handle.write(original)
        with open(rc, "w", opener=private_file) as handle:
            handle.write(updated)
    if remove:
        print("Chutoro shell integration removed. Open a new terminal to use native claude directly.")
    else:
        print(f"Chutoro shell integration installed in {rc}. Open a new terminal, then run claude. "
              "The first launch asks for the Hub URL if it has not been saved. "
              "Keep the Chutoro launcher at its current path.")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--shell", choices=("bash", "zsh"), default=Path(os.environ.get("SHELL", "/bin/zsh")).name)
    parser.add_argument("--remove", action="store_true")
    args = parser.parse_args()
    try:
        sys.exit(install(args.shell, remove=args.remove))
    except (HubError, OSError) as error:
        sys.exit(f"Chutoro: {error}")
