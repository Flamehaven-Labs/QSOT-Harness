"""Unit tests for ExperimentRunner and phase execution."""
from __future__ import annotations

from qsot_v2.core.runner import ExperimentRunner


def test_runner_all_enabled(sample_config):
    # Enable all phases to verify runner integration works end-to-end
    for phase in sample_config.phases:
        phase.enabled = True
        
    runner = ExperimentRunner(sample_config)
    res = runner.run()
    
    assert res is not None
    assert "flat_rest_purity_is_1" in res.checks
    assert "schwarzschild_purity_decays" in res.checks
    assert "boost_accelerates_purity_decay" in res.checks
    assert "kd_basis_optimization_ran" in res.checks
    assert "memory_kernel_selftest_detects_injected_backflow" in res.checks
    # Phase 6 might fail or pass/degraded depending on cargo availability
    assert "rust_verify_binary_runs" in res.checks
    assert "scientific_audit_accepts_flat" in res.checks
    assert "scientific_audit_confirms_eguchi_hanson_expected_revision" in res.checks

    # Verify exact contract values in observations
    schwarz_verify = res.observations["schwarzschild_verify"]
    assert schwarz_verify["physics"]["ricci_norm"] == 0.0
    assert schwarz_verify["physics"]["riemann_norm"] > 0.0
    
    desitter_verify = res.observations["desitter_verify"]
    assert desitter_verify["physics"]["brst_proxy_ok"] is False
    
    godel_verify = res.observations["godel_verify"]
    assert godel_verify["physics"]["ctc_status"] == "DETECTED"

def test_runner_skips(sample_config):
    # Disable all phases (including required ones) -> verdict must be FAIL
    for phase in sample_config.phases:
        phase.enabled = False
        
    runner = ExperimentRunner(sample_config)
    res = runner.run()
    
    assert all(status == "SKIPPED" for status in res.checks.values())
    assert res.verdict == "FAIL"

def test_runner_skips_optional_only(sample_config):
    # Keep required phases enabled, but disable optional Phase 4 (KD)
    for phase in sample_config.phases:
        if phase.id == "phase4_kd_governance":
            phase.enabled = False
        else:
            phase.enabled = True

    runner = ExperimentRunner(sample_config)
    res = runner.run()
    
    # Optional checks are skipped
    assert res.checks["kd_basis_optimization_ran"] == "SKIPPED"
    # Verdict should be DEGRADED_PASS
    assert res.verdict == "DEGRADED_PASS"

