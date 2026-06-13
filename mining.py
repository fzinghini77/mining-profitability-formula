"""
mining.py — Core Proof-of-Work mining profitability calculator.

The standard model:
  daily_revenue = (hashrate / network_hashrate) * blocks_per_day * block_reward * coin_price
  daily_cost    = (power_watts / 1000) * 24 * electricity_kwh
  daily_profit  = daily_revenue * (1 - pool_fee) - daily_cost

Hashrate units must be consistent between `hashrate` and `network_hashrate`.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class MiningResult:
    daily_revenue_usd: float
    daily_cost_usd: float
    daily_profit_usd: float
    weekly_profit_usd: float
    monthly_profit_usd: float
    yearly_profit_usd: float
    break_even_kwh: Optional[float]   # electricity price at which profit = 0
    pool_share_pct: float             # your % of total network hashrate

    def __str__(self) -> str:
        lines = [
            "MiningResult(",
            f"  daily_revenue_usd  = {self.daily_revenue_usd:>10.4f}",
            f"  daily_cost_usd     = {self.daily_cost_usd:>10.4f}",
            f"  daily_profit_usd   = {self.daily_profit_usd:>10.4f}",
            f"  monthly_profit_usd = {self.monthly_profit_usd:>10.4f}",
            f"  yearly_profit_usd  = {self.yearly_profit_usd:>10.4f}",
            f"  break_even_kwh     = {self.break_even_kwh:>10.4f}" if self.break_even_kwh else "  break_even_kwh     =       None",
            f"  pool_share_pct     = {self.pool_share_pct:>10.8f} %",
            ")",
        ]
        return "\n".join(lines)


class MiningCalculator:
    """
    Calculates PoW mining profitability for a single rig or farm.

    Parameters
    ----------
    hashrate : float
        Your mining hashrate. Units must match network_hashrate in calculate().
    power_watts : float
        Total power draw of your rig in watts.
    electricity_kwh : float
        Electricity cost in USD per kWh.
    pool_fee : float
        Pool fee as a decimal fraction (e.g. 0.01 for 1 %).
    """

    def __init__(
        self,
        hashrate: float,
        power_watts: float,
        electricity_kwh: float,
        pool_fee: float = 0.01,
        # Legacy kwarg aliases kept for compatibility
        hashrate_th: float = None,
    ):
        self.hashrate = hashrate if hashrate_th is None else hashrate_th
        self.power_watts = power_watts
        self.electricity_kwh = electricity_kwh
        self.pool_fee = pool_fee

    def calculate(
        self,
        network_hashrate: float,
        block_reward: float,
        block_time_seconds: float,
        coin_price_usd: float,
        # Legacy kwarg alias
        network_hashrate_th: float = None,
    ) -> MiningResult:
        """
        Compute profitability given current network conditions.

        Parameters
        ----------
        network_hashrate : float
            Total network hashrate (same unit as self.hashrate).
        block_reward : float
            Current block reward in coins (post-halving value).
        block_time_seconds : float
            Target seconds per block (e.g. 600 for Bitcoin).
        coin_price_usd : float
            Current coin price in USD.

        Returns
        -------
        MiningResult
        """
        if network_hashrate_th is not None:
            network_hashrate = network_hashrate_th

        blocks_per_day = 86_400 / block_time_seconds
        pool_share = self.hashrate / network_hashrate

        daily_revenue = pool_share * blocks_per_day * block_reward * coin_price_usd
        daily_cost    = (self.power_watts / 1_000) * 24 * self.electricity_kwh
        daily_profit  = daily_revenue * (1 - self.pool_fee) - daily_cost

        # Electricity price at which profit flips to zero
        daily_revenue_net = daily_revenue * (1 - self.pool_fee)
        if self.power_watts > 0:
            break_even = daily_revenue_net / ((self.power_watts / 1_000) * 24)
        else:
            break_even = None

        return MiningResult(
            daily_revenue_usd  = round(daily_revenue, 6),
            daily_cost_usd     = round(daily_cost, 6),
            daily_profit_usd   = round(daily_profit, 6),
            weekly_profit_usd  = round(daily_profit * 7, 4),
            monthly_profit_usd = round(daily_profit * 30.44, 4),
            yearly_profit_usd  = round(daily_profit * 365.25, 4),
            break_even_kwh     = round(break_even, 6) if break_even else None,
            pool_share_pct     = pool_share * 100,
        )

    def roi_days(self, hardware_cost_usd: float, network_hashrate: float,
                 block_reward: float, block_time_seconds: float,
                 coin_price_usd: float) -> Optional[float]:
        """Return estimated days to break even on hardware cost, or None if unprofitable."""
        result = self.calculate(network_hashrate, block_reward, block_time_seconds, coin_price_usd)
        if result.daily_profit_usd <= 0:
            return None
        return round(hardware_cost_usd / result.daily_profit_usd, 1)
