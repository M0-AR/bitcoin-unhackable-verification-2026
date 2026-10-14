# Reproducibility

- `docker compose run --rm tests` → 6 passed (determinism, avalanche, Q1/Q2/Q3, longest-chain, monotonic catch-up).
- `docker compose run --rm reproduce` → `data/stages_transcript.json` (all 5 stages + timings).
- `docker compose run --rm benchmark` → `data/benchmarks/results.json` (16^d law, O(n) validation, Nakamoto table).
- `docker compose run --rm verify-live` → `data/live_snapshot.json` (CoinGecko live + Oct-2026 reference with provenance).
- No API keys, no private data, Python stdlib + pytest only. Offline: live fetch degrades to checked-in reference and flags it.
- Expected variance: mining times ±2× run-to-run (geometric); verdicts invariant.
