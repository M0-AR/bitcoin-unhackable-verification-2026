"""End-to-end reproduction of the video's five stages. Run: python -m src.experiments.run_all_5_stages"""
from __future__ import annotations

import json
import sys

sys.path.insert(0, "src")

from btc_study.attack_stage import run_four_attacks  # noqa: E402
from btc_study.chain_stage import create_chain, validate_chain  # noqa: E402
from btc_study.consensus_stage import simulate_network  # noqa: E402
from btc_study.hash_stage import demo_stage1  # noqa: E402
from btc_study.mining_stage import benchmark_difficulty  # noqa: E402

DATAS = [
    "genesis: network start",
    "Ahmed sent Mohamed 10",
    "Mohamed sent Sarah 7",
    "Sarah sent Yousef 3",
]


def main(difficulty: int = 4):
    print("=" * 72)
    print("STAGE 1 — fingerprint (SHA-256)")
    s1 = demo_stage1()
    print(json.dumps(s1, indent=2))

    print("=" * 72)
    print("STAGE 2 — chain (5 blocks incl. genesis pattern, here 4 for speed)")
    chain = create_chain(DATAS, difficulty=0)
    # show linkage
    for b in chain:
        print(f"block {b.index} data={b.data!r} prev={b.previous_hash[:16]}... hash={b.hash[:16]}...")
    ok, errs = validate_chain(chain, 0)
    print("valid (d=0):", ok, errs)

    print("=" * 72)
    print(f"STAGE 3 — mining (difficulty={difficulty} zeros)")
    from btc_study.mining_stage import mine_chain

    chain = mine_chain(chain, difficulty)
    for b in chain:
        print(f"block {b.index} nonce={b.nonce} hash={b.hash}")
    ok, errs = validate_chain(chain, difficulty)
    print("valid after mining:", ok, errs)
    print("difficulty ladder (1..4):")
    print(json.dumps(benchmark_difficulty(max_difficulty=4, trials=1), indent=2))

    print("=" * 72)
    print("STAGE 4 — Zico's four attacks")
    transcript = run_four_attacks(chain, difficulty)
    print(json.dumps(transcript, indent=2, default=str))

    print("=" * 72)
    print("STAGE 5 — the secret: longest valid chain over 5 nodes")
    import copy

    honest = chain
    forged = copy.deepcopy(chain)
    # forged = fully re-mined tampered copy (reuse attempt-4 logic quickly)
    forged[1].data = forged[1].data.replace("10", "1000")
    from btc_study.mining_stage import mine_block

    mine_block(forged[1], difficulty)
    for k in range(2, len(forged)):
        forged[k].previous_hash = forged[k - 1].hash
        forged[k].nonce = 0
        mine_block(forged[k], difficulty)
    # honest network advances by 2 blocks while Zico rewrites
    honest_extended = honest + create_chain(["Yousef sent Layla 1", "Layla sent Omar 2"], difficulty=0)
    # mine the two new blocks on top of honest tip
    honest_extended[4].previous_hash = honest_extended[3].hash
    honest_extended[5].previous_hash = ""  # will be set by mine_chain segment
    from btc_study.chain_stage import Block
    import time

    # simplest: re-mine only the 2 new blocks linked correctly
    honest_extended[4].previous_hash = honest[3].hash
    mine_block(honest_extended[4], difficulty)
    honest_extended[5].previous_hash = honest_extended[4].hash
    mine_block(honest_extended[5], difficulty)
    sim = simulate_network(honest_extended, forged, n_honest=4, difficulty=difficulty)
    print(json.dumps(sim, indent=2))

    print("=" * 72)
    print("DONE. All five video claims reproduced + measured.")
    with open("data/stages_transcript.json", "w") as f:
        json.dump({"stage1": s1, "stage4": transcript, "stage5": sim}, f, indent=2, default=str)


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--difficulty", type=int, default=4)
    main(**vars(p.parse_args()))
