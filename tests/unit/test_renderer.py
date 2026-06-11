"""Unit tests for ReportRenderer class."""

from __future__ import annotations

import tempfile
from pathlib import Path

from qsot_v2.core.results import ExperimentResult
from qsot_v2.reports.renderer import ReportRenderer


def test_renderer():
    with tempfile.TemporaryDirectory() as td:
        out_dir = Path(td)
        result = ExperimentResult(experiment_id="test-exp")
        result.checks = {"check_0": "PASS"}
        result.observations = {"obs_0": 4.2}

        renderer = ReportRenderer()
        paths = renderer.render(result, out_dir, ["json", "md"])

        assert "json" in paths
        assert "md" in paths
        assert paths["json"].exists()
        assert paths["md"].exists()

        # Check content
        import json

        data = json.loads(paths["json"].read_text())
        assert data["experiment_id"] == "test-exp"
        assert data["verdict"] == "PASS"

        md_content = paths["md"].read_text()
        assert "Quantum Geometry & Entropy Verification Report" in md_content
        assert "check_0" in md_content
