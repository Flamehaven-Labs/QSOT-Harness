"""Systemic Accessibility Score -- accessibility.py

Accessibility computation module.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

_PASS_GATES = frozenset({"PASS", "GOLD", "SILVER"})
_RISK_PENALTY = {"red": 0.20, "yellow": 0.10, "orange": 0.10, "green": 0.0}
# Penalty caps (free calibration choices, surfaced in the calibration manifest).
_MARKOV_PENALTY_CAP = 0.15
_KD_PENALTY_CAP = 0.20


def compute_accessibility_score(
    gate_report: dict,
    kd_metrics: dict = None,
    markov_report: dict = None,
    integrity_result: object = None,
    verdict: dict = None,
) -> dict:
    """Compute systemic accessibility score from gate report and optional physics data."""
    # --- Gate check ---
    gate_str = gate_report.get("gate", "")
    gate_bool = gate_report.get("pass", gate_str in _PASS_GATES)

    if not gate_bool and gate_str and gate_str not in _PASS_GATES:
        gate_bool = False
    if not gate_bool:
        return {
            "final_access_score": 0.0,
            "gate_pass": False,
            "base_score": 0.0,
            "markov_penalty": 0.0,
            "kd_penalty": 0.0,
            "risk_penalty": 0.0,
            "markov_hint": "blocked",
            "kd_signal": 0.0,
        }

    # --- Base score: Integrity score or admissibility score or 1.0 ---
    base_score = 1.0
    if integrity_result is not None:
        base_score = float(getattr(integrity_result, "admissibility", 1.0))
    elif verdict is not None:
        base_score = float(verdict.get("admissibility_total", 1.0))

    # --- Markov penalty ---
    markov_penalty = 0.0
    markov_hint = "likely_markovian"
    if markov_report is not None:
        nm = float(markov_report.get("nm_measure", 0.0))
        if nm > 1e-6:
            markov_penalty = min(_MARKOV_PENALTY_CAP, nm * 0.1)
            markov_hint = "non_markovian"

    # --- KD negativity penalty ---
    kd_penalty = 0.0
    kd_signal = 0.0
    if kd_metrics is not None:
        neg = float(kd_metrics.get("negativity_proxy", 0.0))
        kd_signal = neg
        kd_penalty = min(_KD_PENALTY_CAP, neg * 10.0)

    # --- Risk penalty from governance verdict ---
    risk_penalty = 0.0
    if verdict is not None:
        risk = verdict.get("risk", "green")
        risk_penalty = _RISK_PENALTY.get(risk, 0.0)

    # --- Final score ---
    score = base_score - markov_penalty - kd_penalty - risk_penalty
    score = max(0.0, min(1.0, score))

    return {
        "final_access_score": round(score, 6),
        "gate_pass": True,
        "base_score": round(base_score, 6),
        "markov_penalty": round(markov_penalty, 6),
        "kd_penalty": round(kd_penalty, 6),
        "risk_penalty": round(risk_penalty, 6),
        "markov_hint": markov_hint,
        "kd_signal": round(kd_signal, 6),
    }
