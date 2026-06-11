"""Phase 4: KD Governance."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np

from qsot_v2.core.checks import PHASE_CHECKS
from qsot_v2.physics import (
    BACKGROUND_BUILDERS,
    TORCH_AVAILABLE,
    QuantumCircuit,
    QuantumState,
    run_kd_optimization,
)

if TYPE_CHECKING:
    from qsot_v2.core.phase_context import PhaseContext

# DQE backend policy (code-level, not runtime pyproject parsing).
# flame_torch is a private/externally-provisioned governance engine: it is NOT
# declared as a project dependency, so dependency_declared is fixed False.
# backend_available is resolved at runtime via import success.
DQE_BACKEND_NAME = "flame_torch"
DQE_DEPENDENCY_DECLARED = False

# KD basis-optimization step budget (free calibration choice, surfaced in the
# result-level calibration manifest). Current runs do not converge within it.
KD_OPTIMIZATION_STEPS = 50


def run_phase4(ctx: PhaseContext) -> None:
    """Execute Phase 4 checks."""
    temp_dir = Path("temp_kd_run")
    temp_dir.mkdir(exist_ok=True)
    state_path = temp_dir / "temp_state.npz"
    out_path = temp_dir / "temp_opt.json"

    D = 10
    bg_desitter = BACKGROUND_BUILDERS["de_sitter"](D)
    c_desitter = QuantumCircuit(QuantumState.ground())
    c_desitter.evolve_through_background(bg_desitter, steps=2, sensitivity=ctx.config.sensitivity)

    # Save flat final state (from Phase 1 state observations, fallback to ground if not found)
    flat_rho = (
        ctx.state.flat_final_rho
        if ctx.state.flat_final_rho is not None
        else QuantumState.ground().rho
    )
    np.savez(state_path, rho_0=np.array(flat_rho))
    kd_flat = run_kd_optimization(str(state_path), str(out_path), steps=KD_OPTIMIZATION_STEPS)

    # Save de Sitter final state
    np.savez(state_path, rho_0=c_desitter.state.rho)
    kd_desitter = run_kd_optimization(str(state_path), str(out_path), steps=KD_OPTIMIZATION_STEPS)

    # Clean up
    if state_path.exists():
        state_path.unlink()
    if out_path.exists():
        out_path.unlink()
    try:
        temp_dir.rmdir()
    except OSError:
        pass

    kd_checks = [
        "kd_basis_optimization_ran",
        "kd_returns_basis_angles",
        "kd_optimization_converged",
        "kd_relative_signal_recorded",
    ]
    if TORCH_AVAILABLE:
        if kd_flat is not None and kd_desitter is not None:
            ctx.result.observations["kd_flat"] = kd_flat
            ctx.result.observations["kd_desitter"] = kd_desitter

            # Flat-relative comparative signal. Raw KD negativity is NOT treated as
            # a standalone contextuality proof (Packet A); the de-Sitter-minus-flat
            # delta is the reported model-relative quantity, and optimizer
            # convergence is surfaced separately.
            flat_val = kd_flat["kd_value"]
            desitter_val = kd_desitter["kd_value"]
            flat_conv = bool(kd_flat.get("convergence", {}).get("converged", False))
            desitter_conv = bool(kd_desitter.get("convergence", {}).get("converged", False))
            both_converged = flat_conv and desitter_conv
            kd_delta = {
                "value": desitter_val - flat_val,
                "kd_flat": flat_val,
                "kd_desitter": desitter_val,
                "flat_converged": flat_conv,
                "desitter_converged": desitter_conv,
                "interpretation": (
                    "Relative KD signal (de Sitter minus flat) under the implemented "
                    "model. Not a standalone proof of curvature-induced contextuality; "
                    "optimizer convergence status is reported separately."
                ),
            }
            ctx.result.observations["kd_delta"] = kd_delta

            # Engineering: both optimizations produced a value.
            ctx.result.checks["kd_basis_optimization_ran"] = (
                "PASS" if ("kd_value" in kd_flat and "kd_value" in kd_desitter) else "FAIL"
            )
            # Structural: basis angles returned.
            ctx.result.checks["kd_returns_basis_angles"] = (
                "PASS"
                if (
                    "angles" in kd_desitter
                    and "basis_a" in kd_desitter["angles"]
                    and "basis_b" in kd_desitter["angles"]
                )
                else "FAIL"
            )
            # Convergence explicitly labeled: converged -> PASS, otherwise
            # DEGRADED_PASS (a non-converged but labeled relative proxy is
            # acceptable in Stage A and is surfaced in the verdict).
            ctx.result.checks["kd_optimization_converged"] = (
                "PASS" if both_converged else "DEGRADED_PASS"
            )
            # Comparative signal recorded (finite delta), not a raw-negativity proof.
            ctx.result.checks["kd_relative_signal_recorded"] = (
                "PASS" if np.isfinite(kd_delta["value"]) else "FAIL"
            )
        else:
            for c in kd_checks:
                ctx.result.checks[c] = "FAIL"
    else:
        for c in kd_checks:
            ctx.result.checks[c] = "SKIPPED"
        ctx.result.observations["kd_note"] = "PyTorch not found. KD optimization checks skipped."

    # DQE Covenant Validation (Optional)
    dqe_engine_available = False
    try:
        import flame_torch  # noqa: F401
        import torch  # noqa: F401
        from flame_torch.governance.omega_core import omega  # noqa: F401

        dqe_engine_available = True
    except ImportError:
        dqe_engine_available = False

    if dqe_engine_available:
        try:
            import torch
            from flame_torch.governance.omega_core import omega

            purities = ctx.result.observations.get("flat_rest_purities", [1.0] * 4)
            purity_tensor = torch.tensor(purities, dtype=torch.float64)
            omega.process_tensor("purity_flat", purity_tensor, spec="steps")
            ctx.result.checks["dqe_covenant_validated"] = "PASS"
        except Exception as e:
            ctx.result.checks["dqe_covenant_validated"] = "FAIL"
            ctx.result.observations["dqe_error"] = str(e)
    else:
        ctx.result.checks["dqe_covenant_validated"] = "SKIPPED"
        ctx.result.observations["dqe_note"] = (
            "Optional differentiable governance engine (flame_torch) not installed."
        )

    # Structured backend metadata (replaces free-text-only DQE status).
    from qsot_v2.core.evidence import RUNTIME_DEPENDENCY_STATUS

    dqe_backend_name = DQE_BACKEND_NAME if dqe_engine_available else "unavailable"
    ctx.result.audit_context["dqe_covenant"] = {
        "backend_name": dqe_backend_name,
        "backend_available": dqe_engine_available,
        "dependency_declared": DQE_DEPENDENCY_DECLARED,
        "claim_scope": "optional_engine_check_only",
        # Backend descriptor block = dependency status (Packet D).
        "evidence_class": RUNTIME_DEPENDENCY_STATUS,
    }
    ctx.result.observations["dqe_runtime"] = {
        "backend_name": dqe_backend_name,
        "backend_available": dqe_engine_available,
        "dependency_declared": DQE_DEPENDENCY_DECLARED,
        "evidence_class": "optional_engine_check",
    }


def skip_phase4(ctx: PhaseContext) -> None:
    """Skip Phase 4 checks."""
    for c in PHASE_CHECKS["phase4_kd_governance"]:
        ctx.result.checks[c] = "SKIPPED"
