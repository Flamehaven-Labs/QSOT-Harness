"""Physics engine: KrausChannel, MetricToChannelMap, BackgroundField, QuantumCircuit, QuantumState."""

from __future__ import annotations

from qsot_v2.physics.accessibility import compute_accessibility_score
from qsot_v2.physics.background import run_background_verify
from qsot_v2.physics.beta_residual import BetaResidualVerifier
from qsot_v2.physics.channels import (
    BACKGROUND_BUILDERS,
    BackgroundField,
    KrausChannel,
    MetricToChannelMap,
)
from qsot_v2.physics.memory_kernel import compute_memory_kernel
from qsot_v2.physics.optimizer import TORCH_AVAILABLE, run_kd_optimization
from qsot_v2.physics.quantum import QuantumCircuit, QuantumState
from qsot_v2.physics.scientific_audit import (
    ScientificAuditResult,
    get_audit_backend_info,
    get_audit_runtime,
    run_scientific_audit,
)

__all__ = [
    "BackgroundField",
    "KrausChannel",
    "MetricToChannelMap",
    "BACKGROUND_BUILDERS",
    "QuantumCircuit",
    "QuantumState",
    "run_background_verify",
    "BetaResidualVerifier",
    "run_kd_optimization",
    "TORCH_AVAILABLE",
    "run_scientific_audit",
    "get_audit_runtime",
    "get_audit_backend_info",
    "ScientificAuditResult",
    "compute_memory_kernel",
    "compute_accessibility_score",
]
