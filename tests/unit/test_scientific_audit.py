"""Unit tests for scientific_audit module (P-1: bounded review-signal schema)."""
from __future__ import annotations

import importlib
import sys

import pytest

from qsot_v2.physics.scientific_audit import (  # noqa: F401
    ScientificAuditResult,
    get_audit_runtime,
    run_scientific_audit,
)


def _make_result(**overrides):
    base = dict(
        verdict="ACCEPT",
        raw_score=0.95,
        normalized_score=0.95,
        raw_score_scale="unit_interval",
        claim_drift_raw=0.02,
        claim_drift_normalized=0.02,
        claim_drift_scale="unit_interval",
        coverage_rate=1.0,
        backend_mode="mock",
        backend_name="qsot_v2_mock_audit",
    )
    base.update(overrides)
    return ScientificAuditResult(**base)


def test_unknown_verdict_coerced_to_unknown():
    with pytest.warns(RuntimeWarning):
        res = _make_result(verdict="TOTALLY_BOGUS")
    assert res.verdict == "UNKNOWN"


def test_invalid_internal_label_raises():
    with pytest.raises(ValueError):
        _make_result(evidence_class="physics_truth")
    with pytest.raises(ValueError):
        _make_result(backend_mode="quantum")
    with pytest.raises(ValueError):
        _make_result(raw_score_scale="furlongs")


def _reload_audit_in_mock_mode(monkeypatch):
    """Force the external framework to be unimportable and reload the module."""
    monkeypatch.setitem(sys.modules, "spar_framework", None)
    monkeypatch.setitem(sys.modules, "spar_framework.engine", None)
    monkeypatch.setitem(sys.modules, "spar_domain_physics.runtime", None)
    monkeypatch.setitem(sys.modules, "spar_domain_physics", None)
    import qsot_v2.physics.scientific_audit as audit
    importlib.reload(audit)
    return audit


def test_audit_mock_verdicts(monkeypatch):
    audit = _reload_audit_in_mock_mode(monkeypatch)
    rt = audit.get_audit_runtime()
    assert rt is not None

    res_flat = audit.run_scientific_audit(rt, {"ricci_norm": 0.0}, "flat", "PASS", "Report")
    assert res_flat.verdict == "ACCEPT"

    res_ads = audit.run_scientific_audit(rt, {"ricci_norm": 1.265}, "ads5", "FAIL", "Report")
    assert res_ads.verdict == "MINOR_REVISION"


def test_audit_mock_backend_mode_and_evidence_class(monkeypatch):
    audit = _reload_audit_in_mock_mode(monkeypatch)
    rt = audit.get_audit_runtime()
    res = audit.run_scientific_audit(rt, {"ricci_norm": 0.0}, "flat", "PASS", "Report")

    assert res.backend_mode == "mock"
    assert res.backend_name == "qsot_v2_mock_audit"
    assert res.evidence_class == "external_review_signal"


def test_audit_mock_normalized_scales(monkeypatch):
    audit = _reload_audit_in_mock_mode(monkeypatch)
    rt = audit.get_audit_runtime()
    res = audit.run_scientific_audit(rt, {"ricci_norm": 0.0}, "flat", "PASS", "Report")

    # Mock declares the unit interval: raw == normalized.
    assert res.raw_score_scale == "unit_interval"
    assert res.normalized_score == res.raw_score == 0.95
    assert res.claim_drift_scale == "unit_interval"
    assert res.claim_drift_normalized == res.claim_drift_raw == 0.02


def test_audit_normalize_percentage_helper(monkeypatch):
    audit = _reload_audit_in_mock_mode(monkeypatch)
    # Percentage -> unit interval; unit_interval/unknown pass through.
    assert audit._normalize(98.0, "percentage") == 0.98
    assert audit._normalize(0.95, "unit_interval") == 0.95
    assert audit._normalize(0.5, "unknown") == 0.5


def test_audit_entry_schema_completeness(monkeypatch):
    audit = _reload_audit_in_mock_mode(monkeypatch)
    rt = audit.get_audit_runtime()
    res = audit.run_scientific_audit(rt, {"ricci_norm": 0.0}, "flat", "PASS", "Report")
    entry = res.to_entry("ACCEPT")

    required = {
        "verdict", "expected_verdict", "raw_score", "normalized_score", "raw_score_scale",
        "claim_drift_raw", "claim_drift_normalized", "claim_drift_scale",
        "coverage_rate", "evidence_class", "backend_mode",
    }
    assert required.issubset(entry.keys())
    # Legacy fields must not appear in Stage A outputs.
    assert "score" not in entry
    assert "claim_drift" not in entry


def test_audit_backend_info_mock(monkeypatch):
    audit = _reload_audit_in_mock_mode(monkeypatch)
    info = audit.get_audit_backend_info()

    assert info["backend_mode"] == "mock"
    assert info["backend_available"] is False
    assert info["dependency_declared"] is True  # spar-framework declared as [audit] extra
    assert info["raw_score_scale"] == "unit_interval"
    assert info["normalized_score_scale"] == "unit_interval"
    assert info["claim_scope"] == "external_review_signal_only"
    # Runtime carrier surfaced separately from the engine (finding 2).
    assert info["runtime_backend"] == "local_fallback"
    assert info["runtime_backend_available"] is False


def test_audit_empty_subject_does_not_use_name_fallback(monkeypatch):
    audit = _reload_audit_in_mock_mode(monkeypatch)
    rt = audit.get_audit_runtime()
    res = audit.run_scientific_audit(rt, {}, "ads5", "PASS", "Report")
    assert res.verdict == "MINOR_REVISION"
    assert res.coverage_rate == 0.0
    assert res.backend_mode == "mock"
