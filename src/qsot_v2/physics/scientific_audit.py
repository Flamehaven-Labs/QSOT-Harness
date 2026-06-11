"""Scientific audit framework integration/mock adapter.

Provides a fallback to a local deterministic mock when the external compliance
framework (spar-framework) is not importable.

Epistemic scope (Stage A): audit outputs are bounded, environment-dependent
review signals -- evidence class ``external_review_signal``. They do not establish
external physical validity. See ``docs/stage_a_masterplan.md`` (P-1).

Normalization authority lives here: every numeric output is normalized to the
unit interval inside this module so phase code only serializes and evaluates
verdicts (it never performs scale conversion).
"""
from __future__ import annotations

import logging
import warnings
from dataclasses import dataclass
from typing import Any, Literal

logger = logging.getLogger(__name__)

ScaleLabel = Literal["unit_interval", "percentage", "unknown"]
VerdictLabel = Literal["ACCEPT", "MINOR_REVISION", "REJECT", "UNKNOWN"]
BackendMode = Literal["mock", "external"]
EvidenceClass = Literal["external_review_signal"]

# Bounded allowed-value sets (runtime guard; Literal types are static-only).
ALLOWED_VERDICTS = ("ACCEPT", "MINOR_REVISION", "REJECT", "UNKNOWN")
ALLOWED_SCALES = ("unit_interval", "percentage", "unknown")
ALLOWED_BACKEND_MODES = ("mock", "external")
ALLOWED_EVIDENCE_CLASSES = ("external_review_signal",)

# --- Backend policy constants -------------------------------------------------
# backend_available is determined at runtime (import success).
# dependency_declared is a fixed POLICY statement and is NOT derived from runtime
# pyproject parsing.
#
#   - spar-framework is published on PyPI and is declared as the optional extra
#     [audit] in pyproject.toml -> dependency_declared = True.
#   - The external mock uses the unit interval; spar-framework reports on a
#     percentage scale.
AUDIT_BACKEND_EXTERNAL_NAME = "spar_framework"
AUDIT_BACKEND_MOCK_NAME = "qsot_v2_mock_audit"
AUDIT_DEPENDENCY_DECLARED = True
AUDIT_EXTERNAL_SCORE_SCALE: ScaleLabel = "percentage"
AUDIT_MOCK_SCORE_SCALE: ScaleLabel = "unit_interval"


def _normalize(value: float, scale: ScaleLabel) -> float:
    """Map a raw value onto the unit interval according to its declared scale."""
    if scale == "percentage":
        return value / 100.0
    # unit_interval and unknown pass through unchanged.
    return value


def _external_audit_available() -> bool:
    """Runtime check: is the external review *engine* importable?"""
    try:
        import spar_framework.engine  # noqa: F401
        return True
    except ImportError:
        return False


def _external_runtime_available() -> bool:
    """Runtime check: is the external review *runtime carrier* importable?

    This is a distinct dependency from the engine: the engine
    (``spar_framework.engine``) can be present while the domain runtime
    (``spar_domain_physics.runtime``) is absent. We surface both so the JSON
    never silently claims a fully external stack when the runtime is the local
    fallback (P-1 finding 2).
    """
    try:
        import spar_domain_physics.runtime  # noqa: F401
        return True
    except ImportError:
        return False


@dataclass
class ScientificAuditResult:
    verdict: VerdictLabel
    raw_score: float
    normalized_score: float
    raw_score_scale: ScaleLabel
    claim_drift_raw: float
    claim_drift_normalized: float
    claim_drift_scale: ScaleLabel
    coverage_rate: float
    backend_mode: BackendMode
    backend_name: str
    evidence_class: EvidenceClass = "external_review_signal"

    def __post_init__(self) -> None:
        # Schema-anchor hardening (P-1): an unrecognized external verdict is
        # coerced to UNKNOWN rather than leaking an arbitrary label into
        # result.json. Internally-controlled labels must never drift -- a
        # violation there is a programming error, so it raises.
        if self.verdict not in ALLOWED_VERDICTS:
            warnings.warn(
                f"Unrecognized audit verdict '{self.verdict}' coerced to 'UNKNOWN'.",
                RuntimeWarning,
                stacklevel=2,
            )
            self.verdict = "UNKNOWN"
        if self.backend_mode not in ALLOWED_BACKEND_MODES:
            raise ValueError(f"Invalid backend_mode: {self.backend_mode!r}")
        if self.evidence_class not in ALLOWED_EVIDENCE_CLASSES:
            raise ValueError(f"Invalid evidence_class: {self.evidence_class!r}")
        if self.raw_score_scale not in ALLOWED_SCALES:
            raise ValueError(f"Invalid raw_score_scale: {self.raw_score_scale!r}")
        if self.claim_drift_scale not in ALLOWED_SCALES:
            raise ValueError(f"Invalid claim_drift_scale: {self.claim_drift_scale!r}")

    def to_entry(self, expected_verdict: str) -> dict:
        """Serialize one per-background review entry (schema-stable across backends)."""
        return {
            "verdict": self.verdict,
            "expected_verdict": expected_verdict,
            "raw_score": self.raw_score,
            "normalized_score": self.normalized_score,
            "raw_score_scale": self.raw_score_scale,
            "claim_drift_raw": self.claim_drift_raw,
            "claim_drift_normalized": self.claim_drift_normalized,
            "claim_drift_scale": self.claim_drift_scale,
            "coverage_rate": self.coverage_rate,
            "evidence_class": self.evidence_class,
            "backend_mode": self.backend_mode,
        }


