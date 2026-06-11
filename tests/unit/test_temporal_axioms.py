"""Unit tests for Temporal-State Axioms verifier and Phase 0 checks."""

from __future__ import annotations

import numpy as np

from qsot_v2.theory.axioms import TemporalStateAxiomVerifier
from qsot_v2.theory.falsification import run_phase0_checks


def test_linearity_passes_for_valid_kraus_channel():
    verifier = TemporalStateAxiomVerifier()
    # E(rho) = I @ rho @ I
    kraus = [np.eye(2)]

    def valid_map(rho):
        return sum(k @ rho @ k.conj().T for k in kraus)

    rho_a = np.array([[1.0, 0.0], [0.0, 0.0]], dtype=complex)
    rho_b = np.array([[0.0, 0.0], [0.0, 1.0]], dtype=complex)

    assert verifier.check_linearity(rho_a, rho_b, valid_map) is True


def test_linearity_fails_for_nonlinear_map():
    verifier = TemporalStateAxiomVerifier()

    # E(rho) = rho^2 (Non-linear map)
    def nonlinear_map(rho):
        return rho @ rho

    rho_a = np.array([[1.0, 0.0], [0.0, 0.0]], dtype=complex)
    rho_b = np.array([[0.0, 0.0], [0.0, 1.0]], dtype=complex)

    assert verifier.check_linearity(rho_a, rho_b, nonlinear_map) is False


def test_cptp_completeness_fails_for_broken_kraus():
    verifier = TemporalStateAxiomVerifier()

    # K_0 = 0.5 * I -> sum(K^dag K) = 0.25 * I != I
    broken_kraus = [0.5 * np.eye(2)]
    assert verifier.check_cptp_completeness(broken_kraus) is False

    # Empty list
    assert verifier.check_cptp_completeness([]) is False


def test_trace_preservation_fails_for_leaky_channel():
    verifier = TemporalStateAxiomVerifier()

    # leaky Kraus: sum(K^dag K) = 0.9 * I
    leaky_kraus = [np.sqrt(0.9) * np.eye(2)]
    test_states = [np.array([[1.0, 0.0], [0.0, 0.0]], dtype=complex)]

    assert verifier.check_trace_preservation_on_states(leaky_kraus, test_states) is False


def test_conditionability_passes_for_composed_channels():
    verifier = TemporalStateAxiomVerifier()

    # Valid composition: E_a = I, E_b = I, E_ba = I
    def identity_map(rho):
        return rho

    rho0 = np.array([[0.5, 0.5], [0.5, 0.5]], dtype=complex)
    assert (
        verifier.check_composed_channel_consistency(rho0, identity_map, identity_map, identity_map)
        is True
    )


def test_conditionability_fails_for_mismatched_external_trajectory():
    verifier = TemporalStateAxiomVerifier()

    # Trajectory points: rho_i, rho_next, but map_fn is identity
    # if rho_next != rho_i, check_sequential_replay_consistency must fail
    rho_i = np.array([[1.0, 0.0], [0.0, 0.0]], dtype=complex)
    rho_next = np.array([[0.0, 0.0], [0.0, 1.0]], dtype=complex)

    def identity_map(rho):
        return rho

    assert verifier.check_sequential_replay_consistency(rho_i, rho_next, identity_map) is False


def test_density_validity_rejects_non_psd_matrix():
    verifier = TemporalStateAxiomVerifier()

    # Trace 1, Hermitian, but eigenvalues are -1 and 2 (not PSD)
    non_psd = np.array([[0.5, 1.5], [1.5, 0.5]], dtype=complex)
    assert verifier.check_density_validity(non_psd) is False


def test_run_phase0_checks_integration():
    res = run_phase0_checks(sensitivity=0.1, boost_beta=0.5)
    assert "checks" in res
    assert "observations" in res
    # All baseline flat Minkowski checks should pass
    assert all(status == "PASS" for status in res["checks"].values())
