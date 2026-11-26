"""Publish the current native conversation to this launch's MCP bridge."""
import json
from pathlib import Path
import sys
from uuid import UUID


def main():
    event = json.load(sys.stdin)
    session = str(UUID(event["session_id"]))
    path = Path(sys.argv[1])
    # SessionStart runs for startup, resume, clear, and compaction. SessionEnd
    # pauses delivery until the next SessionStart, even if MCP stays alive.
    value = {"session_id": session, "active": event["hook_event_name"] == "SessionStart"}
    if not value['active'] and path.exists():
        if json.loads(path.read_text())['session_id'] != session:
            return  # A delayed end hook must not pause a newer conversation.
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(value))
    temp.replace(path)


if __name__ == '__main__':
    main()
