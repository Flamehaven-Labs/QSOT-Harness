# Frozen experiment evidence — QSOT-Harness paper

This directory holds the **exact, frozen experiment artifacts** that back the
numerical claims in the manuscript (`paper/`). They are preserved unmodified for
transparency and for registration in the audit ledger.

## Frozen files (SHA-256)

SHA-256 over the **canonical LF bytes** as committed/archived in this repository
(the repo normalizes text to LF via `.gitattributes`, so these match a fresh
clone and the Zenodo archive on any platform):

| File | SHA-256 (LF) |
|---|---|
| `result.json` | `b1a83df5caf8d1f222b6d15254c7de0d87ebfece574d7605d30f7ef9951dac6b` |
| `report.md`   | `18c6a2facecb2cd107f1b45b117997d1aca2a36346e671f1e546cb60a4d51976` |

## Provenance

- **generated_at**: `2026-06-12T04:50:29.334295+00:00` (from `result.json`)
- **run engine commit**: `26c06800e6e38fb53dc69b915d8cf509715f9ca7`
- **archived in release**: v2.1.0 (`4f19078`). The run engine (`src/`, `configs/`, `run_experiment.py`) is byte-identical between `26c0680` and `4f19078` (empty diff), so this frozen artifact is canonical for the v2.1.0 record.
- **schema**: `compliance.qsot_v2.experiment_result.v2`

## Environment dependence (read before reproducing)

This run was produced with the optional external review backend **present**, so:

- `audit_context.scientific_audit.backend_mode = "external"` (`spar_framework`),
  with percentage-scale raw scores normalized to the unit interval.
- A reproduction **without** `spar_framework` runs the local deterministic mock
  (`backend_mode = "mock"`, unit-interval scores). The audit **scores** will then
  differ, but the verdict, KD, and memory-kernel results below are unaffected
  (KD uses a fixed seed; the channel maps are deterministic).

The optional governance engine `flame_torch` was **absent**, so
`dqe_covenant_validated = SKIPPED`.

## Cross-check: manuscript claim ↔ frozen value

| Manuscript claim | Frozen value in `result.json` |
|---|---|
| Overall verdict `DEGRADED_PASS` (48 / 0 / 1 / 1) | `verdict=DEGRADED_PASS`, `summary={total:50, pass:48, fail:0, skipped:1, degraded_pass:1}` |
| `kd_optimization_converged = DEGRADED_PASS` (non-convergence) | `checks.kd_optimization_converged="DEGRADED_PASS"`, both `convergence.converged=false` |
| `dqe_covenant_validated = SKIPPED` | `checks.dqe_covenant_validated="SKIPPED"` |
| `Q_KD^flat ≈ -0.123` | `observations.kd_flat.kd_value = -0.1234` |
| `Q_KD^deSitter ≈ -0.012` | `observations.kd_desitter.kd_value = -0.0120` |
| `Δ_KD ≈ +0.11` | `observations.kd_delta.value = +0.1115` |
| synthetic self-test `nm ≈ 1.4e-3` | `observations.memory_kernel.nm_measure = 0.0014132…` (`source=synthetic_injected_backflow`) |
| model trajectory `nm = 0` | `observations.memory_kernel_model_trajectory.nm_measure = 0.0` (`source=model_generated_trajectory`) |

The test/coverage figures in the manuscript (**64 passed, 94.48% coverage**) come
from the test suite, not from `result.json`.

## Reproduction

```bash
# Experiment artifacts (result.json + report.md)
python run_experiment.py --config configs/experiment.yaml --out reports

# Test suite + coverage (64 passed, ~94.48%)
python -m pytest --cov=qsot_v2 --cov-report=term-missing
```

Re-running is content-stable except for two expected sources of variation that do
**not** change the scientific result: the `generated_at` timestamp, and the audit
`backend_mode` (external vs mock) per the environment note above. Because of the
timestamp, a fresh run is not byte-identical and will hash differently; the SHA-256
values above anchor *this specific frozen copy* for the ledger.
