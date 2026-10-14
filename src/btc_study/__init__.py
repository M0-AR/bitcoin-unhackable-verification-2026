"""btc_study: five-stage educational Bitcoin security model."""
from .hash_stage import sha256_hex, avalanche_distance, demo_stage1
from .chain_stage import Block, create_chain, compute_hash, validate_chain
from .mining_stage import mine_block, mine_chain, benchmark_difficulty
from .attack_stage import run_four_attacks
from .consensus_stage import Node, simulate_network, longest_valid_chain

__all__ = [
    "sha256_hex",
    "avalanche_distance",
    "demo_stage1",
    "Block",
    "create_chain",
    "compute_hash",
    "validate_chain",
    "mine_block",
    "mine_chain",
    "benchmark_difficulty",
    "run_four_attacks",
    "Node",
    "simulate_network",
    "longest_valid_chain",
]
