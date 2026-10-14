# Threat model

- **Adversary:** Zico — can edit any local copy, recompute hashes, brute-force nonces, withhold blocks; cannot break SHA-256 preimage/collision or forge ECDSA (out of scope for toy).
- **Honest majority:** holds >50% hash, follows longest-valid-chain, mines continuously during attacks.
- **In scope:** silent edits, unworked/partial/full rewrites, minority-hash revision.
- **Out of scope (real attackers go here):** key theft, address reuse + Shor, pool coercion (3-pool majority Oct-2026), eclipse/Vector76, selfish mining, PQC migration.
- **Success metric:** attacker chain adopted by honest nodes. Measured: false for any minority-hash attacker regardless of local validity.
