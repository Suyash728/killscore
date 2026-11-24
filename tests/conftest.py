"""Session-wide guards for the test suite.

`~/.killscore/runs.db` is a real user database. `audit` records to it by default, so a
single CLI test that forgets `--no-save` writes fixture runs into someone's actual history,
where they surface in `killscore history` and the local UI. That happened: 116 of the 119
runs in this machine's database were fixture rows left by earlier test runs.

Passing `--no-save` in each test fixes today's leak but relies on every future test
remembering. Redirecting the default path for the whole session makes it structural: a test
that forgets the flag writes to a temporary file instead of the user's history.
"""

import shutil

import pytest

from killscore import store


@pytest.fixture(autouse=True, scope="session")
def _never_touch_the_real_database(tmp_path_factory):
    """Point the default database at a throwaway file for the whole run."""
    redirected = tmp_path_factory.mktemp("killscore-home") / "runs.db"
    original = store.DEFAULT_DB_PATH
    store.DEFAULT_DB_PATH = redirected
    try:
        yield redirected
    finally:
        store.DEFAULT_DB_PATH = original


# ------------------------------------------------------------------------- ts-morph marker
#
# A test marked `@pytest.mark.ts_morph` needs the real TypeScript helpers: node on PATH and
# a helper dir with ts-morph installed. Without them it skips, and says which one is missing.
# This is the only place that decides it. A test must not skip on `result.skipped` itself,
# because that also hides a helper that is installed but broken ("ts-morph helper failed").

_TS_MORPH_UNAVAILABLE: list[str | None] = []


def _ts_morph_unavailable() -> str | None:
    if not _TS_MORPH_UNAVAILABLE:
        from killscore.checks import node_helper

        if shutil.which("node") is None:
            reason = "node is not on PATH"
        elif node_helper.helper_dir() is None:
            reason = node_helper.missing_reason()
        else:
            reason = None
        _TS_MORPH_UNAVAILABLE.append(reason)
    return _TS_MORPH_UNAVAILABLE[0]


def pytest_runtest_setup(item):
    if item.get_closest_marker("ts_morph") is not None:
        reason = _ts_morph_unavailable()
        if reason is not None:
            pytest.skip(f"needs the ts-morph helper: {reason}")
