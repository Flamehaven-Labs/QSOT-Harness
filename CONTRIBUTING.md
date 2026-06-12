# Contributing to QSOT-Harness

Thank you for contributing to QSOT-Harness (QSOT: *Quantum State Over Time*)! Below are the guidelines for developing, testing, and verifying changes.

---

## Onboarding & Setup

1. **Activate the Virtual Environment**:
   Always execute development commands within the virtual environment context to ensure dependency isolation:
   ```powershell
   # Windows PowerShell
   .\venv\Scripts\Activate.ps1
   ```

2. **Install Editable Package**:
   ```bash
   pip install -e .[dev,torch]
   ```

3. **Rust Sidecar Build**:
   When modifying or building the sidecar binary, navigate to its directory and run:
   ```powershell
   cd src/qsot_v2/rust_sidecar
   cargo build --release
   ```

---

## Code Quality Standards

- **Formatting & Linting**: We use `ruff` to lint the code. Run before committing:
  ```bash
  ruff check src/
  ```
- **Typing**: Run `mypy` to verify type annotations:
  ```bash
  mypy src/
  ```

---

## Testing & Coverage

We enforce a strict **90%+ test coverage** constraint on all python packages.

1. **Run Pytest**:
   ```bash
   python -m pytest --cov=qsot_v2 --cov-report=term-missing
   ```
2. **Reviewing Coverage**:
   - Ensure new physics modules, configuration keys, or reporting renderer branches are covered by unit tests inside `tests/unit/`.
   - Ensure full CLI pipelines are validated inside `tests/integration/test_integration.py` to cover end-to-end execution.

---

## Modifying Physics Engines & Presets

- If adding or refining a spacetime background, update the mappings in `src/qsot_v2/physics/background.py` and the corresponding unit test assertions in `tests/unit/test_physics.py`.
- If modifying the scientific audit review rules, ensure the expected-behavior anchors match the project's own verification policy. These are the project's predefined expectations (a bounded review signal), not external ground truth.
- Ensure that density matrices are not directly exposed in `result.observations` to prevent complex-value JSON serialization errors.
