"""Evidence-class taxonomy and per-observation registry (Packet D).

Every major reported signal carries an explicit epistemic label so a reader can
tell, per value, what kind of evidence it is. Stage A uses a hybrid scheme:

  * P-1 blocks that already embed ``evidence_class`` inline keep it
    (scientific_audit_reviews entries, dqe_runtime, audit_context blocks).
  * Remaining raw observation blocks are labeled by the top-level
    ``evidence_classes`` registry built from ``OBSERVATION_EVIDENCE_CLASS`` here.

This module is the single source of truth for the vocabulary and the mapping.
"""
from __future__ import annotations

from typing import Dict

# Bounded vocabulary (the only labels allowed anywhere in a result).
EVIDENCE_CLASSES = (
    "mathematical_invariant",       # exact algebraic property of the representation
    "phenomenological_model_output",  # output of the phenomenological channel map
    "policy_derived_classification",  # gate / admissibility / decree from rule-based policy
    "synthetic_harness_output",     # value from an injected / generated test scenario
    "external_review_signal",       # bounded, environment-dependent external audit signal
    "optional_engine_check",        # result of an optional governance-engine validation
    "runtime_dependency_status",    # which runtime dependencies are present / declared
)

# Observation block key -> evidence class. Only *major* signals are listed;
# incidental values (parameters used, free-text notes, raw stdout) intentionally
# carry no class, mirroring the credibility-architecture rule that incidental
# values are unlabeled.
OBSERVATION_EVIDENCE_CLASS: Dict[str, str] = {
    # Phase 0: exact algebraic properties of the temporal-state channel.
    "phase0_scenarios": "mathematical_invariant",
    "linearity_max_deviation": "mathematical_invariant",
    "cptp_completeness_max_deviation": "mathematical_invariant",
    "trace_preservation_max_deviation": "mathematical_invariant",
    "composed_channel_max_deviation": "mathematical_invariant",
    "sequential_replay_max_deviation": "mathematical_invariant",
    "two_step_conditionability_max_deviation": "mathematical_invariant",
    # Phenomenological channel-map outputs (purity / entropy / KD).
    "flat_rest_purities": "phenomenological_model_output",
    "flat_rest_entropies": "phenomenological_model_output",
    "flat_boost_purities": "phenomenological_model_output",
    "schwarz_purity": "phenomenological_model_output",
    "desitter_purity": "phenomenological_model_output",
    "ads_purity": "phenomenological_model_output",
    "eguchi_purity": "phenomenological_model_output",
    "schwarz_entropy": "phenomenological_model_output",
    "desitter_entropy": "phenomenological_model_output",
    "ads_entropy": "phenomenological_model_output",
    "eguchi_entropy": "phenomenological_model_output",
    "kd_flat": "phenomenological_model_output",
    "kd_desitter": "phenomenological_model_output",
    "kd_delta": "phenomenological_model_output",
    "memory_kernel_model_trajectory": "phenomenological_model_output",
    # Boost / curvature channel-map numerics (no gate logic in the block).
    "ads_boost_info": "phenomenological_model_output",
    "schwarz_rest_info": "phenomenological_model_output",
    # Background verification blocks: the headline is a rule-based gate /
    # admissibility / decree (policy), not a physics measurement. The physics
    # sub-dict they carry is duplicated by the labeled scalar observations above.
    "flat_verify": "policy_derived_classification",
    "schwarzschild_verify": "policy_derived_classification",
    "desitter_verify": "policy_derived_classification",
    "ads5_verify": "policy_derived_classification",
    "godel_verify": "policy_derived_classification",
    "eguchi_verify": "policy_derived_classification",
    # Synthetic harness outputs (injected backflow / generated test vectors).
    "memory_kernel": "synthetic_harness_output",
    "accessibility_scores": "synthetic_harness_output",
    "rust_turbovec_result": "synthetic_harness_output",
    # External review signal (also labeled inline on each per-background entry).
    "scientific_audit_reviews": "external_review_signal",
    # Optional governance-engine check (also labeled inline on the block).
    "dqe_runtime": "optional_engine_check",
}

# The runtime_dependency_status class is carried inline on the audit_context
# backend descriptor blocks (scientific_audit, dqe_covenant), not via the
# observation registry. Kept here so the literal stays consistent.
RUNTIME_DEPENDENCY_STATUS = "runtime_dependency_status"


def build_evidence_registry(observations: Dict[str, object]) -> Dict[str, str]:
    """Return {observation_key: evidence_class} for the major blocks present.

    Unmapped (incidental) observations are omitted. A mapped class outside the
    bounded vocabulary is a programming error and raises.
    """
    registry: Dict[str, str] = {}
    for key in observations:
        cls = OBSERVATION_EVIDENCE_CLASS.get(key)
        if cls is None:
            continue
        if cls not in EVIDENCE_CLASSES:
            raise ValueError(f"Unknown evidence class {cls!r} for observation {key!r}")
        registry[key] = cls
    return registry
