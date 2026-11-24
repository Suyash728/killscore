"""A project's reference to itself (`all = ["app[a,b]"]`) is not a dependency.

Found on killscore's own pyproject on 2026-11-24: composing `[all]` from the other extras,
and pulling `killscore[all]` into the dev group, made slopsquat fetch `killscore` from PyPI.
It was not published yet, so the 404 read as a HIGH "nonexistent-package". The fix drops a
declaration only when its name is the project's own `[project].name`; anything else stays.
"""

from __future__ import annotations

from pathlib import Path
import textwrap

from killscore.deps import read_python_declarations


def _names(tmp_path: Path, pyproject: str) -> list[str]:
    (tmp_path / "pyproject.toml").write_text(textwrap.dedent(pyproject))
    declarations, unparsed = read_python_declarations(tmp_path, ["pyproject.toml"])
    assert unparsed == []
    return sorted(d.name for d in declarations)


def test_self_references_in_extras_and_groups_are_not_dependencies(tmp_path):
    names = _names(
        tmp_path,
        """
        [project]
        name = "My_App"
        dependencies = ["requests"]
        [project.optional-dependencies]
        cli = ["typer"]
        all = ["my-app[cli]"]
        [dependency-groups]
        dev = ["my.app[all]", "pytest"]
        """,
    )

    assert names == ["pytest", "requests", "typer"]


def test_a_dependency_that_only_resembles_the_project_name_is_kept(tmp_path):
    names = _names(
        tmp_path,
        """
        [project]
        name = "my-app"
        dependencies = ["my-app-core", "myapp"]
        """,
    )

    assert names == ["my-app-core", "myapp"]


def test_without_a_project_name_nothing_is_dropped(tmp_path):
    names = _names(
        tmp_path,
        """
        [dependency-groups]
        dev = ["my-app[all]"]
        """,
    )

    assert names == ["my-app"]
