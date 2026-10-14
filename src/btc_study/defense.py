"""Defense layer: confirmation policy, reorg guard, 51% costing.

Defensive-only: no attack tooling. Inputs are your own toy chain +
public network stats. Outputs are operator decisions:
how many confirmations, when to alarm, what an attacker would need to spend.
"""
from __future__ import annotations

from .consensus_stage import nakamoto_catchup_probability

__all__ = [
    "recommended_confirmations",
    "reorg_guard",
    "estimate_attack_cost",
    "confirmation_table",
]


def recommended_confirmations(q: float, max_risk: float = 0.001, z_max: int = 100) -> int:
    """Smallest z with P(catch-up | q) <= max_risk. Raises if never within z_max."""
    if not isinstance(q, (int, float)) or not 0.0 <= q <= 1.0:
        raise ValueError(f"q must be within [0, 1], got {q!r}")
    if not isinstance(max_risk, (int, float)) or not 0.0 < max_risk < 1.0:
        raise ValueError(f"max_risk must be within (0, 1), got {max_risk!r}")
    if not isinstance(z_max, int) or z_max < 1:
        raise ValueError(f"z_max must be a positive int, got {z_max!r}")
    for z in range(1, z_max + 1):
        if nakamoto_catchup_probability(q, z) <= max_risk:
            return z
    raise ValueError(f"risk {max_risk} unreachable within {z_max} confirmations at q={q}")


def reorg_guard(old_tip: str, new_chain, max_reorg_depth: int = 6) -> dict:
    """Flag suspicious reorganizations on your own node.

    new_chain: list[Block] currently adopted. old_tip: previous tip hash.
    Returns decision dict; alarms when the common ancestor is deeper than allowed.
    """
    if not isinstance(max_reorg_depth, int) or max_reorg_depth < 0:
        raise ValueError(f"max_reorg_depth must be a non-negative int, got {max_reorg_depth!r}")
    hashes = [b.hash for b in new_chain] if new_chain else []
    if not hashes:
        return {"reorg_depth": None, "alarm": True, "tip": None, "note": "empty chain — resync required"}
    if old_tip in hashes:
        depth = len(hashes) - 1 - hashes.index(old_tip)
        alarm = depth > max_reorg_depth
        return {"reorg_depth": depth, "alarm": alarm, "tip": hashes[-1][:16]}
    return {"reorg_depth": None, "alarm": True, "tip": hashes[-1][:16], "note": "old tip absent — deep reorg or resync"}


def estimate_attack_cost(
    network_hashrate_hs: float,
    share: float = 0.51,
    hours: float = 24.0,
    usd_per_mwh: float = 60.0,
    watts_per_ths: float = 20.0,
) -> dict:
    """Order-of-magnitude 51%-style cost from public hashrate.

    watts_per_ths: fleet-average ASIC efficiency (~20 W/TH/s class, 2026).
    Returns power draw + energy bill for `hours`. Hardware capex excluded
    (dominant term — see README $6B/week reference); energy is the floor.
    """
    if not isinstance(network_hashrate_hs, (int, float)) or network_hashrate_hs < 0:
        raise ValueError(f"network_hashrate_hs must be >= 0, got {network_hashrate_hs!r}")
    if not isinstance(share, (int, float)) or not 0.0 <= share <= 1.0:
        raise ValueError(f"share must be within [0, 1], got {share!r}")
    if not isinstance(hours, (int, float)) or hours < 0:
        raise ValueError(f"hours must be >= 0, got {hours!r}")
    if not isinstance(usd_per_mwh, (int, float)) or usd_per_mwh < 0:
        raise ValueError(f"usd_per_mwh must be >= 0, got {usd_per_mwh!r}")
    if not isinstance(watts_per_ths, (int, float)) or watts_per_ths <= 0:
        raise ValueError(f"watts_per_ths must be > 0, got {watts_per_ths!r}")
    attacker_hs = network_hashrate_hs * share / (1.0 - share) if share < 1 else network_hashrate_hs
    # convert H/s to TH/s then to watts
    power_w = attacker_hs / 1e12 * watts_per_ths
    energy_mwh = power_w * hours / 1e6
    return {
        "attacker_hashrate_hs": attacker_hs,
        "power_gw": round(power_w / 1e9, 3),
        "energy_mwh": round(energy_mwh, 1),
        "energy_usd_floor": round(energy_mwh * usd_per_mwh, 2),
        "note": "energy floor only; ASIC capex + facilities dominate real cost",
    }


def confirmation_table(q_values=(0.1, 0.3), risks=(0.01, 0.001)) -> list[dict]:
    rows = []
    for q in q_values:
        for r in risks:
            try:
                z = recommended_confirmations(q, r)
            except ValueError:
                z = None
            rows.append({"q": q, "max_risk": r, "recommended_z": z})
    return rows
