"""Kirkwood-Dirac quasi-probability optimizer (PyTorch).

Finds optimal measurement basis angles (theta, phi) to maximize
KD negativity -- a proxy indicator of non-classicality (contextuality).
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np

logger = logging.getLogger(__name__)

DEFAULT_PATIENCE = 20

try:
    import torch

    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


if TORCH_AVAILABLE:

    class QuantumOptimizer(torch.nn.Module):
        """Differentiable Bloch-angle search for KD negativity.

        Learns basis angles (theta_a, phi_a, theta_b, phi_b) via Adam
        to minimize Re(Tr(P_b P_a rho)), finding negative KD values.
        """

        def __init__(self, rho_np: np.ndarray):
            super().__init__()
            self.rho = torch.tensor(rho_np, dtype=torch.complex128)
            torch.manual_seed(42)
            self.theta_a = torch.nn.Parameter((torch.rand(1) * np.pi).to(dtype=torch.float64))
            self.phi_a = torch.nn.Parameter((torch.rand(1) * 2 * np.pi).to(dtype=torch.float64))
            self.theta_b = torch.nn.Parameter((torch.rand(1) * np.pi).to(dtype=torch.float64))
            self.phi_b = torch.nn.Parameter((torch.rand(1) * 2 * np.pi).to(dtype=torch.float64))

        def get_projector(self, theta, phi):
            c = torch.cos(theta / 2)
            s = torch.sin(theta / 2)
            phase = torch.exp(1j * phi)
            psi = torch.stack([c, phase * s]).squeeze()
            if psi.dim() == 0:
                psi = psi.unsqueeze(0)
            return torch.outer(psi, psi.conj())

        def forward(self):
            Pa = self.get_projector(self.theta_a, self.phi_a)
            Pb = self.get_projector(self.theta_b, self.phi_b)
            return torch.trace(Pb @ Pa @ self.rho).real


def run_kd_optimization(
    state_path: str,
    out_path: str,
    *,
    steps: int = 200,
    lr: float = 0.1,
    patience: int = DEFAULT_PATIENCE,
    min_delta: float = 1e-6,
) -> Optional[Dict[str, Any]]:
    """Gradient-based Kirkwood-Dirac basis optimization (PyTorch Adam) with early stopping."""
    if not TORCH_AVAILABLE:
        logger.warning("PyTorch not found -- KD optimization skipped.")
        Path(out_path).write_text(
            json.dumps({"kd_value": 0.0, "error": "torch_missing"}, indent=2)
        )
        return None

    try:
        with np.load(state_path) as data:
            keys = sorted(k for k in data.keys() if k.startswith("rho_"))
            if not keys:
                raise ValueError(f"No rho states in {state_path}")
            rho = data[keys[-1]]
    except (FileNotFoundError, KeyError, OSError, ValueError) as e:
        logger.error("Failed to load state: %s", e)
        Path(out_path).write_text(json.dumps({"kd_value": 0.0, "error": str(e)}, indent=2))
        return None

    model = QuantumOptimizer(rho)
    opt = torch.optim.Adam(model.parameters(), lr=lr)

    best_loss = float("inf")
    no_improve = 0
    best_state = None
    final_step = 0

    for i in range(steps):
        opt.zero_grad()
        val = model()
        val.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        opt.step()

        current = val.item()
        if current < best_loss - min_delta:
            best_loss = current
            no_improve = 0
            best_state = {k: v.clone() for k, v in model.state_dict().items()}
        else:
            no_improve += 1

        final_step = i + 1
        if no_improve >= patience:
            if best_state is not None:
                model.load_state_dict(best_state)
            break

    final_val = model().item()
    result = {
        "kd_value": final_val,
        "is_negative": final_val < 0,
        "contextuality_proxy": final_val < -1e-6,
        "convergence": {
            "converged": no_improve >= patience,
            "final_step": final_step,
            "total_steps": steps,
        },
        "angles": {
            "basis_a": {
                "theta": float(model.theta_a.item()),
                "phi": float(model.phi_a.item()),
            },
            "basis_b": {
                "theta": float(model.theta_b.item()),
                "phi": float(model.phi_b.item()),
            },
        },
        "target_state_index": keys[-1],
    }

    Path(out_path).write_text(json.dumps(result, indent=2))
    return result
