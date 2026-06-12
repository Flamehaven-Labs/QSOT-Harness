# Quantum Geometry & Entropy Verification Report (QGB-TEST-0057)

**Verdict:** `DEGRADED_PASS`  
**Generated:** `2026-06-12T04:50:29.334295+00:00`  
**Repo:** `.`

> [!NOTE]
> **Scope note:**  
> This report verifies model-output consistency under explicitly stated assumptions.  
> It does not claim external physical validation or proof of a new physical law.

## Overview
This report documents the verification of the Quantum Geometry Bridge (QGB) and the Entropy Gate under various classical backgrounds.
This model simulates the mapping of Riemann curvature of classical spacetimes to quantum channels, evaluating how curvature is modeled as a source of decoherence within the implemented mapping, driving purity decay and Von Neumann entropy growth. Relativistic boosts are modeled to further amplify these effects through time dilation.

## Check Summary
- **Total checks:** 50
- **PASS:** 48
- **DEGRADED_PASS:** 1
- **SKIPPED:** 1
- **FAIL:** 0


## Audit Backend Context

> [!IMPORTANT]
> External audit results are **environment-dependent review signals** (evidence class `external_review_signal`). They do not establish external physical validity.

- **Scientific audit backend:** `spar_framework` (mode: `external`, available: `True`, dependency declared: `True`)
- **Score scale:** raw `percentage` normalized to `unit_interval`
- **Claim scope:** `external_review_signal_only`
- **DQE governance engine:** `unavailable` (available: `False`, dependency declared: `False`, scope: `optional_engine_check_only`)





## Calibration (free parameters)

> [!NOTE]
> The outputs below depend on these hand-set calibration choices, not on first-principles derivation.

| Parameter | Value | Source | Governs |
|---|---|---|---|
| `sensitivity_alpha` | `0.1` | config (experiment.yaml: sensitivity) | background purity decay, entropy growth, p_curvature, phase2_curvature_noise checks |
| `boost_beta` | `0.5` | config (experiment.yaml: boost_beta) | gamma_boost, p_effective, phase3_boosts checks |
| `evolution_steps` | `3` | config (experiment.yaml: steps) | purity / entropy trajectories |
| `kd_optimization_steps` | `50` | hardcoded (phase4.KD_OPTIMIZATION_STEPS) | kd_optimization_converged, kd_delta |
| `ttm_epsilon_base` | `1e-06` | hardcoded (memory_kernel._EPSILON_BASE) | memory_kernel depth, memory_kernel_model_trajectory |
| `ttm_alpha` | `0.5` | hardcoded (memory_kernel._ALPHA_DEFAULT) | dynamic_ttm_threshold |
| `accessibility_markov_penalty_cap` | `0.15` | hardcoded (accessibility._MARKOV_PENALTY_CAP) | accessibility_penalizes_non_markovianity |
| `accessibility_kd_penalty_cap` | `0.2` | hardcoded (accessibility._KD_PENALTY_CAP) | accessibility_penalizes_kd_negativity |


**Notable magic constants** (hand-set; physical justification not fully documented in code):
- `schwarzschild_g00` — metric g00 -> gamma_grav = 1 / sqrt(-g00); corresponds to a fixed r/M ratio (hardcoded (channels._build_schwarzschild)). _magic constant (H4): the physical r/M interpretation is not documented in code_




## Checks

