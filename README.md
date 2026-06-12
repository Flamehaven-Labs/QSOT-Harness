# QSOT Harness

[![CI](https://github.com/Flamehaven-Labs/QSOT-Harness/actions/workflows/ci.yml/badge.svg)](https://github.com/Flamehaven-Labs/QSOT-Harness/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Coverage ~94%](https://img.shields.io/badge/coverage-~94%25-brightgreen.svg)](#running-tests)
[![Claim scope: model-consistency only](https://img.shields.io/badge/claim%20scope-model--consistency%20only-orange.svg)](#what-this-is-and-is-not)

A bounded, **epistemically-labeled** CLI harness that runs quantum-channel models of curved-spacetime backgrounds and emits machine-readable verification artifacts (`result.json`, `report.md`). It verifies **model-output consistency under explicitly stated assumptions** — not external physical validity. The pipeline is a strict, reproducible **"Print-and-Exit"** CLI runner.

> **Honest reconstruction.** This is the genuine rebuild of QSOT. Its predecessor (*"QSOT Compiler V1"*) was published as an **intentional** high-formality slop artifact — executable and formal-looking, but scientifically hollow. QSOT Harness removes that slop: every reported signal declares its evidence class, every external/optional backend is surfaced in `audit_context`, the KD signal is reported flat-relative (not as a contextuality proof), non-Markovianity self-tests are kept distinct from model trajectories, and free calibration parameters are listed with what they govern. The claim boundary is machine-readable — see [`docs/theory/claim_boundary.md`](docs/theory/claim_boundary.md).

## What this is and is not

- **Is:** a reproducible verification harness for a *phenomenological* channel-map model; a rigorously bounded, self-labeling experiment runner whose every output declares its epistemic class.
- **Is not:** a physics proof, a Theory of Everything, or external experimental validation. A passing check means *model-internal consistency under the stated assumptions* — nothing more.

---

## Features

- **CLI-First Architecture**: Run experiments directly with configuration files:
  ```bash
  python run_experiment.py --config configs/experiment.yaml
  ```
- **8-Phase Verification Pipeline**: Executes 50 sequential checks (5 temporal-state axiom checks + 45 model verification checks) across temporal-state axioms, flat/curved baselines, boosts, Kirkwood-Dirac optimization, Transfer Tensor Method (TTM) non-Markovianity, Rust sidecars, and scientific audit reviews.
- **Strict Verdict Resolution**: Propagates execution status (`PASS`, `FAIL`, `SKIPPED`, `DEGRADED_PASS`) to determine the overall experimental outcome.
- **Optional & local integrations**: optional backends enrich a run when installed; the pipeline degrades cleanly without them and records which backend was used in `result.json` (`audit_context`).
  - **Scientific compliance audit** (`spar-framework`, optional `[audit]` extra): produces a bounded, environment-dependent **review signal** over gate outputs and report text, including a normalized claim-drift score. When the framework is absent, a local deterministic mock runs and the result is marked `backend_mode: "mock"`. This is a review signal, **not** external physical validation.
  - **Accessibility scoring** (local): derives an accessibility score from gate status with non-Markovianity, KD-negativity, and risk penalties.
  - **Differentiable governance engine** (`flame_torch`, externally provisioned, optional): a covenant check on flat-baseline purity; skipped and reported as `SKIPPED` when not installed.
- **Rust Sidecar Vector Search**: Subprocess execution of the `turbovec`-powered `rust_verify` package comparing exact dot products against quantized similarity search.

---

## Directory Structure

```
QSOT-Harness/
├── .github/workflows/       # CI/CD pipelines
│   └── ci.yml
├── configs/                 # YAML configuration presets
│   └── experiment.yaml
├── reports/                 # Raw and rendered outputs (result.json, report.md)
├── src/qsot_v2/
│   ├── cli/                 # Argparse and run script entrypoints
│   ├── core/                # Configuration, Results schema, and Phase Runner
│   ├── physics/             # Evolution, Channels, Accessibility, Optimizer, and Scientific Audit
│   ├── reports/             # Jinja2 template and markdown rendering
│   └── rust_sidecar/        # Cargo sidecar implementing turbovec search
└── tests/                   # Complete unit and integration test suite
```

---

## Quick Start

### 1. Installation

Activate the Python virtual environment and install dependencies:
```powershell
# Windows
.\venv\Scripts\Activate.ps1
pip install -e .[dev,torch]
```

### 2. Build the Rust Sidecar

Build the sidecar binary using the virtualenv context:
```powershell
cd src/qsot_v2/rust_sidecar
cargo build --release
cd ../../..
```

### 3. Run Experiments

Execute the full verification suite against the background presets:
```bash
python run_experiment.py --config configs/experiment.yaml
```

The outputs will be generated inside the `reports/` folder:
- `reports/result.json`: Comprehensive machine-readable execution details and NumPy-sanitized metrics.
- `reports/report.md`: Beautiful, human-readable summary of checks and physics interpretations.

---

## 8-Phase Physics Pipeline

0. **Phase 0: Temporal-State Axioms**: Evaluates temporal quantum evolution representation validity under explicit mathematical constraints (Linearity, CPTP, Trace preservation, Conditionability consistency, and Density matrix validity).
1. **Phase 1: Flat Baselines**: Establishes rest and boosted flat spacetime limits ($P=1.0, S=0$).
2. **Phase 2: Curvature Noise**: Drives state purity decay and entropy growth across de Sitter, Schwarzschild, AdS5, and Eguchi-Hanson metrics.
3. **Phase 3: Relativistic Boosts**: Checks that, within the implemented model, high-velocity observers experience increased effective noise.
4. **Phase 4: Kirkwood-Dirac (flat-relative)**: Runs a bounded basis-search optimization and reports the de-Sitter-minus-flat KD delta as a relative signal under the implemented model — not a contextuality proof. Optimizer convergence is labeled explicitly (a non-converged run is surfaced as `DEGRADED_PASS`).
5. **Phase 5: TTM & Accessibility**: Uses Transfer Tensors to measure memory depth and determines accessibility.
6. **Phase 6: Rust turbovec**: Tests vector search quantization limits under the `turbovec` sidecar.
7. **Phase 7: Scientific Audit**: Compares each background's gate outputs and residuals against the project's own predefined expected-behavior table, producing a bounded, environment-dependent review signal — not external ground truth.

---

## Running Tests

Run the complete suite of tests and check coverage:
```bash
python -m pytest --cov=qsot_v2 --cov-report=term-missing
```
*Coverage is gated at 90% (`--cov-fail-under=90` in `pyproject.toml`); the current suite measures ~94%.*
