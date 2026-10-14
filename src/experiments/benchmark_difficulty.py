"""Benchmark runner. Run: python -m src.experiments.benchmark_difficulty"""
import json
import sys

sys.path.insert(0, "src")
from btc_study.benchmarks import run_full_benchmark

if __name__ == "__main__":
    out = run_full_benchmark()
    print(json.dumps(out, indent=2))
