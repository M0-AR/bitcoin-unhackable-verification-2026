# Methodology (zero → hero)

1. **Survey:** compare agreeing and dissenting views across papers, protocol docs, live explorers and community analyses (distinct topics, one at a time) to collect 2026 numbers before writing any code.
2. **Reproduce:** new directory, no local code reused; five modules mirror the video's five stages 1:1 (hash → chain → mining → 4 attacks → 5-node consensus).
3. **Measure:** every README number is a program output (`data/*.json`); timings are means over 10 trials where variance matters (mining), single-shot where deterministic (hash).
4. **Anchor live:** CoinGecko price fetched at runtime; difficulty/hashrate cross-checked across CoinWarz/mempool.space/startmining/miningcalcs 13–14 Oct 2026; mempool.space timeouts recorded honestly, never silently replaced.
5. **Falsify:** pytest guards invert each claim (tamper must fail, short forgery must lose, catch-up must decay); any guard failure blocks the "verified" label.
