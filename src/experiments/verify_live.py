"""Live verification runner. Run: python -m src.experiments.verify_live"""
import json
import sys

sys.path.insert(0, "src")
from btc_study.live_verify import build_snapshot

if __name__ == "__main__":
    print(json.dumps(build_snapshot("data/live_snapshot.json"), indent=2))
