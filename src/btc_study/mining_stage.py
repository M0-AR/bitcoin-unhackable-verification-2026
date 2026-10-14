"""Stage 3 — Mining (why Bitcoin consumes electricity like a country's budget).

Video claim: computing a fingerprint is trivial, so Zico could rewrite the
whole ledger in seconds. Bitcoin's fix: a block is accepted ONLY if its hash
starts with `difficulty` zeros. Because SHA-256 is unpredictable, the only way
is brute-force trial of `nonce` — like a 4-digit suitcase lock.

This module implements that PoW, plus the benchmark proving the video's
"16x per extra zero" claim (hex alphabet => P(leading zero) = 1/16).

Bitcoin mainnet (Oct 2026, verified live in this repo): difficulty ~132.72T,
hashrate ~950-1077 EH/s, i.e. ~19-20 leading hex zeros (~76-79 bits).
Our toy difficulty 1..5 extrapolates exactly to that wall.
"""
from __future__ import annotations

import time

from .chain_stage import Block


def mine_block(block: Block, difficulty: int, max_nonce: int = 50_000_000) -> Block:
    """Brute-force nonce until hash starts with `difficulty` zeros."""
    prefix = "0" * difficulty
    nonce = 0
    while nonce < max_nonce:
        block.nonce = nonce
        h = block.recompute()
        if h.startswith(prefix):
            block.hash = h
            return block
        nonce += 1
    raise RuntimeError(f"failed to mine difficulty={difficulty} within {max_nonce} nonces")


def mine_chain(chain: list[Block], difficulty: int) -> list[Block]:
    prev = "0" * 64
    for b in chain:
        b.previous_hash = prev
        b.nonce = 0
        b.hash = ""
        mine_block(b, difficulty)
        prev = b.hash
    return chain


def benchmark_difficulty(max_difficulty: int = 5, trials: int = 1) -> list[dict]:
    """Time mining a single block at each difficulty 1..max_difficulty."""
    import time as _t

    from .chain_stage import Block as _B

    results: list[dict] = []
    for d in range(1, max_difficulty + 1):
        times: list[float] = []
        hashes: list[int] = []
        for _ in range(trials):
            b = _B(index=0, data="Ahmed sent Mohamed 10", timestamp=_t.time(), previous_hash="0" * 64)
            t0 = _t.perf_counter()
            mine_block(b, d)
            dt = _t.perf_counter() - t0
            times.append(dt)
            hashes.append(b.nonce + 1)
        avg_t = sum(times) / len(times)
        avg_h = int(sum(hashes) / len(hashes))
        results.append(
            {
                "difficulty_zeros": d,
                "avg_seconds": avg_t,
                "avg_hashes": avg_h,
                "expected_hashes_theory": 16**d,
            }
        )
    return results


def extrapolation_to_bitcoin(local_hashrate: float) -> dict:
    """Extrapolate local single-core hashrate to Bitcoin mainnet difficulty.

    Bitcoin target ~ 2^(256-79); expected hashes ~ 2^79 ~ 6e23 at b≈79 bits
    (Jan-2025 b≈79 per arXiv:2603.25519; Oct-2026 difficulty 132.72T same order).
    """
    import math

    # Expected hashes for full 79-bit difficulty:
    expected_mainnet_hashes = 2**79
    seconds_single_core = expected_mainnet_hashes / max(local_hashrate, 1)
    years_single_core = seconds_single_core / (3600 * 24 * 365.25)
    # Network at ~1 ZH/s = 1e21 H/s:
    seconds_network = expected_mainnet_hashes / 1e21
    return {
        "expected_hashes_mainnet_2pow79": f"{expected_mainnet_hashes:.3e}",
        "single_core_years": f"{years_single_core:.3e}",
        "network_seconds_at_1ZHs": round(seconds_network, 1),
        "network_minutes": round(seconds_network / 60, 2),
        "note": "network finds block ~every 600s by design; difficulty retargets every 2016 blocks",
    }