def get_audit_backend_info() -> dict:
    """Top-level audit backend context for ``audit_context.scientific_audit``.

    backend_mode/backend_available are runtime-resolved; dependency_declared and
    claim_scope are policy-fixed.
    """
    from qsot_v2.core.evidence import RUNTIME_DEPENDENCY_STATUS

    available = _external_audit_available()
    runtime_available = _external_runtime_available()
    return {
        "backend_name": AUDIT_BACKEND_EXTERNAL_NAME if available else AUDIT_BACKEND_MOCK_NAME,
        "backend_mode": "external" if available else "mock",
        "backend_available": available,
        # The runtime carrier is a separate dependency; surface it explicitly so
        # an external engine + local-fallback runtime is never reported as a
        # uniformly external stack.
        "runtime_backend": "spar_domain_physics" if runtime_available else "local_fallback",
        "runtime_backend_available": runtime_available,
        "dependency_declared": AUDIT_DEPENDENCY_DECLARED,
        "raw_score_scale": AUDIT_EXTERNAL_SCORE_SCALE if available else AUDIT_MOCK_SCORE_SCALE,
        "normalized_score_scale": "unit_interval",
        "claim_scope": "external_review_signal_only",
        # This block describes dependency presence/declaration, not a review
        # signal itself (Packet D); canonical class from core.evidence.
        "evidence_class": RUNTIME_DEPENDENCY_STATUS,
    }


class AuditRuntime:
    pass


def get_audit_runtime() -> AuditRuntime:
    try:
        from spar_domain_physics.runtime import get_review_runtime as get_real_runtime
        return get_real_runtime()
    except ImportError:
        return AuditRuntime()


def _physics_constraint_overrides_accept(subject: dict) -> bool:
    """Whether physical constraints force ACCEPT -> MINOR_REVISION."""
    physics = subject.get("physics", {})
    ricci_norm = (
        subject["ricci_norm"]
        if subject.get("ricci_norm") is not None
        else physics.get("ricci_norm", 0.0)
    )
    has_ctc = subject.get("has_ctc") or physics.get("ctc_status") == "DETECTED"
    gs_anomaly = subject.get("gs_anomaly_flag") or physics.get("gs_anomaly_flag", False)
    return bool(has_ctc or gs_anomaly or ricci_norm > 0.0)


def run_scientific_audit(
    runtime: Any,
    subject: dict,
    source: str,
    gate: str,
    report_text: str,
) -> ScientificAuditResult:
    from qsot_v2.theory.claim_boundary import CLAIM_BOUNDARY
    is_empty = not subject or all(k == "claim_boundary" for k in subject)
    if "claim_boundary" not in subject:
        subject["claim_boundary"] = CLAIM_BOUNDARY

    try:
        from spar_framework.engine import run_review as run_real_review
        res = run_real_review(
            runtime=runtime,
            subject=subject,
            source=source,
            gate=gate,
            report_text=report_text,
        )
        # Align the external verdict with our physical constraints to prevent
        # environment drift between mock and external backends.
        verdict = res.verdict
        if verdict == "ACCEPT" and _physics_constraint_overrides_accept(subject):
            verdict = "MINOR_REVISION"

        raw_score = float(getattr(res, "score", 95.0))
        raw_drift = float(getattr(res, "claim_drift", 0.0))
        coverage = float(getattr(res, "coverage_rate", 1.0))
        return ScientificAuditResult(
            verdict=verdict,
            raw_score=raw_score,
            normalized_score=_normalize(raw_score, AUDIT_EXTERNAL_SCORE_SCALE),
            raw_score_scale=AUDIT_EXTERNAL_SCORE_SCALE,
            claim_drift_raw=raw_drift,
            claim_drift_normalized=_normalize(raw_drift, AUDIT_EXTERNAL_SCORE_SCALE),
            claim_drift_scale=AUDIT_EXTERNAL_SCORE_SCALE,
            coverage_rate=coverage,
            backend_mode="external",
            backend_name=AUDIT_BACKEND_EXTERNAL_NAME,
        )
    except ImportError:
        # Mock -- unit interval, dynamic classification only (no name-based fallback).
        #
        # subject formats accepted:
        #   (a) flat dict  {"ricci_norm": float, "gs_anomaly_flag": bool, "has_ctc": bool, ...}
        #   (b) nested     {"physics": {"ricci_norm": ..., "ctc_status": ..., ...}}
        #   (c) empty {}   -- unverifiable; coverage_rate = 0.0, verdict = MINOR_REVISION
        if is_empty:
            warnings.warn(
                f"Empty subject passed to run_scientific_audit for source '{source}'.",
                DeprecationWarning,
                stacklevel=2,
            )
            return ScientificAuditResult(
                verdict="MINOR_REVISION",
                raw_score=0.95,
                normalized_score=0.95,
                raw_score_scale=AUDIT_MOCK_SCORE_SCALE,
                claim_drift_raw=0.02,
                claim_drift_normalized=0.02,
                claim_drift_scale=AUDIT_MOCK_SCORE_SCALE,
                coverage_rate=0.0,
                backend_mode="mock",
                backend_name=AUDIT_BACKEND_MOCK_NAME,
            )

        verdict = "MINOR_REVISION" if _physics_constraint_overrides_accept(subject) else "ACCEPT"
        return ScientificAuditResult(
            verdict=verdict,
            raw_score=0.95,
            normalized_score=0.95,
            raw_score_scale=AUDIT_MOCK_SCORE_SCALE,
            claim_drift_raw=0.02,
            claim_drift_normalized=0.02,
            claim_drift_scale=AUDIT_MOCK_SCORE_SCALE,
            coverage_rate=1.0,
            backend_mode="mock",
            backend_name=AUDIT_BACKEND_MOCK_NAME,
        )
