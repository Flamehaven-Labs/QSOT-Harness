# Temporal-State Axiom Contract

The **Temporal-State candidate principle** (QSOT) represents quantum evolution not simply as a parameterized transition over an external time parameter, but as a representation possibility within a constrained multipartite temporal-state structure.

QSOT 2.1 introduces a **Temporal-State Axiom Contract Layer** (Phase 0) to evaluate whether such representation is contract-preserving under explicitly bounded model assumptions. It serves as a falsification harness rather than a physical proof.

## Core Axioms

Phase 0 enforces five required mathematical checks on the quantum maps:

### 1. Linearity
Quantum maps representing temporal transitions must satisfy linearity over state mixtures:
$$\mathcal{E}(\alpha \rho_a + (1-\alpha) \rho_b) = \alpha \mathcal{E}(\rho_a) + (1-\alpha) \mathcal{E}(\rho_b)$$

### 2. CPTP Completeness
The Kraus operators $\{K_i\}$ constituting the channel must satisfy the completeness relation:
$$\sum_i K_i^\dagger K_i = I$$

### 3. Trace Preservation
For all valid test density matrices $\rho$, the evolved state must have unit trace:
$$\text{Tr}(\mathcal{E}(\rho)) = 1$$

### 4. Trajectory and Composed-Channel Consistency (Conditionability)
The conditionability check verifies trajectory and composed-channel consistency under the implemented model. It does not by itself prove a physical theorem about time:
- **1-step Replay**: $\rho_{i+1} \approx \mathcal{E}_i(\rho_i)$
- **2-step Conditionability**: $\rho_{i+2} \approx \mathcal{E}_{i+1}(\mathcal{E}_i(\rho_i))$
- **Composition Consistency**: $\mathcal{E}_b(\mathcal{E}_a(\rho)) \approx \mathcal{E}_{ba}(\rho)$

### 5. Density Matrix Validity
All states generated along the temporal trajectory must be mathematically valid density matrices:
- Hermitian: $\rho = \rho^\dagger$
- Trace: $\text{Tr}(\rho) = 1$
- Positive Semi-Definite (PSD): $\rho \ge 0$

---

## Mathematical Validity vs. Gate Verdicts

Phase 0 checks focus strictly on **channel mathematical validity** (CPTP completeness, trace preservation, linearity, and density validity). 
It does not assess classical gravitational anomalies, CTCs, or moduli stability (which are evaluated at the gate level in Phase 2 and audited in Phase 7). 

For example:
- **Eguchi-Hanson**: Evaluates to `MINOR_REVISION` in Phase 7 due to its gravitational anomaly (`gs_anomaly_flag = True`).
- **Phase 0 Status**: The metric-to-channel mapping produces mathematically valid, trace-preserving CPTP Kraus operators for Eguchi-Hanson. Therefore, Phase 0 checks correctly pass for the Eguchi-Hanson scenario. 

This decoupling ensures that Phase 0 functions purely as a mathematical regression harness for the channel mapping equations, independent of the background's physical acceptability.
