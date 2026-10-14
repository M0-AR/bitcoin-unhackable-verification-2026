"""Stage 2 — Chain (why it is called Blockchain).

Video claim: "Every block carries the fingerprint of the previous block.
So if you change any block, all the blocks that depend on it break."

Block fields (exactly as narrated): index, data (who sent how much to whom),
timestamp, previous_hash, nonce (ignored until Stage 3), hash.
Block 0 = genesis block, previous_hash = "0"*64.

validate_chain() asks the three questions from the video:
  Q1. Is the stored fingerprint still valid? (recompute == stored)
  Q2. Does this block really point to the block before it?
  Q3. Was this block mined correctly? (hash meets difficulty)
"""
from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field


def compute_hash(index: int, data: str, timestamp: float, previous_hash: str, nonce: int) -> str:
    payload = f"{index}|{data}|{timestamp}|{previous_hash}|{nonce}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass
class Block:
    index: int
    data: str
    timestamp: float
    previous_hash: str
    nonce: int = 0
    hash: str = field(default="")

    def recompute(self) -> str:
        return compute_hash(self.index, self.data, self.timestamp, self.previous_hash, self.nonce)


def create_chain(datas: list[str], difficulty: int = 0) -> list[Block]:
    """Build a chain; if difficulty>0 each block is mined (see mining_stage)."""
    from .mining_stage import mine_block

    chain: list[Block] = []
    prev = "0" * 64
    for i, data in enumerate(datas):
        b = Block(index=i, data=data, timestamp=time.time(), previous_hash=prev)
        if difficulty > 0:
            mine_block(b, difficulty)
        else:
            b.hash = b.recompute()
        chain.append(b)
        prev = b.hash
    return chain


def validate_chain(chain: list[Block], difficulty: int = 0) -> tuple[bool, list[str]]:
    """Return (is_valid, error_list). Checks Q1/Q2/Q3 for every block."""
    errors: list[str] = []
    for i, b in enumerate(chain):
        # Q1: stored fingerprint still valid?
        if b.recompute() != b.hash:
            errors.append(f"block {i}: Q1 FAIL stored hash != recomputed (tampered data/nonce)")
        # Q2: linkage?
        if i == 0:
            if b.previous_hash != "0" * 64:
                errors.append("block 0: Q2 FAIL genesis previous_hash != zeros")
        else:
            if b.previous_hash != chain[i - 1].hash:
                errors.append(
                    f"block {i}: Q2 FAIL previous_hash != hash of block {i-1} (chain broken)"
                )
        # Q3: mined correctly?
        if difficulty > 0 and not b.hash.startswith("0" * difficulty):
            errors.append(f"block {i}: Q3 FAIL hash does not meet difficulty={difficulty}")
    return (len(errors) == 0, errors)
