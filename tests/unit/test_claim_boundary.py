"""Unit tests for claim boundaries and non-claims."""

from __future__ import annotations

from qsot_v2.theory.claim_boundary import (
    CLAIM_BOUNDARY,
    EXECUTION_PROVES_NEW_LAW,
    EXTERNAL_EXPERIMENTAL_VALIDATION_PROVIDED,
    EXTERNAL_PHYSICAL_VALIDITY_CLAIMED,
    MODEL_HAS_PHENOMENOLOGICAL_CHANNEL_MAP,
    MODEL_OUTPUT_CONSISTENCY_ONLY,
)


def test_claim_boundary_nonclaims_are_false():
    """Assert that non-claims are explicitly False to prevent physical over-claiming."""
    assert EXTERNAL_PHYSICAL_VALIDITY_CLAIMED is False
    assert EXECUTION_PROVES_NEW_LAW is False
    assert EXTERNAL_EXPERIMENTAL_VALIDATION_PROVIDED is False

    # Assert consistency checks are enabled
    assert MODEL_OUTPUT_CONSISTENCY_ONLY is True
    assert MODEL_HAS_PHENOMENOLOGICAL_CHANNEL_MAP is True

    # Assert dictionary alignment
    assert CLAIM_BOUNDARY["external_physical_validity_claimed"] is False
    assert CLAIM_BOUNDARY["execution_proves_new_law"] is False
    assert CLAIM_BOUNDARY["external_experimental_validation_provided"] is False
    assert CLAIM_BOUNDARY["model_output_consistency_only"] is True
    assert CLAIM_BOUNDARY["model_has_phenomenological_channel_map"] is True
