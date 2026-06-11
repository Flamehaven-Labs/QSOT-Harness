"""ExperimentRunner — runs 8 phases (Phase 0 + 7 verification phases) and 50 checks based on config."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from qsot_v2.core.checks import REQUIRED_CHECKS
from qsot_v2.core.phase_context import PhaseContext, RunnerState
from qsot_v2.core.phases import (
    run_phase0,
    run_phase1,
    run_phase2,
    run_phase3,
    run_phase4,
    run_phase5,
    run_phase6,
    run_phase7,
    skip_phase0,
    skip_phase1,
    skip_phase2,
    skip_phase3,
    skip_phase4,
    skip_phase5,
    skip_phase6,
    skip_phase7,
)
from qsot_v2.core.results import ExperimentResult

if TYPE_CHECKING:
    from qsot_v2.core.config import ExperimentConfig

logger = logging.getLogger(__name__)


class ExperimentRunner:
    """Orchestrates the execution of all quantum geometry & entropy verification phases."""

    def __init__(self, config: ExperimentConfig) -> None:
        self.config = config
        self.result = ExperimentResult(experiment_id=config.experiment_id)
        self.state = RunnerState()

    def run(self) -> ExperimentResult:
        """Run all enabled phases."""
        enabled = self.config.enabled_phases
        ctx = PhaseContext(self.config, self.result, self.state)

        # Map of phase ID to executor functions (run_fn, skip_fn)
        phases = [
            ("phase0_temporal_axioms", run_phase0, skip_phase0),
            ("phase1_flat_baselines", run_phase1, skip_phase1),
            ("phase2_curvature_noise", run_phase2, skip_phase2),
            ("phase3_boosts", run_phase3, skip_phase3),
            ("phase4_kd_governance", run_phase4, skip_phase4),
            ("phase5_ttm_accessibility", run_phase5, skip_phase5),
            ("phase6_rust_turbovec", run_phase6, skip_phase6),
            ("phase7_scientific_audit", run_phase7, skip_phase7),
        ]

        for phase_id, run_fn, skip_fn in phases:
            if phase_id in enabled:
                run_fn(ctx)
            else:
                skip_fn(ctx)

        # Surface the calibration manifest (free / hand-set parameters).
        from qsot_v2.core.calibration import build_calibration_manifest

        self.result.calibration = build_calibration_manifest(self.config)

        # Compute overall verdict
        self._compute_verdict()
        return self.result

    def _compute_verdict(self) -> None:
        has_fail = False
        has_skipped_required = False
        has_skipped_optional = False
        has_degraded = False

        for name, status in self.result.checks.items():
            if status == "FAIL":
                has_fail = True
            elif status == "SKIPPED":
                if name in REQUIRED_CHECKS:
                    has_skipped_required = True
                else:
                    has_skipped_optional = True
            elif status == "DEGRADED_PASS":
                has_degraded = True

        if has_fail or has_skipped_required:
            self.result.set_verdict("FAIL")
        elif has_degraded or has_skipped_optional:
            self.result.set_verdict("DEGRADED_PASS")
        else:
            self.result.set_verdict("PASS")
