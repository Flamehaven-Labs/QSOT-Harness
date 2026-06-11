"""QSOT Compiler V2 — CLI-First Quantum Experiment Runner.

V2 changes vs V1:
  - No Streamlit dashboard, no REST API server
  - CLI: python run_experiment.py --config experiment.yaml
  - Output: result.json + report.md (+ optional report.pdf via pandoc)
  - Physics: Full QGB pipeline (BackgroundField -> MetricToChannelMap)
  - Rust sidecar: turbovec subprocess + JSON file exchange (unchanged)
  - Tests: pytest 90%+ coverage target
"""

__version__ = "2.1.0"
__author__ = "Quantum-Audit-Labs"
