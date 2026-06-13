"""
fetcher.py — Live network data from the Minerstat API.

Pulls the same fields used by MiningReturns.com:
  - network_hashrate  (normalised to the hashrate unit used by MiningCalculator)
  - block_reward
  - block_time
  - price (USD)

Usage:
    from fetcher import MinerstatFetcher
    data = MinerstatFetcher().get_coin("BTC")
"""

import urllib.request
import json
from typing import Dict, Any, Optional

# Minerstat coin identifiers
COIN_MAP = {
    "BTC":  "BTC",
    "LTC":  "LTC",
    "XMR":  "XMR",
    "KAS":  "KAS",
    "ETC":  "ETC",
    "RVN":  "RVN",
    "DOGE": "DOGE",
    "BCH":  "BCH",
    "ZEC":  "ZEC",
    "ALPH": "ALPH",
}

# Divisors to convert raw API hashrate to the unit expected by MiningCalculator
# MiningCalculator uses TH/s for SHA-256/kHeavyHash, MH/s for GPU coins, KH/s for RandomX
HASHRATE_DIVISORS = {
    "BTC":  1e12,   # H/s → TH/s
    "BCH":  1e12,
    "LTC":  1e6,    # H/s → MH/s
    "DOGE": 1e6,
    "ETC":  1e6,
    "RVN":  1e6,
    "ZEC":  1,      # Sol/s — already in natural unit
    "XMR":  1e3,    # H/s → KH/s
    "KAS":  1e12,   # H/s → TH/s
    "ALPH": 1e12,
}


class MinerstatFetcher:
    BASE_URL = "https://api.minerstat.com/v2/coins"

    def get_coin(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch live data for a single coin.

        Returns a dict with keys:
          network_hashrate, block_reward, block_time, price
        All values are already normalised for use with MiningCalculator.
        """
        symbol = symbol.upper()
        if symbol not in COIN_MAP:
            raise ValueError(f"Unsupported coin: {symbol}. Supported: {list(COIN_MAP)}")

        url = f"{self.BASE_URL}?list={COIN_MAP[symbol]}"
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read())[0]

        divisor = HASHRATE_DIVISORS.get(symbol, 1)
        return {
            "symbol":           symbol,
            "name":             data.get("name", symbol),
            "algorithm":        data.get("algorithm", ""),
            "network_hashrate": data["network_hashrate"] / divisor,
            "block_reward":     data["reward"],
            "block_time":       data["block_time"],
            "price":            data["price"],
        }

    def get_coins(self, symbols: list) -> Dict[str, Dict[str, Any]]:
        """Fetch multiple coins in one request."""
        query = ",".join(COIN_MAP[s.upper()] for s in symbols if s.upper() in COIN_MAP)
        url = f"{self.BASE_URL}?list={query}"
        with urllib.request.urlopen(url, timeout=10) as resp:
            raw = json.loads(resp.read())

        result = {}
        for item in raw:
            sym = item["coin"]
            divisor = HASHRATE_DIVISORS.get(sym, 1)
            result[sym] = {
                "symbol":           sym,
                "name":             item.get("name", sym),
                "algorithm":        item.get("algorithm", ""),
                "network_hashrate": item["network_hashrate"] / divisor,
                "block_reward":     item["reward"],
                "block_time":       item["block_time"],
                "price":            item["price"],
            }
        return result
