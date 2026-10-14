import sys

sys.path.insert(0, "src")

from btc_study.chain_stage import create_chain, validate_chain
from btc_study.consensus_stage import nakamoto_catchup_probability, simulate_network
from btc_study.hash_stage import avalanche_distance, sha256_hex
from btc_study.mining_stage import mine_block
from btc_study.chain_stage import Block
import time


def test_sha256_deterministic():
    assert sha256_hex("Ahmed") == sha256_hex("Ahmed")


def test_avalanche():
    h1 = sha256_hex("Ahmed sent Mohammed 10")
    h2 = sha256_hex("Ahmed sent Mohammed 90")
    hd, bd = avalanche_distance(h1, h2)
    assert hd >= 20  # strong avalanche; video reports ~60 for its pair
    assert bd >= 80


def test_chain_linkage_breaks_on_tamper():
    chain = create_chain(["a", "b", "c"], difficulty=0)
    ok, _ = validate_chain(chain, 0)
    assert ok
    chain[1].data = "tampered"
    ok2, errs = validate_chain(chain, 0)
    assert not ok2 and any("Q1" in e for e in errs)


def test_mining_meets_difficulty():
    b = Block(index=0, data="x", timestamp=time.time(), previous_hash="0" * 64)
    mine_block(b, difficulty=2)
    assert b.hash.startswith("00")
    ok, _ = validate_chain([b], difficulty=2)
    assert ok


def test_longest_chain_rejects_shorter_forgery():
    import copy

    honest = create_chain(["g", "a", "b", "c", "d", "e", "f"], difficulty=0)
    forged = copy.deepcopy(honest[:5])
    sim = simulate_network(honest, forged, n_honest=2, difficulty=0)
    assert not sim["attacker_wins"]


def test_nakamoto_probability_monotonic():
    # more confirmations => strictly smaller catch-up prob for q<0.5
    p1 = nakamoto_catchup_probability(0.3, 2)
    p2 = nakamoto_catchup_probability(0.3, 6)
    assert p2 < p1
    assert nakamoto_catchup_probability(0.51, 6) == 1.0
