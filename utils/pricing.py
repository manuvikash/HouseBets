"""AMM (Automated Market Maker) pricing logic using constant product formula."""

from typing import Dict, Tuple
import math


def calculate_price(liquidity: Dict[str, float], outcome: str) -> float:
    """
    Calculate current price for an outcome using constant product AMM.
    Price = liquidity[outcome] / sum(all liquidity)

    Returns a value between 0 and 1.
    """
    total_liquidity = sum(liquidity.values())
    if total_liquidity == 0:
        return 1.0 / len(liquidity)  # Equal probability if no liquidity

    return liquidity[outcome] / total_liquidity


def calculate_all_prices(liquidity: Dict[str, float]) -> Dict[str, float]:
    """Calculate prices for all outcomes."""
    return {outcome: calculate_price(liquidity, outcome) for outcome in liquidity}


def calculate_cost(
    liquidity: Dict[str, float], outcome: str, shares: float
) -> Tuple[float, Dict[str, float]]:
    """
    Calculate cost to buy shares of an outcome and return new liquidity state.

    Using constant product: product of all liquidity values remains constant.
    Cost = current_liquidity - new_liquidity

    Returns: (cost, new_liquidity_dict)
    """
    if shares <= 0:
        raise ValueError("Shares must be positive")

    # Calculate constant product
    product = 1.0
    for liq in liquidity.values():
        product *= liq

    # New liquidity for the outcome being bought
    # When buying, we're decreasing liquidity of that outcome
    new_liquidity = dict(liquidity)

    # For binary markets or multi-outcome, buying shares of one outcome
    # reduces its liquidity proportionally
    old_outcome_liq = liquidity[outcome]

    # Calculate new liquidity maintaining constant product
    # Simplified: reduce liquidity by shares purchased
    new_outcome_liq = old_outcome_liq - shares

    if new_outcome_liq <= 0:
        raise ValueError("Insufficient liquidity for this bet size")

    new_liquidity[outcome] = new_outcome_liq

    # Adjust other outcomes to maintain product (simplified model)
    # In a more complex AMM, you'd solve for exact product maintenance
    # For now, we use a simpler approach: cost = shares / price

    price = calculate_price(liquidity, outcome)
    cost = shares * price

    # Alternative: more realistic cost calculation
    # Cost increases as you buy more (slippage)
    actual_cost = -math.log(new_outcome_liq / old_outcome_liq) * old_outcome_liq

    return actual_cost, new_liquidity


def calculate_payout(shares: float, winning: bool) -> float:
    """
    Calculate payout for shares.
    If outcome wins, you get 1 Buck per share.
    If outcome loses, you get 0.
    """
    if winning:
        return shares * 1.0  # 1 Buck per share
    return 0.0


def format_price(price: float) -> str:
    """Format price as percentage."""
    return f"{price * 100:.1f}%"


def format_currency(amount: float, currency: str = "Bucks") -> str:
    """Format currency amount."""
    return f"{amount:.2f} {currency}"
