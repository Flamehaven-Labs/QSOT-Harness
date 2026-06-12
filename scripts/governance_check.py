#!/usr/bin/env python
"""Claim-integrity & OPSEC governance gate for QSOT Harness.

Adapted from the Flamehaven sanitizer governance pattern. Fails (exit 1) if any
git-tracked text file contains:

  1. a local-workspace absolute-path / codename leak, or
  2. a Stage A forbidden overclaim phrase (external-validity / physics-proof
     framing). The bounded "not ... ground truth" negation is allowed.

Only git-tracked files are scanned, so the local result matches CI (gitignored
internal docs such as the architect masterplan and the unaudited paper draft are
never inspected or published).

Run:  python scripts/governance_check.py
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SELF = Path(__file__).name

SCAN_SUFFIXES = {".py", ".md", ".toml", ".yaml", ".yml", ".j2", ".rs", ".cff", ".txt"}

# 1. Local-workspace path / codename leaks (DI-SAN-001 style).
LEAK_PATTERNS = [
    re.compile(r"Sanctum"),
    re.compile(r"STRUCTURA"),
    re.compile(r"Users[/\\]dream"),
    re.compile(r"[A-Za-z]:[\\/](?:Sanctum|Users)"),
]

# 2. Affirmative overclaim phrases (Stage A claim boundary). These are written
#    so they do not match honest negations ("... is not external ...").
OVERCLAIM_PATTERNS = [
    re.compile(r"AI-driven", re.I),
    re.compile(r"scientific audit proves", re.I),
    re.compile(r"scientific audit validates the physics", re.I),
    re.compile(r"audit confirms physical truth", re.I),
    re.compile(r"externally validated physics", re.I),
    re.compile(r"physically verified by audit", re.I),
    re.compile(r"DQE proves", re.I),
    re.compile(r"governance engine confirms the law", re.I),
    re.compile(r"review score measures physical correctness", re.I),
    re.compile(r"MINOR_REVISION means physically plausible", re.I),
    re.compile(r"ACCEPT means externally true", re.I),
]

GROUND_TRUTH = re.compile(r"ground[ -]?truth", re.I)


def _bounded_ground_truth(text: str, start: int) -> bool:
    """True for the allowed 'not ... ground truth' negation."""
    return "not " in text[max(0, start - 24) : start].lower()


def _tracked_files() -> list[Path]:
    out = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return [ROOT / line for line in out.splitlines() if line]


def main() -> int:
    findings: list[tuple[str, int, str, str]] = []
    for path in _tracked_files():
        if path.suffix.lower() not in SCAN_SUFFIXES or path.name == SELF:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        rel = path.relative_to(ROOT).as_posix()
        for pat in LEAK_PATTERNS:
            for m in pat.finditer(text):
                ln = text[: m.start()].count("\n") + 1
                findings.append((rel, ln, "workspace-leak", m.group()))
        for pat in OVERCLAIM_PATTERNS:
            for m in pat.finditer(text):
                ln = text[: m.start()].count("\n") + 1
                findings.append((rel, ln, "overclaim", m.group()))
        for m in GROUND_TRUTH.finditer(text):
            if _bounded_ground_truth(text, m.start()):
                continue
            ln = text[: m.start()].count("\n") + 1
            findings.append((rel, ln, "overclaim", m.group()))

    if findings:
        print("Governance gate FAILED -- claim-integrity / OPSEC violations:")
        for rel, ln, kind, snip in findings:
            print(f"  {rel}:{ln} [{kind}] {snip!r}")
        return 1
    print("Governance gate passed: no workspace leaks or overclaim phrases.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
