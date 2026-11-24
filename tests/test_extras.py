"""A missing optional extra is an operational error with one line naming the install.

The base install is what a pre-commit hook needs. `harden`, `baseline`, `tui` and `mcp` need
an extra, and without it they must exit 3 with the exact install command - never a
traceback from an import deep inside the command, and never 1 or 2, which mean findings.
`extras._installed` is patched rather than the packages uninstalled, so this runs anywhere;
the real uninstalled case is the clean-venv check recorded in CLAUDE.md.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from killscore import cli, extras


FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def without(monkeypatch):
    """Make the named modules look uninstalled."""

    def hide(*modules: str) -> None:
        real = extras._installed
        monkeypatch.setattr(extras, "_installed", lambda name: name not in modules and real(name))

    return hide


def _run(monkeypatch, *args: str) -> int:
    monkeypatch.setattr("sys.argv", ["killscore", *args])
    return cli.main_entry()


@pytest.mark.parametrize(
    ("args", "module", "extra", "command"),
    [
        (["harden", str(FIXTURES / "mutmut")], "claude_agent_sdk", "agent", "harden"),
        (["baseline", str(FIXTURES / "mutmut"), "--module", "src/pricing.py"], "claude_agent_sdk",
         "agent", "baseline"),
        (["tui"], "textual", "tui", "tui"),
        (["mcp"], "mcp", "mcp", "mcp"),
    ],
)
def test_a_command_without_its_extra_exits_three_with_the_install_line(
    monkeypatch, capsys, without, args, module, extra, command
):
    without(module)

    assert _run(monkeypatch, *args) == 3

    err = capsys.readouterr().err
    assert f"uv tool install 'killscore[{extra}]'" in err
    assert f"uvx --from 'killscore[{extra}]' killscore {command}" in err
    assert "Traceback" not in err
    assert err.count("\n") == 1, "one line, so it can be copied"


def test_anyio_alone_missing_still_counts_as_the_extra_missing(without):
    without("anyio")

    assert extras.missing("agent")
    assert extras.missing("mcp")
    assert not extras.missing("tui")


def test_deps_explain_without_the_agent_keeps_the_verdict(monkeypatch, capsys, tmp_path, without):
    """Losing the prose must never change the exit code a hook branches on."""
    (tmp_path / "requirements.txt").write_text("requests\n")
    clean = _run(monkeypatch, "deps", str(tmp_path), "--no-network")
    capsys.readouterr()

    without("claude_agent_sdk")
    explained = _run(monkeypatch, "deps", str(tmp_path), "--no-network", "--explain")

    assert explained == clean == 0
    assert "uv tool install 'killscore[agent]'" in capsys.readouterr().err


def test_the_base_commands_need_no_extra(monkeypatch, without):
    without("claude_agent_sdk", "anyio", "textual", "mcp")

    assert _run(monkeypatch, "audit", str(FIXTURES / "models-clean"), "--no-save") == 0
    assert _run(monkeypatch, "models", "--list") == 0
