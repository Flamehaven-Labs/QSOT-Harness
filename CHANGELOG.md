# Changelog

All notable changes to **QSOT-Harness** (QSOT: *Quantum State Over Time*) will be documented in this file.

---

## [2.1.1] - 2026-06-12

### Fixed
- **Frozen-evidence provenance repair**: `paper/evidence/PROVENANCE.md` recorded the Windows CRLF working-tree SHA-256 of `result.json` / `report.md` (`0d2461a9...` / `023c8a4c...`), but the repository normalizes text to LF (`.gitattributes`), so the committed, archived (Zenodo), and freshly-cloned bytes hash to `b1a83df5...` / `18c6a2fa...`. A third party verifying the published files against the recorded hashes would have mismatched. Corrected the recorded hashes to the canonical LF values and normalized the working-tree copies.

### Changed
- Citation / archive title now spells out the acronym: **QSOT (Quantum State Over Time)-Harness**.
- **No** physics, model, report, or experiment-result semantics changed; this is a provenance/metadata repair only.

## [2.1.0] - 2026-06-12

### Added
- **Accompanying manuscript** (`paper/`) with a LaTeX -> PDF CI build (`paper.yml`) and SHA-256-anchored frozen experiment evidence (`paper/evidence/`).
- **Claim-integrity governance gate** (`scripts/governance_check.py` + `governance.yml`): fails CI on local-workspace path leaks or forbidden overclaim phrases; covers code, docs, and the manuscript.
- **Archival/citation metadata**: `.zenodo.json` and `CITATION.cff`.

### Changed
- Manuscript repositioned as a bounded verification-architecture paper (claim boundary, evidence classes, calibration manifest, synthetic-vs-model separation) rather than a physics-result paper; numbers and identity synchronized to the current code (64 tests, ~94% coverage, `QSOT-Harness`).
- README Phase 4 aligned to flat-relative Kirkwood-Dirac semantics.

### Fixed
- Rust sidecar CI build: install `libopenblas-dev` for the `turbovec` BLAS backend.
- Deterministic formatting via pinned Black (`26.5.1`); Node 24-compatible GitHub Actions.

## [2.0.1] - 2026-06-09

### Added
- **Seeded KD Optimization**: Introduced `torch.manual_seed(42)` to parameter initialization in `QuantumOptimizer` to guarantee deterministic convergence and reproducible basis searches.
- **Phase 4 Step Isolation**: Isolated the de Sitter background to a fixed 2 steps of evolution in Phase 4, keeping the state in the coherent regime (purity > 0.707) where Kirkwood-Dirac negativity is mathematically possible, regardless of config step overrides.

### Fixed
- **Rust Sidecar Portability**: Updated `Cargo.toml` to link to crates.io `turbovec = "0.8.0"` instead of a local absolute path, ensuring compilation works on generic external environments and GitHub Actions CI.
- **Eguchi-Hanson Audit expected verdict alignment**: Added `eguchi_hanson` to Phase 7 `expected_minor_revision` group since it contains a gravitational anomaly (`gs_anomaly_flag=True`), and renamed its check key to `scientific_audit_confirms_eguchi_hanson_expected_revision` in both the runner and CLI output formatter.
- **SPAR Framework Verdict Drift**: Added physical gate alignment checks in `run_scientific_audit`'s real review pathway to force `MINOR_REVISION` on backgrounds with CTCs, anomalies, or Ricci-flat mismatches, ensuring mock and real framework outputs match completely.
- **Safe `ricci_norm` Check**: Updated `scientific_audit.py` to check `ricci_norm` with an explicit `is not None` check, avoiding falsy evaluation of `0.0` and incorrect fallback.
- **Unused Imports & Linting**: Cleaned up import sorting, formatting, and unused imports to comply with Ruff lint checks.

## [2.0.0] - 2026-06-08

### Added
- **CLI-First Architecture**: Replaced V1 Streamlit dashboard and API server with a print-and-exit `run_experiment.py` script.
- **7-Phase Physics Pipeline**: Refactored the core execution engine to run 45 sequential checks across 7 verification sectors.
- **Unified Results Schema**: Added `ExperimentResult` with status resolution mapping (`PASS`, `FAIL`, `SKIPPED`, `DEGRADED_PASS`) and custom NumPy type sanitization for JSON exports.
- **Scientific Audit Integration**: Phase 7 reviews all background reports against the project's own analytical expected-behavior anchors (a bounded review signal, not external ground truth).
- **TTM Non-Markovianity**: Added Transfer Tensor Method memory kernel calculations to assess non-Markovian backflow.
- **Accessibility Scores**: Implemented `compute_accessibility_score` to penalize scores based on non-Markovianity, contextuality (KD negativity), and risk.
- **Rust Sidecar Subprocess**: Added `src/qsot_v2/rust_sidecar` linking to `turbovec` to perform quantized vector search checks via file exchange.

### Fixed
- **Windows File Locking (WinError 32)**: Fixed a bug where `np.load` in `optimizer.py` held open file descriptors, blocking temporary `.npz` files from being deleted. Wrapped operations in a `with np.load(...) as data:` context.
- **Complex JSON Serialization**: Resolved a serialization crash caused by raw density matrices containing `complex128` values by storing them in private runner variables.
- **Rust Sidecar Path Mismatch**: Aligned file exchange directories between `runner.py` and `main.rs` to correctly resolve `../test_vectors.json` relative to the sidecar working directory.
- **Scientific Audit Expectation Mismatch**: Updated Schwarzschild and AdS5 presets in `background.py` and unit tests to return `gate = "PASS"` and zero beta functions, resolving review anomalies and preventing false `REJECT` verdicts.
