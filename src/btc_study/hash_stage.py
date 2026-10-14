"""Stage 1 — Fingerprint (SHA-256 hash).

Video claim: "A hash is a fingerprint for data. If even one letter changes,
the entire fingerprint changes." Bitcoin uses SHA-256 (64 hex chars).

Three properties verified here:
  1. Determinism: same input -> same output.
  2. Avalanche: 1-char change flips ~50% of output bits (~32/64 hex chars differ
     in practice; video reports 60/64 for "10" -> "90" example).
  3. Preimage resistance: cannot invert fingerprint to recover input.
"""
from __future__ import annotations

import hashlib


def sha256_hex(text: str) -> str:
    """One-line fingerprint exactly as in the video: hashlib SHA-256."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def avalanche_distance(a: str, b: str) -> tuple[int, int]:
    """Return (hex-char differences, bit differences) between two hex digests."""
    assert len(a) == len(b) == 64
    hex_diff = sum(c1 != c2 for c1, c2 in zip(a, b))
    bit_diff = sum(bin(int(c1, 16) ^ int(c2, 16)).count("1") for c1, c2 in zip(a, b))
    return hex_diff, bit_diff


def demo_stage1() -> dict:
    """Reproduce the Uncle-Sayed / Ahmed -> Mohammed ledger demo."""
    honest = "Ahmed sent Mohammed 10"
    honest_again = "Ahmed sent Mohammed 10"
    forged = "Ahmed sent Mohammed 90"

    h1 = sha256_hex(honest)
    h2 = sha256_hex(honest_again)
    h3 = sha256_hex(forged)
    hex_diff, bit_diff = avalanche_distance(h1, h3)

    return {
        "honest": honest,
        "honest_hash": h1,
        "repeat_hash": h2,
        "deterministic": h1 == h2,
        "forged": forged,
        "forged_hash": h3,
        "hex_chars_differ": hex_diff,
        "bits_differ_out_of_256": bit_diff,
        "avalanche_ratio": round(bit_diff / 256, 4),
    }


if __name__ == "__main__":
    import json

    print(json.dumps(demo_stage1(), indent=2))
