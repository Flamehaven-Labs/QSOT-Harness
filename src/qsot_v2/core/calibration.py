"""Calibration manifest (Packet E).

Surfaces the free / hand-set parameters that govern model outputs, so a reviewer
can identify which results depend on calibration choices rather than on
first-principles derivation. This exposes parameters; it does not move the model
toward first-principles (that would be Stage B).

Values are sourced from a single place each (config or a named module constant)
to avoid spec/code drift.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict

if TYPE_CHECKING:
    from qsot_v2.core.config import ExperimentConfig


def build_calibration_manifest(config: ExperimentConfig) -> Dict[str, Any]:
    """Assemble the calibration manifest from config + named module constants."""
    from qsot_v2.core.phases.phase4 import KD_OPTIMIZATION_STEPS
    from qsot_v2.physics.accessibility import _KD_PENALTY_CAP, _MARKOV_PENALTY_CAP
    from qsot_v2.physics.memory_kernel import _ALPHA_DEFAULT, _EPSILON_BASE

    return {
        "note": (
            "Free / hand-set parameters governing model outputs. These are "
            "calibration choices, not first-principles constants. Realized "
            "per-run values appear in the referenced observations."
        ),
        "free_parameters": {
            "sensitivity_alpha": {
                "value": config.sensitivity,
                "source": "config (experiment.yaml: sensitivity)",
                "role": "alpha in p = 1 - exp(-alpha * ||Riemann||_F); curvature-to-noise mapping",
                "governs": [
                    "background purity decay",
                    "entropy growth",
                    "p_curvature",
                    "phase2_curvature_noise checks",
                ],
                "realized_in": ["ads_boost_info.alpha", "schwarz_rest_info.alpha"],
            },
            "boost_beta": {
                "value": config.boost_beta,
                "source": "config (experiment.yaml: boost_beta)",
                "role": "observer velocity beta; gamma_boost = 1 / sqrt(1 - beta^2)",
                "governs": ["gamma_boost", "p_effective", "phase3_boosts checks"],
                "realized_in": ["ads_boost_info.gamma_boost", "phase0_boost_beta_used"],
            },
            "evolution_steps": {
                "value": config.steps,
                "source": "config (experiment.yaml: steps)",
                "role": "number of channel applications per background evolution (phase1/phase2)",
                "governs": ["purity / entropy trajectories"],
                "realized_in": [
                    "flat_rest_purities",
                    "schwarz_purity",
                    "desitter_purity",
                    "ads_purity",
                    "eguchi_purity",
                ],
            },
        },
        "hardcoded_thresholds": {
            "kd_optimization_steps": {
                "value": KD_OPTIMIZATION_STEPS,
                "source": "hardcoded (phase4.KD_OPTIMIZATION_STEPS)",
                "role": "Adam step budget for KD basis optimization; current runs do not converge within it",
                "governs": ["kd_optimization_converged", "kd_delta"],
                "realized_in": ["kd_flat.convergence", "kd_desitter.convergence"],
            },
            "ttm_epsilon_base": {
                "value": _EPSILON_BASE,
                "source": "hardcoded (memory_kernel._EPSILON_BASE)",
                "role": "base TTM deviation threshold; epsilon_eff = epsilon_base * exp(-alpha * |R|)",
                "governs": ["memory_kernel depth", "memory_kernel_model_trajectory"],
                "realized_in": ["memory_kernel.threshold_used"],
            },
            "ttm_alpha": {
                "value": _ALPHA_DEFAULT,
                "source": "hardcoded (memory_kernel._ALPHA_DEFAULT)",
                "role": "curvature scaling of the TTM threshold",
                "governs": ["dynamic_ttm_threshold"],
                "realized_in": [
                    "memory_kernel.threshold_used",
                    "memory_kernel_model_trajectory.threshold_used",
                ],
            },
            "accessibility_markov_penalty_cap": {
                "value": _MARKOV_PENALTY_CAP,
                "source": "hardcoded (accessibility._MARKOV_PENALTY_CAP)",
                "role": "maximum non-Markovian penalty on the accessibility score",
                "governs": ["accessibility_penalizes_non_markovianity"],
                "realized_in": ["accessibility_scores.score_nm.markov_penalty"],
            },
            "accessibility_kd_penalty_cap": {
                "value": _KD_PENALTY_CAP,
                "source": "hardcoded (accessibility._KD_PENALTY_CAP)",
                "role": "maximum KD-negativity penalty on the accessibility score",
                "governs": ["accessibility_penalizes_kd_negativity"],
                "realized_in": ["accessibility_scores.score_kd.kd_penalty"],
            },
        },
        "notable_magic_constants": {
            "schwarzschild_g00": {
                "source": "hardcoded (channels._build_schwarzschild)",
                "role": "metric g00 -> gamma_grav = 1 / sqrt(-g00); corresponds to a fixed r/M ratio",
                "governs": ["schwarzschild gamma_gravitational"],
                "realized_in": ["schwarz_rest_info.g00"],
                "caveat": "magic constant (H4): the physical r/M interpretation is not documented in code",
            },
        },
    }
