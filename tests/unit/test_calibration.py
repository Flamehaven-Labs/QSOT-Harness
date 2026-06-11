"""Unit tests for the calibration manifest (Packet E)."""

from __future__ import annotations

from qsot_v2.core.calibration import build_calibration_manifest
from qsot_v2.core.phases.phase4 import KD_OPTIMIZATION_STEPS
from qsot_v2.physics.accessibility import _KD_PENALTY_CAP, _MARKOV_PENALTY_CAP
from qsot_v2.physics.memory_kernel import _ALPHA_DEFAULT, _EPSILON_BASE


def test_manifest_sources_config_values(sample_config):
    m = build_calibration_manifest(sample_config)
    fp = m["free_parameters"]
    assert fp["sensitivity_alpha"]["value"] == sample_config.sensitivity
    assert fp["boost_beta"]["value"] == sample_config.boost_beta
    assert fp["evolution_steps"]["value"] == sample_config.steps


def test_manifest_references_single_source_constants(sample_config):
    # Values must come from the named constants, not duplicated literals (no drift).
    th = build_calibration_manifest(sample_config)["hardcoded_thresholds"]
    assert th["kd_optimization_steps"]["value"] == KD_OPTIMIZATION_STEPS
    assert th["ttm_epsilon_base"]["value"] == _EPSILON_BASE
    assert th["ttm_alpha"]["value"] == _ALPHA_DEFAULT
    assert th["accessibility_markov_penalty_cap"]["value"] == _MARKOV_PENALTY_CAP
    assert th["accessibility_kd_penalty_cap"]["value"] == _KD_PENALTY_CAP


def test_manifest_covers_required_categories(sample_config):
    m = build_calibration_manifest(sample_config)
    # Each masterplan-required category is represented and carries a governs map.
    assert "sensitivity_alpha" in m["free_parameters"]  # curvature-to-noise
    assert "boost_beta" in m["free_parameters"]  # boost settings
    assert "kd_optimization_steps" in m["hardcoded_thresholds"]  # step count
    assert "ttm_epsilon_base" in m["hardcoded_thresholds"]  # threshold choices
    for group in (m["free_parameters"], m["hardcoded_thresholds"]):
        for entry in group.values():
            assert entry["governs"], "every calibration parameter must declare what it governs"


def test_every_parameter_points_to_realized_effect(sample_config):
    # Traceability contract: each free / threshold parameter must point to where
    # its realized effect appears in the observations.
    m = build_calibration_manifest(sample_config)
    for group in (m["free_parameters"], m["hardcoded_thresholds"]):
        for name, entry in group.items():
            assert entry.get("realized_in"), f"{name} missing realized_in"


def test_schwarzschild_g00_flagged_as_magic(sample_config):
    g00 = build_calibration_manifest(sample_config)["notable_magic_constants"]["schwarzschild_g00"]
    assert "caveat" in g00 and "H4" in g00["caveat"]
