"""Unit tests for compute_accessibility_score."""

from __future__ import annotations

import pytest

from qsot_v2.physics.accessibility import compute_accessibility_score


def test_gate_fail():
    res = compute_accessibility_score(gate_report={"pass": False, "gate": "FAIL"})
    assert res["final_access_score"] == 0.0
    assert res["gate_pass"] is False


def test_passes_fully():
    res = compute_accessibility_score(gate_report={"pass": True, "gate": "PASS"})
    assert res["final_access_score"] == 1.0
    assert res["gate_pass"] is True


def test_penalties():
    # Markov penalty
    res_nm = compute_accessibility_score(
        gate_report={"pass": True, "gate": "PASS"},
        markov_report={"nm_measure": 0.5, "depth": 1},
    )
    assert res_nm["final_access_score"] < 1.0
    assert res_nm["markov_penalty"] > 0.0

    # KD negativity penalty
    res_kd = compute_accessibility_score(
        gate_report={"pass": True, "gate": "PASS"},
        kd_metrics={"negativity_proxy": 0.01},
    )
    assert res_kd["final_access_score"] < 1.0
    assert res_kd["kd_penalty"] > 0.0

    # Risk penalty
    res_risk = compute_accessibility_score(
        gate_report={"pass": True, "gate": "PASS"},
        verdict={"risk": "red", "admissibility_total": 1.0},
    )
    assert res_risk["final_access_score"] == pytest.approx(0.8)
    assert res_risk["risk_penalty"] == 0.20
