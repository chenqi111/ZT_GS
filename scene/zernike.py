"""
Zernike Spectral Trajectory Field (ZSTF) for ZT-GS.

Replaces cubic Hermite splines with a global spectral decomposition on a
conformally embedded unit disk (ZT-GS.pdf Sec. III-A).

    mu_g(t) = sum_{n=0..N} sum_{m=-n..n} C_{n,m}^{(g)} * Z_{n,m}(rho(t), theta(t)) + eps_g(t)

with the modified Zernike-Sobolev basis (Eq. 2):

    Z_{n,m}(rho, theta) = sqrt((2n+2)/pi) * R_n^{|m|}(rho) * Theta_m(theta)
                          * exp(-beta * n/N * rho^2)

Conformal embedding (Eq. 1):

    rho(t) = t / T,    theta(t) = omega * t / T
"""

import math

import torch
import torch.nn as nn


def _radial_poly(n: int, m: int, rho: torch.Tensor) -> torch.Tensor:
    """Zernike radial polynomial R_n^{|m|}(rho)."""
    m = abs(m)
    if (n - m) % 2 != 0:
        return torch.zeros_like(rho)
    out = torch.zeros_like(rho)
    k_max = (n - m) // 2
    for k in range(k_max + 1):
        sign = -1.0 if k % 2 else 1.0
        num = math.factorial(n - k)
        den = (
            math.factorial(k)
            * math.factorial((n + m) // 2 - k)
            * math.factorial((n - m) // 2 - k)
        )
        coeff = sign * num / den
        out = out + coeff * rho ** (n - 2 * k)
    return out


def build_mode_list(N: int):
    """Return list of (n, m) pairs for n=0..N, m=-n..n. Total (N+1)^2 modes."""
    modes = []
    for n in range(N + 1):
        for m in range(-n, n + 1):
            modes.append((n, m))
    return modes


def precompute_basis(rho: torch.Tensor, theta: torch.Tensor, N: int, beta: float):
    """
    Evaluate all (N+1)^2 Zernike-Sobolev basis functions at the given (rho, theta).

    Args:
        rho:   [..., 1] or [...] tensor in [0, 1]
        theta: [...] tensor
        N:     maximum radial order
        beta:  exponential decay coefficient
    Returns:
        basis: [..., M] tensor, M = (N+1)^2
        ns:    [M] tensor of radial orders (used for frequency-selective ops)
    """
    modes = build_mode_list(N)
    M = len(modes)
    basis_list = []
    ns = []
    rho = rho.to(theta.dtype)
    rho_sq = rho ** 2
    for n, m in modes:
        R = _radial_poly(n, m, rho)
        if m >= 0:
            ang = torch.cos(m * theta)
        else:
            ang = torch.sin(abs(m) * theta)
        norm = math.sqrt((2 * n + 2) / math.pi)
        decay = torch.exp(torch.tensor(-beta * n / max(N, 1) * 1.0, device=theta.device, dtype=theta.dtype)) ** rho_sq
        Z = norm * R * ang * decay
        basis_list.append(Z)
        ns.append(n)
    basis = torch.stack(basis_list, dim=-1)  # [..., M]
    ns_t = torch.tensor(ns, device=theta.device, dtype=torch.float32)
    return basis, ns_t


def conformal_embed(t: torch.Tensor, T: float, omega: float):
    """
    Conformal embedding Phi(t) = (rho(t), theta(t)) onto the unit disk.

    Args:
        t:     [...] tensor, normalized time in [0, 1] (or any scalar)
        T:     sequence length used for normalizing (kept for API symmetry;
               if t is already normalized, pass T=1.0)
        omega: temporal winding number (periodic physiological motion)
    Returns:
        rho, theta: each of shape [...]
    """
    T = max(float(T), 1.0)
    rho = t / T
    theta = omega * t / T
    return rho, theta


def evaluate_zernike(coeffs: torch.Tensor, t: torch.Tensor, N: int, omega: float, beta: float, T: float = 1.0):
    """
    Evaluate the Zernike spectral trajectory field at time t.

    Args:
        coeffs: [B, M, 3] learnable Zernike spectral coefficients C_{n,m}^{(g)}
        t:      scalar tensor in [0, 1] (normalized time)
        N, omega, beta, T: ZSTF hyperparameters
    Returns:
        mu: [B, 3] trajectory position (displacement, to be scaled by deform_spatial_scale)
    """
    rho, theta = conformal_embed(t, T, omega)
    # broadcast t-shape with [B, M]
    rho = rho.expand(coeffs.shape[0], 1) if rho.dim() == 0 else rho
    theta = theta.expand(coeffs.shape[0], 1) if theta.dim() == 0 else theta
    basis, _ = precompute_basis(rho, theta, N, beta)  # [B, M]
    mu = (basis.unsqueeze(-1) * coeffs).sum(dim=1)  # [B, 3]
    return mu


def evaluate_zernike_batched(coeffs: torch.Tensor, t: torch.Tensor, N: int, omega: float, beta: float, T: float = 1.0):
    """
    Batched evaluation: different time per Gaussian.

    Args:
        coeffs: [B, M, 3]
        t:      [B, 1] or [B] tensor of per-Gaussian normalized times
    Returns:
        mu: [B, 3]
    """
    if t.dim() == 1:
        t = t.unsqueeze(-1)
    rho = t / T
    theta = omega * t / T
    # basis: we need per-Gaussian basis -> [B, M]
    basis_list = []
    modes = build_mode_list(N)
    rho_flat = rho.squeeze(-1) if rho.shape[-1] == 1 else rho[..., 0]
    theta_flat = theta.squeeze(-1) if theta.shape[-1] == 1 else theta[..., 0]
    rho_sq = rho_flat ** 2
    for n, m in modes:
        R = _radial_poly(n, m, rho_flat)
        if m >= 0:
            ang = torch.cos(m * theta_flat)
        else:
            ang = torch.sin(abs(m) * theta_flat)
        norm = math.sqrt((2 * n + 2) / math.pi)
        decay = torch.exp(-beta * n / max(N, 1) * rho_sq)
        Z = norm * R * ang * decay
        basis_list.append(Z)
    basis = torch.stack(basis_list, dim=-1)  # [B, M]
    mu = (basis.unsqueeze(-1) * coeffs).sum(dim=1)  # [B, 3]
    return mu


def fit_zernike(curves: torch.Tensor, times: torch.Tensor, N: int, omega: float, beta: float, T: float = 1.0):
    """
    Inverse fit: given trajectory samples, solve for Zernike spectral coefficients
    via linear least-squares (analogous to inverse_cubic_hermite).

    The 1D time-spiral sampling of the 2D Zernike basis can be rank-deficient
    (many modes are linearly dependent along the spiral), so we use a
    Tikhonov-regularized (ridge) solve for numerical stability. This returns
    a minimum-norm coefficient set; redundant modes are driven toward zero,
    which is consistent with the spectral sparsity loss (Eq. 8).

    Args:
        curves: [B, T_len, 3] sampled trajectory positions
        times:  [T_len] or [1, T_len] normalized times in [0, 1]
        N, omega, beta, T: ZSTF hyperparameters
    Returns:
        coeffs: [B, M, 3] fitted Zernike spectral coefficients
    """
    if times.dim() == 2:
        times = times.squeeze(0)
    T_len = times.shape[0]
    B = curves.shape[0]
    modes = build_mode_list(N)
    M = len(modes)
    # Build design matrix A: [T_len, M]
    rho = times / T
    theta = omega * times / T
    rho_sq = rho ** 2
    cols = []
    for n, m in modes:
        R = _radial_poly(n, m, rho)
        if m >= 0:
            ang = torch.cos(m * theta)
        else:
            ang = torch.sin(abs(m) * theta)
        norm = math.sqrt((2 * n + 2) / math.pi)
        decay = torch.exp(-beta * n / max(N, 1) * rho_sq)
        cols.append(norm * R * ang * decay)
    A = torch.stack(cols, dim=-1)  # [T_len, M]
    # Tikhonov regularization for rank-deficient design:
    #   min ||A @ C - curves||^2 + lambda * ||C||^2
    # Solve via the normal equations: (A^T A + lambda I) C = A^T curves
    lam = 1e-4 * max(1.0, (A.T @ A).diagonal().abs().mean().item())
    AtA = A.T @ A + lam * torch.eye(M, device=A.device, dtype=A.dtype)
    AtB = A.T @ curves  # [M, 3]
    # Broadcast over batch: curves is [B, T_len, 3], A is [T_len, M]
    # Use batched solve: (AtA) C_b = A^T curves_b for each b
    AtA_b = AtA.unsqueeze(0).expand(B, -1, -1)
    AtB_b = torch.bmm(A.unsqueeze(0).expand(B, -1, -1).transpose(1, 2), curves)  # [B, M, 3]
    coeffs = torch.linalg.solve(AtA_b, AtB_b)  # [B, M, 3]
    return coeffs


def num_modes(N: int) -> int:
    """Total number of Zernike modes for max order N: (N+1)^2."""
    return (N + 1) ** 2


def mode_orders(N: int, device=None, dtype=torch.float32) -> torch.Tensor:
    """Return tensor of radial orders n for each mode index (used for
    frequency-selective MG-TPC and spectral entropy in TASS)."""
    modes = build_mode_list(N)
    return torch.tensor([n for n, _ in modes], device=device, dtype=dtype)
