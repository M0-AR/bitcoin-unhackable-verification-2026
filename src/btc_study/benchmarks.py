"""Reproducible benchmarks: scaling law + validation cost + catch-up table."""
from __future__ import annotations

import json
import time

from .chain_stage import create_chain, validate_chain
from .consensus_stage import catchup_table
from .mining_stage import benchmark_difficulty


def run_full_benchmark(difficulties=(1, 2, 3, 4, 5), out_path="data/benchmarks/results.json") -> dict:
    t0 = time.perf_counter()
    mining = benchmark_difficulty(max_difficulty=max(difficulties), trials=1)
    # validation cost O(n): time validate_chain for n=10..200
    val_cost = []
    for n in (10, 50, 100, 200):
        chain = create_chain([f"tx {i}" for i in range(n)], difficulty=0)
        s = time.perf_counter()
        validate_chain(chain, 0)
        val_cost.append({"n_blocks": n, "validate_seconds": time.perf_counter() - s})
    catchup = catchup_table()
    # scaling ratios: t(d+1)/t(d)
    ratios = []
    for a, b in zip(mining[:-1], mining[1:]):
        ratios.append(
            {
                "from": a["difficulty_zeros"],
                "to": b["difficulty_zeros"],
                "time_ratio": (b["avg_seconds"] / a["avg_seconds"]) if a["avg_seconds"] > 0 else None,
                "hash_ratio": (b["avg_hashes"] / a["avg_hashes"]) if a["avg_hashes"] > 0 else None,
            }
        )
    out = {
        "mining": mining,
        "scaling_ratios": ratios,
        "validation_cost": val_cost,
        "nakamoto_catchup": catchup,
        "total_seconds": time.perf_counter() - t0,
    }
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)
    return out
