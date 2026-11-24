"""Optional extras: which command needs which, and the one-line hint when one is missing.

The base install is what a pre-commit hook needs (`audit`, `deps`, `models`, `history`,
`diff`). Anything that runs a model, a terminal UI or an MCP server is an extra, and every
import of one is already lazy, so a missing extra is detected here before the import is
attempted - never as a traceback from deep inside a command.

`pyproject.toml` declares the same mapping as `[project.optional-dependencies]`;
`tests/test_packaging.py` builds the wheel and asserts the two agree.
"""

from __future__ import annotations

import importlib.util


# extra -> the top-level modules it provides. A module counts as present when it can be found,
# without importing it: importing claude_agent_sdk or textual just to check is slow.
EXTRA_MODULES: dict[str, tuple[str, ...]] = {
    "agent": ("claude_agent_sdk", "anyio"),
    "tui": ("textual",),
    "mcp": ("mcp", "anyio"),
}


def _installed(module: str) -> bool:
    try:
        return importlib.util.find_spec(module) is not None
    except (ImportError, ValueError):
        return False


def missing(extra: str) -> bool:
    return not all(_installed(module) for module in EXTRA_MODULES[extra])


def install_hint(extra: str, command: str) -> str:
    return (
        f"killscore {command} needs the '{extra}' extra: "
        f"uv tool install 'killscore[{extra}]'  "
        f"(or: uvx --from 'killscore[{extra}]' killscore {command})"
    )
