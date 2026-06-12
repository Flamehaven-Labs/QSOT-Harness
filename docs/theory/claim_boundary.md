# Bounded Model Assumptions and Claim Control

QSOT-Harness (QSOT: *Quantum State Over Time*) implements a strict claim control boundary to prevent over-claiming and name-based physics validation anomalies.

## Claim Boundaries (`claim_boundary.py`)

The codebase enforces the following constants representing the scope of the simulation:

- **`EXTERNAL_PHYSICAL_VALIDITY_CLAIMED = False`**: The execution of this model is phenomenological and does not claim to represent verified external physical spacetimes.
- **`EXECUTION_PROVES_NEW_LAW = False`**: Code execution verifies mathematical consistency, not the validation of a new physical law of time.
- **`MODEL_OUTPUT_CONSISTENCY_ONLY = True`**: Assesses only whether outputs match internal model assumptions.
- **`MODEL_HAS_PHENOMENOLOGICAL_CHANNEL_MAP = True`**: The curvature-to-channel mapping (using Riemann norm as a proxy for tidal curvature) is a phenomenological assumption, not a first-principles derivation.
- **`EXTERNAL_EXPERIMENTAL_VALIDATION_PROVIDED = False`**: No external laboratory validation is provided.

## Automation and Propagation

These constants are automatically connected to all outputs:
1. **JSON Output (`result.json`)**: Embedded directly under the `"claim_boundary"` key.
2. **Markdown Report (`report.md`)**: A prominent **Scope Note** banner is automatically rendered at the top of the report.
3. **Scientific Audit (`scientific_audit.py`)**: Included inside the review `subject` metadata, allowing audit engines to evaluate the claims in context.
