# Migration Guide: V1 to V2.1

This guide documents the transition from the prototype-focused V1 architecture to the audit-first V2.1 executable contract runner.

## Summary of Changes

| Feature | QSOT V1 (Prototype) | QSOT V2.0 (Audit-First) | QSOT V2.1 (Axiom Contract) |
|---|---|---|---|
| **Interface** | Streamlit Dashboard / REST API | CLI-first (`run_experiment.py`) | CLI-first (`run_experiment.py`) |
| **Output Artifacts** | `optimization_result.json`, etc. | `result.json`, `report.md` | `result.json`, `report.md` |
| **Theoretical Claims** | "Time is an entangled quantum state" | Phenomenological curvature maps | **Temporal-State Axiom Contract** |
| **Falsification** | None | Registry/residual audit | **Phase 0 Axiom Contract Verification** |
| **Claim Control** | Low (over-claiming risk) | High (phenomenological scope) | **Highest (automated claim boundaries)** |

## Migration Steps for Configuration Files

### Default Configuration File
Update `configs/experiment.yaml` to include `phase0_temporal_axioms` under `phases`:

```yaml
phases:
  - id: phase0_temporal_axioms
    enabled: true
  - id: phase1_flat_baselines
    enabled: true
  ...
```

## Running the Compiler

To run the full suite:
```bash
python run_experiment.py --config configs/experiment.yaml
```
The overall verdict will evaluate to `FAIL` if any of the Phase 0 checks fail, serving as an absolute mathematical gatekeeper.
