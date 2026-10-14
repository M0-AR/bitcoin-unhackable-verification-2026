"""Stage 4 — Zico & me: four hacking attempts (exactly as narrated).

Attempt 1 (change data only):  Ahmed "10" -> "1000", hash NOT updated.
  -> Q1 fails (stored != recomputed). Detected instantly.

Attempt 2 (change data + recompute hash, but no mining):
  -> Q3 fails (hash has no leading zeros). Detected.

Attempt 3 (change data + re-mine block 1 only):
  -> block 1 passes, but block 2's previous_hash still points at OLD hash.
  -> Q2 fails downstream. Attacker must now re-mine every later block.

Attempt 4 (re-mine block 1..end): full rewrite.
  -> On toy difficulty=4, 4-block chain: succeeds in ~seconds (video: ~3 s).
  -> This is the video's honest admission: small chain + small difficulty = hackable.
     Security comes only from Stage 5 (scale + decentralization).

Returns a structured transcript with timings so the README/PAPER can quote numbers.
"""
from __future__ import annotations

import copy
import time

from .chain_stage import validate_chain
from .mining_stage import mine_block


def run_four_attacks(chain, difficulty: int) -> dict:
    transcript: dict = {"difficulty": difficulty, "attempts": []}

    # --- Attempt 1: naive data edit ---
    c1 = copy.deepcopy(chain)
    c1[1].data = c1[1].data.replace("10", "1000")
    t0 = time.perf_counter()
    ok1, err1 = validate_chain(c1, difficulty)
    dt1 = time.perf_counter() - t0
    transcript["attempts"].append(
        {
            "n": 1,
            "name": "edit data only (10 -> 1000)",
            "valid": ok1,
            "errors": err1,
            "seconds": dt1,
            "verdict": "DETECTED at block 1 Q1" if not ok1 else "UNEXPECTED PASS",
        }
    )

    # --- Attempt 2: edit + recompute hash without mining ---
    c2 = copy.deepcopy(chain)
    c2[1].data = c2[1].data.replace("10", "1000")
    c2[1].hash = c2[1].recompute()
    t0 = time.perf_counter()
    ok2, err2 = validate_chain(c2, difficulty)
    dt2 = time.perf_counter() - t0
    transcript["attempts"].append(
        {
            "n": 2,
            "name": "edit + fresh hash, no PoW",
            "valid": ok2,
            "errors": err2,
            "seconds": dt2,
            "verdict": "DETECTED at block 1 Q3 (no leading zeros)" if not ok2 else "UNEXPECTED PASS",
        }
    )

    # --- Attempt 3: re-mine block 1 only ---
    c3 = copy.deepcopy(chain)
    c3[1].data = c3[1].data.replace("10", "1000")
    c3[1].nonce = 0
    t0 = time.perf_counter()
    mine_block(c3[1], difficulty)
    dt3 = time.perf_counter() - t0
    ok3, err3 = validate_chain(c3, difficulty)
    transcript["attempts"].append(
        {
            "n": 3,
            "name": "re-mine block 1 only",
            "valid": ok3,
            "errors": err3,
            "seconds": dt3,
            "verdict": "block 1 PASSES but block 2 Q2 FAILS (must re-mine downstream)",
        }
    )

    # --- Attempt 4: re-mine block 1..tip (full rewrite) ---
    c4 = copy.deepcopy(chain)
    c4[1].data = c4[1].data.replace("10", "1000")
    t0 = time.perf_counter()
    mine_block(c4[1], difficulty)
    for k in range(2, len(c4)):
        c4[k].previous_hash = c4[k - 1].hash
        c4[k].nonce = 0
        mine_block(c4[k], difficulty)
    dt4 = time.perf_counter() - t0
    ok4, err4 = validate_chain(c4, difficulty)
    transcript["attempts"].append(
        {
            "n": 4,
            "name": f"re-mine blocks 1..{len(c4)-1} (full rewrite)",
            "valid": ok4,
            "errors": err4,
            "seconds": dt4,
            "verdict": "FORGERY SUCCEEDS on toy chain — see Stage 5 for why mainnet differs",
        }
    )
    transcript["toy_rewrite_seconds"] = dt4
    return transcript
