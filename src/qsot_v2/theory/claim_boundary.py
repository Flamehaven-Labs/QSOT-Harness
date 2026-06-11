"""Explicit claim boundary constants for QSOT Compiler V2.1."""

from __future__ import annotations

EXTERNAL_PHYSICAL_VALIDITY_CLAIMED: bool = False
EXECUTION_PROVES_NEW_LAW: bool = False
MODEL_OUTPUT_CONSISTENCY_ONLY: bool = True
MODEL_HAS_PHENOMENOLOGICAL_CHANNEL_MAP: bool = True
EXTERNAL_EXPERIMENTAL_VALIDATION_PROVIDED: bool = False

# Combined boundary dict for serialization and audits
CLAIM_BOUNDARY = {
    "external_physical_validity_claimed": EXTERNAL_PHYSICAL_VALIDITY_CLAIMED,
    "execution_proves_new_law": EXECUTION_PROVES_NEW_LAW,
    "model_output_consistency_only": MODEL_OUTPUT_CONSISTENCY_ONLY,
    "model_has_phenomenological_channel_map": MODEL_HAS_PHENOMENOLOGICAL_CHANNEL_MAP,
    "external_experimental_validation_provided": EXTERNAL_EXPERIMENTAL_VALIDATION_PROVIDED,
}
