"""Phase 7: Scientific Audit."""
from __future__ import annotations

from typing import TYPE_CHECKING

from qsot_v2.physics import (
    get_audit_backend_info,
    get_audit_runtime,
    run_background_verify,
    run_scientific_audit,
)
from qsot_v2.theory.claim_boundary import CLAIM_BOUNDARY

if TYPE_CHECKING:
    from qsot_v2.core.phase_context import PhaseContext


def run_phase7(ctx: PhaseContext) -> None:
    """Execute Phase 7 checks."""
    rt = get_audit_runtime()

    presets_to_review = [
        "flat", "ads5", "schwarzschild", "de_sitter", "eguchi_hanson", "godel_universe"
    ]

    audit_results = {}
    for name in presets_to_review:
        verify_report = ctx.result.observations.get(f"{name}_verify")
        if verify_report is None:
            # E.g. if phase 2 is disabled, generate dummy verify report for review
            verify_report = run_background_verify(name)[0]

        phys = verify_report["physics"]
        subject = {
            "beta_G_norm": phys.get("beta_G_norm"),
            "beta_B_norm": phys.get("beta_B_norm"),
            "beta_Phi_norm": phys.get("beta_Phi_norm"),
            "drift_admissibility": phys.get("drift_admissibility"),
            "eft_m_kk_gev": phys.get("eft_m_kk_gev"),
            "ricci_norm": phys.get("ricci_norm"),
            "gs_anomaly_flag": phys.get("gs_anomaly_flag", False),
            "has_ctc": phys.get("ctc_status") == "DETECTED",
            "claim_boundary": CLAIM_BOUNDARY,
        }

        res = run_scientific_audit(
            runtime=rt,
            subject=subject,
            source=name,
            gate=verify_report["gate"],
            report_text=f"Reviewing {name} background physics verification."
        )

        expected_minor_revision = {"de_sitter", "godel_universe"}
        expected_accept = {"flat", "schwarzschild"}

        # Determine key, expected verdict, and pass status
        if name == "eguchi_hanson":
            check_key = "scientific_audit_confirms_eguchi_hanson_expected_revision"
            expected = "MINOR_REVISION"
            passed = res.verdict == "MINOR_REVISION"
        elif name in expected_minor_revision:
            check_key = f"scientific_audit_confirms_{name}_expected_fail"
            expected = "MINOR_REVISION"
            passed = res.verdict == "MINOR_REVISION"
        elif name in expected_accept:
            check_key = f"scientific_audit_accepts_{name}"
            expected = "ACCEPT"
            passed = res.verdict == "ACCEPT"
        else:  # ads5
            check_key = f"scientific_audit_accepts_{name}"
            expected = "ACCEPT_OR_MINOR_REVISION"
            passed = res.verdict in ("ACCEPT", "MINOR_REVISION")

        ctx.result.checks[check_key] = "PASS" if passed else "FAIL"
        audit_results[name] = res.to_entry(expected)

    ctx.result.audit_context["scientific_audit"] = get_audit_backend_info()
    ctx.result.observations["scientific_audit_reviews"] = audit_results


def skip_phase7(ctx: PhaseContext) -> None:
    """Skip Phase 7 checks."""
    for name in ["flat", "ads5", "schwarzschild", "de_sitter", "eguchi_hanson", "godel_universe"]:
        expected_minor_revision = {"de_sitter", "godel_universe"}
        if name == "eguchi_hanson":
            check_key = "scientific_audit_confirms_eguchi_hanson_expected_revision"
        else:
            check_key = (
                f"scientific_audit_confirms_{name}_expected_fail"
                if name in expected_minor_revision
                else f"scientific_audit_accepts_{name}"
            )
        ctx.result.checks[check_key] = "SKIPPED"