- `temporal_axiom_linearity_holds`: **PASS**
- `temporal_axiom_cptp_completeness_holds`: **PASS**
- `temporal_axiom_trace_preservation_holds`: **PASS**
- `temporal_axiom_conditionability_holds`: **PASS**
- `temporal_axiom_density_validity_holds`: **PASS**
- `flat_rest_purity_is_1`: **PASS**
- `flat_rest_entropy_is_0`: **PASS**
- `flat_gate_passes`: **PASS**
- `flat_ctc_is_clear`: **PASS**
- `flat_boost_purity_is_1`: **PASS**
- `schwarzschild_purity_decays`: **PASS**
- `desitter_purity_decays`: **PASS**
- `ads5_purity_decays`: **PASS**
- `eguchi_hanson_purity_decays`: **PASS**
- `schwarzschild_entropy_positive`: **PASS**
- `desitter_entropy_positive`: **PASS**
- `ads5_entropy_positive`: **PASS**
- `eguchi_hanson_entropy_positive`: **PASS**
- `desitter_gate_fails`: **PASS**
- `godel_gate_fails_and_ctc_detected`: **PASS**
- `eguchi_hanson_gate_fails_gs`: **PASS**
- `schwarzschild_curvature_positive`: **PASS**
- `desitter_curvature_positive`: **PASS**
- `ads5_curvature_positive`: **PASS**
- `eguchi_hanson_curvature_positive`: **PASS**
- `boost_accelerates_purity_decay`: **PASS**
- `boost_amplifies_noise_parameter`: **PASS**
- `gamma_boost_greater_than_1`: **PASS**
- `gamma_grav_greater_than_1`: **PASS**
- `gamma_total_combines_effects`: **PASS**
- `kd_basis_optimization_ran`: **PASS**
- `kd_returns_basis_angles`: **PASS**
- `kd_optimization_converged`: **DEGRADED_PASS**
- `kd_relative_signal_recorded`: **PASS**
- `dqe_covenant_validated`: **SKIPPED**
- `memory_kernel_selftest_detects_injected_backflow`: **PASS**
- `accessibility_passes_fully`: **PASS**
- `accessibility_fails_fully`: **PASS**
- `accessibility_penalizes_non_markovianity`: **PASS**
- `accessibility_penalizes_kd_negativity`: **PASS**
- `rust_verify_binary_runs`: **PASS**
- `rust_turbovec_verdict_is_pass`: **PASS**
- `rust_turbovec_ingested_correct_count`: **PASS**
- `rust_turbovec_quantization_error_within_bounds`: **PASS**
- `scientific_audit_accepts_flat`: **PASS**
- `scientific_audit_accepts_ads5`: **PASS**
- `scientific_audit_accepts_schwarzschild`: **PASS**
- `scientific_audit_confirms_de_sitter_expected_fail`: **PASS**
- `scientific_audit_confirms_eguchi_hanson_expected_revision`: **PASS**
- `scientific_audit_confirms_godel_universe_expected_fail`: **PASS**


## Interpretation

The 50 automated checks verify consistency with the implemented model assumptions and expected output behavior:
1. **Flat Minkowski Baselines**: Evolving a qubit through a flat Minkowski background (either at rest or boosted) is modeled to preserve state purity ($P=1.0$) and zero Von Neumann entropy.
2. **Curvature Noise & Entropy**: Evolving a qubit through curved backgrounds (Schwarzschild, de Sitter, AdS5, Eguchi-Hanson) is simulated to cause purity decay ($P < 1.0$) and Von Neumann entropy growth. By mapping the decoherence channel to the Riemann curvature norm (representing tidal forces) rather than the Ricci norm, curved backgrounds are simulated to induce decay while allowing Ricci-flat vacua (Schwarzschild and Eguchi-Hanson) to pass admissibility gate checks.
3. **Relativistic Boosts**: Relativistic boosts ($\beta > 0$) are modeled to amplify the effective noise parameter and accelerate the decay of state purity due to the compounding of gravitational and kinematical time dilation.
4. **Kirkwood-Dirac (flat-relative)**: The basis-search optimization is a bounded engineering sanity check. The reported signal is the de-Sitter-minus-flat KD delta (`kd_delta` in observations), interpreted only as a relative quantity under the implemented model -- not a standalone proof of curvature-induced contextuality. Optimizer convergence is reported explicitly; a non-converged run is surfaced as `DEGRADED_PASS`. If an optional differentiable governance engine is installed, it runs an additional covenant check.
5. **TTM & Accessibility Score**: The TTM module is exercised two ways: a **detector self-test** on a synthetic injected backflow (confirms it registers nm > 0), and the **model's own trajectory** (Markovian by construction, nm ~ 0). The synthetic pass validates the detector, not non-Markovian physics in the model. The accessibility score applies penalties for risk, non-Markovianity, and KD negativity.
6. **Rust turbovec Integration**: Ingesting and querying domain embeddings via the Rust turbovec compressed vector index verifies the consistency of the sidecar resonance similarity score with minimal quantization error (< 0.15).
7. **Compliance Audit Admissibility**: The compliance audit compares each background's gate outputs and residuals against the project's own predefined expected-behavior table, producing a bounded, environment-dependent review signal -- not external ground truth. The review found no blocking inconsistency across the six background reports; minor revisions remain only for backgrounds whose expected behavior intentionally surfaces boundary conditions, such as de Sitter, Eguchi-Hanson, and Gödel universe. This review is a packaging/surface sanity check only. Physics-model consistency is assessed through the physics adapter and executable verification checks; external physical validity remains outside the scope of this report.