# mining-profitability-formula

**Python implementation of the standard Proof-of-Work mining profitability model.**

This library implements the same formula used by [MiningReturns.com](https://miningreturns.com) to estimate daily, weekly and monthly earnings for any PoW coin — given your hashrate, power consumption, electricity cost and pool fee.

## Background

The profitability of a mining operation depends on your share of the total network hashrate. The standard model is:

```
daily_revenue  = (hashrate / network_hashrate) × blocks_per_day × block_reward × coin_price
daily_cost     = (power_watts / 1000) × 24 × electricity_price_kwh
daily_profit   = daily_revenue − daily_cost − (daily_revenue × pool_fee)
```

As an Electronic Engineer with a background in Systems Theory, I find it useful to think of the difficulty adjustment mechanism as a **feedback control loop**: the network targets a fixed block time (e.g. 10 min for Bitcoin) by adjusting the target hash, compensating for changes in total hashrate. This library exposes that adjustment explicitly so you can model profitability under different hashrate scenarios.

## Installation

```bash
pip install -r requirements.txt
```

## Quick start

```python
from mining import MiningCalculator

calc = MiningCalculator(
    hashrate_th=100,          # your hashrate in TH/s
    power_watts=3200,         # rig power draw
    electricity_kwh=0.07,     # electricity cost in USD/kWh
    pool_fee=0.01,            # 1 %
)

result = calc.calculate(
    network_hashrate_th=700e6,   # BTC network ~700 EH/s = 700_000_000 TH/s
    block_reward=3.125,          # post-2024-halving
    block_time_seconds=600,
    coin_price_usd=65000,
)

print(result)
```

Output:
```
MiningResult(
  daily_revenue_usd  = 12.47,
  daily_cost_usd     =  5.38,
  daily_profit_usd   =  6.97,
  monthly_profit_usd = 209.03,
  break_even_kwh     =  0.162,
  pool_share_pct     =  0.0000143 %
)
```

## Live data integration

`fetcher.py` pulls live network data from the [Minerstat API](https://minerstat.com) (the same source used by MiningReturns.com):

```python
from fetcher import MinerstatFetcher

fetcher = MinerstatFetcher()
data = fetcher.get_coin("BTC")

result = calc.calculate(
    network_hashrate_th=data["network_hashrate"],
    block_reward=data["block_reward"],
    block_time_seconds=data["block_time"],
    coin_price_usd=data["price"],
)
```

## Supported coins

Any PoW coin with known network hashrate, block reward, and block time. Tested with:

| Coin | Algorithm | Unit |
|------|-----------|------|
| Bitcoin (BTC) | SHA-256 | TH/s |
| Litecoin (LTC) | Scrypt | MH/s |
| Monero (XMR) | RandomX | KH/s |
| Kaspa (KAS) | kHeavyHash | TH/s |
| Ethereum Classic (ETC) | Etchash | MH/s |
| Ravencoin (RVN) | KawPoW | MH/s |
| Alephium (ALPH) | Blake3 | TH/s |

## Files

```
mining-profitability-formula/
├── mining.py        # Core MiningCalculator class
├── fetcher.py       # Minerstat API client
├── examples.py      # Usage examples for multiple coins
├── requirements.txt
└── README.md
```

## License

MIT — free to use, modify and redistribute.

---

*This model is used in production at [MiningReturns.com](https://miningreturns.com) — a free real-time cryptocurrency mining profitability calculator.*
