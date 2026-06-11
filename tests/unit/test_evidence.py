"""Unit tests for the evidence-class registry (Packet D)."""

from __future__ import annotations

import pytest

from qsot_v2.core.evidence import (
    EVIDENCE_CLASSES,
    OBSERVATION_EVIDENCE_CLASS,
    RUNTIME_DEPENDENCY_STATUS,
    build_evidence_registry,
)


def test_all_mapped_classes_are_in_vocabulary():
    for key, cls in OBSERVATION_EVIDENCE_CLASS.items():
        assert cls in EVIDENCE_CLASSES, f"{key} maps to unknown class {cls!r}"


def test_runtime_dependency_status_is_vocabulary():
    assert RUNTIME_DEPENDENCY_STATUS in EVIDENCE_CLASSES


def test_registry_filters_incidental_observations():
    observations = {
        "kd_flat": {"kd_value": -0.12},  # major -> labeled
        "phase0_sensitivity_used": 0.1,  # incidental -> omitted
        "rust_verify_stdout": "PASS",  # incidental -> omitted
        "memory_kernel": {"depth": 1},  # major -> labeled
    }
    registry = build_evidence_registry(observations)
    assert registry == {
        "kd_flat": "phenomenological_model_output",
        "memory_kernel": "synthetic_harness_output",
    }


def test_registry_rejects_class_outside_vocabulary(monkeypatch):
    monkeypatch.setitem(OBSERVATION_EVIDENCE_CLASS, "bogus_block", "not_a_real_class")
    with pytest.raises(ValueError):
        build_evidence_registry({"bogus_block": 1})


def test_each_required_class_has_a_home():
    # Every class in the vocabulary must be reachable: five via the observation
    # registry, runtime_dependency_status via the audit_context blocks.
    used = set(OBSERVATION_EVIDENCE_CLASS.values()) | {RUNTIME_DEPENDENCY_STATUS}
    assert set(EVIDENCE_CLASSES) == used
