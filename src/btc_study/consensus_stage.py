"""Stage 5 — The secret nobody tells you: decentralization + longest valid chain.

Video claim: "The ledger isn't just with Mr. Sayed; there are thousands of
copies... everyone trusts the longest valid chain. So the hacker must outpace
the entire world at the same time."

Model:
  - N nodes (Sayed, grocer, Umm Ahmed, pharmacy, ...), each holds a full chain copy.
  - Honest nodes keep mining new blocks while attacker rewrites history.
  - Fork-choice rule: longest VALID chain wins (most accumulated PoW).

We simulate: honest network with H blocks vs Zico's forged node with F blocks.
If F < H, Zico loses even though his chain is internally valid — exactly the
video's Node-5-has-5-blocks vs Nodes-1..4-have-7-blocks scene.

Also implements Nakamoto (2008) attacker-catch-up probability:
  q = attacker hash fraction, p = 1-q, z = confirmations behind.
  P(win) = 1 - sum_{k=0..z} Poisson(k; z*q/p) * (1 - (q/p)^(z-k))   for q<p.
This is the "hidden pattern" headliner: win probability decays EXPONENTIALLY
in z, which is why 6 confirmations ≈ irreversible.
"""
from __future__ import annotations

import copy
import math
from dataclasses import dataclass, field


@dataclass
class Node:
    name: str
    chain: list = field(default_factory=list)

    @property
    def height(self) -> int:
        return len(self.chain)


def longest_valid_chain(nodes: list[Node], difficulty: int = 0) -> Node:
    from .chain_stage import validate_chain

    best: Node | None = None
    for n in nodes:
        ok, _ = validate_chain(n.chain, difficulty)
        if not ok:
            continue
        if best is None or n.height > best.height:
            best = n
    assert best is not None, "no valid chain in network"
    return best


def simulate_network(
    honest_chain, forged_chain, n_honest: int = 4, difficulty: int = 0
) -> dict:
    """Build n_honest honest nodes + 1 attacker node; apply longest-valid rule."""
    nodes = [Node(name=f"honest-{i+1}", chain=copy.deepcopy(honest_chain)) for i in range(n_honest)]
    nodes.append(Node(name="zico-attacker", chain=copy.deepcopy(forged_chain)))
    winner = longest_valid_chain(nodes, difficulty)
    return {
        "honest_height": len(honest_chain),
        "attacker_height": len(forged_chain),
        "winner": winner.name,
        "attacker_wins": winner.name == "zico-attacker",
        "rule": "longest VALID chain",
        "interpretation": (
            "Zico's internally-valid forgery is REJECTED because honest chain is longer"
            if winner.name != "zico-attacker"
            else "Attacker wins only by out-mining the network (needs >50% hash)"
        ),
    }


def nakamoto_catchup_probability(q: float, z: int) -> float:
    """Probability attacker with hash fraction q ever catches up from z behind."""
    if not isinstance(z, int) or z < 0:
        raise ValueError(f"z must be a non-negative int, got {z!r}")
    if not isinstance(q, (int, float)) or not 0.0 <= q <= 1.0:
        raise ValueError(f"q must be within [0, 1], got {q!r}")
    if q >= 0.5:
        return 1.0
    p = 1.0 - q
    lam = z * q / p
    s = 0.0
    for k in range(z + 1):
        poisson = math.exp(-lam) * lam**k / math.factorial(k)
        s += poisson * (1.0 - (q / p) ** (z - k))
    return 1.0 - s


def catchup_table(q_values=(0.1, 0.3, 0.45, 0.51), z_values=(1, 2, 4, 6, 10)) -> list[dict]:
    rows = []
    for q in q_values:
        for z in z_values:
            rows.append({"q": q, "z": z, "P_catchup": nakamoto_catchup_probability(q, z)})
    return rows
