"""
examples.py — Usage examples for MiningCalculator.

Run:  python examples.py
"""

from mining import MiningCalculator

# ──────────────────────────────────────────────────────────────
# Example 1 — Bitcoin (Antminer S21 Pro, 234 TH/s, 3531 W)
# ──────────────────────────────────────────────────────────────
print("=" * 55)
print("Example 1: Bitcoin — Antminer S21 Pro (234 TH/s)")
print("=" * 55)

btc = MiningCalculator(
    hashrate=234,            # TH/s
    power_watts=3531,
    electricity_kwh=0.07,
    pool_fee=0.01,
)

btc_result = btc.calculate(
    network_hashrate=700_000_000,   # ~700 EH/s in TH/s
    block_reward=3.125,             # post-April-2024 halving
    block_time_seconds=600,
    coin_price_usd=65_000,
)
print(btc_result)
print(f"  ROI (hardware $4,000): {btc.roi_days(4000, 700_000_000, 3.125, 600, 65_000)} days")

# ──────────────────────────────────────────────────────────────
# Example 2 — Kaspa (IceRiver KS5L, 12 TH/s, 3400 W)
# ──────────────────────────────────────────────────────────────
print()
print("=" * 55)
print("Example 2: Kaspa — IceRiver KS5L (12 TH/s)")
print("=" * 55)

kas = MiningCalculator(
    hashrate=12,             # TH/s
    power_watts=3400,
    electricity_kwh=0.07,
    pool_fee=0.01,
)

kas_result = kas.calculate(
    network_hashrate=800_000,    # ~800 PH/s in TH/s
    block_reward=146,
    block_time_seconds=1,
    coin_price_usd=0.125,
)
print(kas_result)
print(f"  ROI (hardware $5,500): {kas.roi_days(5500, 800_000, 146, 1, 0.125)} days")

# ──────────────────────────────────────────────────────────────
# Example 3 — Monero CPU mining (Ryzen 9 7950X, 62 KH/s, 170 W)
# ──────────────────────────────────────────────────────────────
print()
print("=" * 55)
print("Example 3: Monero — Ryzen 9 7950X CPU (62 KH/s)")
print("=" * 55)

xmr = MiningCalculator(
    hashrate=62,             # KH/s
    power_watts=170,
    electricity_kwh=0.07,
    pool_fee=0.01,
)

xmr_result = xmr.calculate(
    network_hashrate=3_200_000,  # ~3.2 GH/s in KH/s
    block_reward=0.6,
    block_time_seconds=120,
    coin_price_usd=170,
)
print(xmr_result)

# ──────────────────────────────────────────────────────────────
# Example 4 — Live data via Minerstat API
# ──────────────────────────────────────────────────────────────
print()
print("=" * 55)
print("Example 4: Live data from Minerstat API")
print("=" * 55)

try:
    from fetcher import MinerstatFetcher
    data = MinerstatFetcher().get_coin("BTC")
    print(f"  Live BTC data: price=${data['price']:,.0f}, "
          f"reward={data['block_reward']} BTC, "
          f"block_time={data['block_time']}s")

    live_result = btc.calculate(
        network_hashrate=data["network_hashrate"],
        block_reward=data["block_reward"],
        block_time_seconds=data["block_time"],
        coin_price_usd=data["price"],
    )
    print(live_result)
except Exception as e:
    print(f"  (Skipped — API unavailable: {e})")
