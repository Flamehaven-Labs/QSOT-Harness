"""Integration tests verifying full CLI execution."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from qsot_v2.cli.run_experiment import main


def test_cli_execution(tmp_dir, monkeypatch):
    config_file = Path(__file__).resolve().parents[2] / "configs" / "experiment.yaml"
    out_dir = tmp_dir / "reports"

    # Mock sys.argv to run inside the same Python process for coverage collection
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_experiment.py",
            "--config",
            str(config_file),
            "--out",
            str(out_dir),
            "--format",
            "json",
            "md",
        ],
    )

    # Call main directly
    ret = main()
    assert ret in (0, 1)

    # Check outputs
    result_json = out_dir / "result.json"
    report_md = out_dir / "report.md"

    assert result_json.exists()
    assert report_md.exists()

    # Verify JSON structure
    data = json.loads(result_json.read_text())
    assert data["experiment_id"] == "qgb-test-0057"
    assert "verdict" in data
    assert "checks" in data

    # P-1: top-level audit_context is serialized with both backend blocks.
    assert "audit_context" in data
    sci = data["audit_context"]["scientific_audit"]
    for key in (
        "backend_name",
        "backend_mode",
        "backend_available",
        "runtime_backend",
        "runtime_backend_available",
        "dependency_declared",
        "raw_score_scale",
        "normalized_score_scale",
        "claim_scope",
    ):
        assert key in sci, f"scientific_audit missing {key}"
    assert sci["backend_mode"] in ("mock", "external")
    assert sci["runtime_backend"] in ("spar_domain_physics", "local_fallback")
    assert sci["claim_scope"] == "external_review_signal_only"

    dqe = data["audit_context"]["dqe_covenant"]
    for key in ("backend_name", "backend_available", "dependency_declared", "claim_scope"):
        assert key in dqe, f"dqe_covenant missing {key}"
    assert dqe["dependency_declared"] is False  # externally provisioned

    # phase4 writes structured DQE runtime metadata (not free text only).
    dqe_runtime = data["observations"]["dqe_runtime"]
    assert dqe_runtime["evidence_class"] == "optional_engine_check"

    # Per-background review entries use the normalized schema, not legacy fields.
    for entry in data["observations"]["scientific_audit_reviews"].values():
        assert "normalized_score" in entry
        assert "evidence_class" in entry
        assert entry["evidence_class"] == "external_review_signal"
        assert "score" not in entry and "claim_drift" not in entry
        # normalized score must lie on the unit interval.
        assert 0.0 <= entry["normalized_score"] <= 1.0

    # Packet D: evidence-class registry labels all major observation blocks.
    from qsot_v2.core.evidence import EVIDENCE_CLASSES

    ev = data["evidence_classes"]
    for cls in ev.values():
        assert cls in EVIDENCE_CLASSES
    # The eight required major blocks must each be labeled (inline or registry).
    assert ev["phase0_scenarios"] == "mathematical_invariant"
    assert ev["schwarz_purity"] == "phenomenological_model_output"
    assert ev["kd_flat"] == "phenomenological_model_output"
    assert ev["memory_kernel"] == "synthetic_harness_output"
    assert ev["memory_kernel_model_trajectory"] == "phenomenological_model_output"
    assert ev["accessibility_scores"] == "synthetic_harness_output"
    assert ev["rust_turbovec_result"] == "synthetic_harness_output"
    assert ev["scientific_audit_reviews"] == "external_review_signal"
    assert ev["dqe_runtime"] == "optional_engine_check"
    # Background verification blocks are rule-based policy classifications.
    for vk in (
        "flat_verify",
        "schwarzschild_verify",
        "desitter_verify",
        "ads5_verify",
        "godel_verify",
        "eguchi_verify",
    ):
        assert ev[vk] == "policy_derived_classification", vk
    # Boost / curvature numerics are phenomenological model outputs.
    assert ev["ads_boost_info"] == "phenomenological_model_output"
    assert ev["schwarz_rest_info"] == "phenomenological_model_output"
    # No major observation block remains unlabeled (Packet D acceptance bar).
    from qsot_v2.core.evidence import OBSERVATION_EVIDENCE_CLASS

    INCIDENTAL = {
        "phase0_sensitivity_used",
        "phase0_boost_beta_used",
        "rust_verify_stdout",
        "dqe_note",
        "kd_note",
        "dqe_error",
    }
    for key in data["observations"]:
        if key in INCIDENTAL:
            continue
        assert key in OBSERVATION_EVIDENCE_CLASS, f"unlabeled major block: {key}"
    # runtime_dependency_status is carried inline on the audit_context blocks.
    assert sci["evidence_class"] == "runtime_dependency_status"
    assert dqe["evidence_class"] == "runtime_dependency_status"

    # Packet A: KD is reported flat-relative; raw negativity is not a proof and
    # the legacy magic-bound check is gone.
    for k in (
        "kd_basis_optimization_ran",
        "kd_returns_basis_angles",
        "kd_optimization_converged",
        "kd_relative_signal_recorded",
    ):
        assert k in data["checks"], k
    assert "kd_flat_respects_lower_bound" not in data["checks"]
    assert "kd_desitter_contextuality_proxy_detected" not in data["checks"]
    if data["checks"]["kd_basis_optimization_ran"] != "SKIPPED":
        assert ev["kd_delta"] == "phenomenological_model_output"
        kd_delta = data["observations"]["kd_delta"]
        assert "value" in kd_delta and "interpretation" in kd_delta
        assert "not a standalone proof" in kd_delta["interpretation"].lower()
        assert data["checks"]["kd_optimization_converged"] in ("PASS", "DEGRADED_PASS")

    # Packet B: memory kernel split into a synthetic detector self-test and the
    # model's own (Markovian-by-construction) trajectory. The pass clearly names
    # its source, and the legacy ambiguous check is gone.
    assert "memory_kernel_selftest_detects_injected_backflow" in data["checks"]
    assert "memory_kernel_detects_non_markovianity" not in data["checks"]
    assert data["observations"]["memory_kernel"]["source"] == "synthetic_injected_backflow"
    mt = data["observations"]["memory_kernel_model_trajectory"]
    assert mt["source"] == "model_generated_trajectory"
    assert mt["nm_measure"] <= mt["threshold_used"]  # Markovian by construction

    # Packet E: calibration manifest surfaces free parameters and what they govern.
    cal = data["calibration"]
    assert cal["free_parameters"]["sensitivity_alpha"]["governs"]
    assert cal["free_parameters"]["boost_beta"]["governs"]
    assert cal["hardcoded_thresholds"]["kd_optimization_steps"]["governs"]
    assert "H4" in cal["notable_magic_constants"]["schwarzschild_g00"]["caveat"]

    # Report markdown surfaces the bounded-review scope note + calibration table.
    report_text = report_md.read_text(encoding="utf-8")
    assert "Audit Backend Context" in report_text
    assert "environment-dependent review signals" in report_text
    assert "Calibration (free parameters)" in report_text
    assert "sensitivity_alpha" in report_text
    # H4 magic constant disclosure must reach the report, not just JSON.
    assert "Notable magic constants" in report_text
    assert "schwarzschild_g00" in report_text
