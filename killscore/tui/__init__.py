"""Terminal UI over the run database and the checks.

`create_app` takes an optional `db_path`, so tests never touch the real database.
"""

from killscore.tui.app import KillscoreApp, create_app


__all__ = ["KillscoreApp", "create_app"]
