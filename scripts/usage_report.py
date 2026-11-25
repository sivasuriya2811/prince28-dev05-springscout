"""Print a formatted LLM cost, latency, and budget report from /v1/usage and /v1/usage/models."""

import argparse
import sys

import httpx

DAY1_TARGET_INR = 0.50


def main() -> int:
    parser = argparse.ArgumentParser(description="SpringScout LLM usage & cost report")
    parser.add_argument("--url", default="http://127.0.0.1:8000", help="Base API URL")
    parser.add_argument("--days", type=int, default=7, help="Lookback window in days (1-90)")
    args = parser.parse_args()

    base = args.url.rstrip("/")
    with httpx.Client(timeout=20.0) as client:
        daily_resp = client.get(f"{base}/v1/usage", params={"days": args.days})
        daily_resp.raise_for_status()
        models_resp = client.get(f"{base}/v1/usage/models", params={"days": args.days})
        models_resp.raise_for_status()

    daily = daily_resp.json()
    models = models_resp.json()

    total_calls = daily["calls"]
    total_errors = sum(d["errors"] for d in daily["days"])
    answered = max(total_calls - total_errors, 0)
    total_cost = daily["total_cost_inr"]
    avg_cost = (total_cost / answered) if answered else 0.0
    status = "PASS" if avg_cost <= DAY1_TARGET_INR else "OVER TARGET"

    print(f"\n=== SpringScout LLM Usage Report (Last {args.days} days) ===")
    print(f"Total calls      : {total_calls} ({answered} answered, {total_errors} errors)")
    print(f"Total spend      : Rs {total_cost:.4f}")
    print(
        f"Avg / answered   : Rs {avg_cost:.4f} (Day 1 target <= Rs {DAY1_TARGET_INR:.2f}: {status})"
    )

    print("\n--- Per-Model Breakdown ---")
    header = (
        f"{'Provider':<10} {'Model':<26} {'Calls':>5} {'Err':>4} "
        f"{'Fb':>4} {'Avg ms':>8} {'Cost (Rs)':>10}"
    )
    print(header)
    print("-" * len(header))
    for row in models["models"]:
        print(
            f"{row['provider']:<10} {row['model']:<26} {row['calls']:>5} "
            f"{row['errors']:>4} {row['fallbacks']:>4} {row['avg_latency_ms']:>8.1f} "
            f"{row['cost_inr']:>10.4f}"
        )
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
