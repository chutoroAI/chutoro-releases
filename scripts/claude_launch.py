"""Launch a native Claude Code conversation with automatic Chutoro delivery."""

from getpass import getpass
import json
import os
from pathlib import Path
import shutil
import shlex
import subprocess
import sys
import tempfile
from urllib.parse import urlsplit
from uuid import UUID

from claude_channel_bridge import HubError, private_file


def validate_arguments(arguments):
    # Claude documents ambiguous startup IDs for implicit resume. Never bind
    # a receiver to a guessed destination.
    for index, argument in enumerate(arguments):
        name, _, value = argument.partition("=")
        if name in {"--bg", "--background", "--cloud", "--safe-mode", "--bare",
                    "--settings", "--mcp-config"}:
            raise HubError(f"{name} is incompatible with the Chutoro foreground launcher and its lifecycle hooks.")
        if name in {"-c", "--continue", "--fork-session"}:
            raise HubError("Use --resume with an explicit conversation UUID, or start a new conversation.")
        if name in {"-r", "--resume"}:
            try:
                UUID(value or arguments[index + 1])
            except (ValueError, IndexError):
                raise HubError("Use --resume with an explicit conversation UUID.") from None


def connection_url():
    path = Path.home() / ".chutoro" / "claude" / "connection.json"
    url = os.environ.get("CHUTORO_MCP_URL")
    if not url and path.exists():
        url = json.loads(path.read_text())["url"]
    if not url:
        url = getpass("Chutoro MCP connection URL (saved privately on this computer): ").strip()
    parsed = urlsplit(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise HubError("Supply the Hub's full HTTP or HTTPS MCP connection URL.")
    # An environment override is temporary; do not overwrite the saved Hub.
    if not os.environ.get("CHUTORO_MCP_URL") and not path.exists():
        path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        with open(path, "x", opener=private_file) as handle:
            json.dump({"url": url}, handle)
    return url


def launch(arguments):
    executable = shutil.which("claude")
    if not executable:
        raise HubError("Install Claude Code before running chutoro claude.")
    commands = {"agents", "attach", "auth", "auto-mode", "doctor", "gateway", "import",
                "install", "logs", "mcp", "plugin", "plugins", "project", "respawn",
                "rm", "setup-token", "stop", "kill", "ultrareview", "update", "upgrade"}
    if (arguments and arguments[0] in commands) or any(
            argument in {"-h", "--help", "-v", "--version"} for argument in arguments):
        return subprocess.call([executable, *arguments])
    validate_arguments(arguments)
    environment = os.environ.copy()
    environment["CHUTORO_MCP_URL"] = connection_url()
    # A fixed pilot path would merge multiple conversations into one identity.
    environment.pop("CHUTORO_SESSION_STATE", None)
    config = {"mcpServers": {"chutoro": {
        "type": "stdio", "command": sys.executable,
        "args": [str(Path(__file__).resolve().parent / "claude_channel_bridge.py")],
    }}}
    print("Chutoro: launching with automatic registration and Channels requested. "
          "Approve the development Channel in Claude Code. If Channels are unavailable, "
          "automatic delivery is unavailable; inbox remains accessible.", file=sys.stderr)
    with tempfile.TemporaryDirectory(prefix="chutoro-claude-") as directory:
        binding = str(Path(directory) / "session.json")
        environment["CHUTORO_CLAUDE_BINDING"] = binding
        hook = shlex.join([sys.executable, str(Path(__file__).with_name("claude_session_hook.py")), binding])
        settings = {"hooks": {event: [{"hooks": [{"type": "command", "command": hook}]}]
                              for event in ("SessionStart", "SessionEnd")}}
        return subprocess.call([executable, "--mcp-config", json.dumps(config),
                                "--settings", json.dumps(settings),
                                "--dangerously-load-development-channels", "server:chutoro",
                                *arguments], env=environment)


if __name__ == "__main__":
    try:
        sys.exit(launch(sys.argv[1:]))
    except HubError as error:
        sys.exit(f"Chutoro: {error}")
    except (OSError, ValueError, KeyError):
        sys.exit("Chutoro: Could not launch Claude Code. Check the saved connection and local files.")
