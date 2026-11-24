"""Presentation helpers: what a trend is and how severity ranks.

No surface may define its own. Two answers to "did this repository get worse" that disagree
is worse than either answer alone, so the TUI and the CLI import from here.

Deliberately dependency-free: no store import (store imports report, and report is imported
by the TUI - a cycle waiting to happen), no rendering, no I/O. Everything here reads the
`.counts` mapping that `RunRow` already exposes.
"""

from __future__ import annotations


SEVERITY_ORDER = ("high", "medium", "low")

# A delta is not a plot. Three runs deserve an arrow and a number, not a chart.
WORSE = "▲"
BETTER = "▼"
FLAT = "—"


def rank(severity: str) -> int:
    """Sort key placing high first and anything unrecognised last."""
    return SEVERITY_ORDER.index(severity) if severity in SEVERITY_ORDER else len(SEVERITY_ORDER)


def trend(run, prior) -> dict:
    """A delta, not a plot. `None` prior means there is nothing to compare against."""
    if prior is None:
        return {"symbol": "", "delta": 0, "label": "first run", "direction": "none"}

    now = run.counts.get("total", 0)
    before = prior.counts.get("total", 0)
    delta = now - before
    if delta > 0:
        return {"symbol": WORSE, "delta": delta, "label": f"+{delta}", "direction": "worse"}
    if delta < 0:
        return {"symbol": BETTER, "delta": delta, "label": str(delta), "direction": "better"}
    return {"symbol": FLAT, "delta": 0, "label": "no change", "direction": "flat"}


def severity_counts(run) -> str:
    """`2 high  0 medium  1 low` - the same phrasing both surfaces use."""
    counts = run.counts
    return "  ".join(f"{counts.get(name, 0)} {name}" for name in SEVERITY_ORDER)
