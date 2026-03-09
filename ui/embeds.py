"""Discord embed builders."""

import discord
from typing import Dict, List, Optional
from datetime import datetime
from utils import format_price, format_currency, format_datetime, calculate_all_prices
import config


def create_market_embed(
    market: Dict,
    user_balance: Optional[float] = None,
    user_position: Optional[Dict] = None,
) -> discord.Embed:
    """Create embed for a market card in DM."""

    # Calculate current prices
    prices = calculate_all_prices(market["liquidity"])

    embed = discord.Embed(
        title="📊 New Market",
        description=market["question"],
        color=discord.Color.blue(),
        timestamp=datetime.now(),
    )

    # Add outcomes with current prices
    outcomes_text = ""
    for outcome in market["outcomes"]:
        price = prices[outcome]
        outcomes_text += f"**{outcome}**: {format_price(price)}\n"

    embed.add_field(name="Outcomes & Prices", value=outcomes_text, inline=False)

    # Add close time
    close_time = market["close_time"]
    if isinstance(close_time, str):
        close_time = datetime.fromisoformat(close_time)

    embed.add_field(name="⏰ Closes", value=format_datetime(close_time), inline=True)

    # Add user balance if provided
    if user_balance is not None:
        embed.add_field(
            name="💰 Your Balance", value=format_currency(user_balance), inline=True
        )

    # Add user position if they have one
    if user_position:
        position_text = ""
        for outcome, pos in user_position.items():
            position_text += f"**{outcome}**: {pos['shares']:.2f} shares\n"

        if position_text:
            embed.add_field(name="📈 Your Position", value=position_text, inline=False)

    embed.set_footer(text=f"Market ID: {market['id']}")

    return embed


def create_balance_embed(user, balance: float, total_profit: float) -> discord.Embed:
    """Create embed showing user balance."""

    embed = discord.Embed(
        title="💰 Your Balance",
        color=discord.Color.green() if total_profit >= 0 else discord.Color.red(),
        timestamp=datetime.now(),
    )

    embed.add_field(name="Current Balance", value=format_currency(balance), inline=True)

    embed.add_field(
        name="Total Profit/Loss", value=format_currency(total_profit), inline=True
    )

    embed.set_footer(text=f"User: {user.name}")

    return embed


def create_leaderboard_embed(users: List[Dict], bot) -> discord.Embed:
    """Create leaderboard embed."""

    embed = discord.Embed(
        title="🏆 HouseBets Leaderboard",
        description="Top players by balance",
        color=discord.Color.gold(),
        timestamp=datetime.now(),
    )

    if not users:
        embed.add_field(
            name="No players yet", value="Be the first to make a bet!", inline=False
        )
        return embed

    medals = ["🥇", "🥈", "🥉"]

    leaderboard_text = ""
    for i, user_data in enumerate(users[:10]):
        medal = medals[i] if i < 3 else f"{i + 1}."
        balance = user_data["balance"]

        # Try to get username (may not be cached)
        user_id = user_data["discord_id"]
        leaderboard_text += f"{medal} <@{user_id}>: {format_currency(balance)}\n"

    embed.add_field(
        name="Rankings",
        value=leaderboard_text if leaderboard_text else "No data yet",
        inline=False,
    )

    return embed


def create_resolved_market_embed(
    market: Dict, payouts: Dict[str, float], bet_details: Dict, total_volume: float
) -> discord.Embed:
    """Create embed for resolved market announcement with per-bettor breakdown."""

    embed = discord.Embed(
        title="✅ Market Resolved",
        description=market["question"],
        color=discord.Color.green(),
        timestamp=datetime.now(),
    )

    embed.add_field(
        name="🎯 Winning Outcome",
        value=f"**{market['winning_outcome']}**",
        inline=False,
    )

    embed.add_field(
        name="💵 Total Volume", value=format_currency(total_volume), inline=True
    )

    embed.add_field(
        name="👥 Total Payouts",
        value=format_currency(sum(payouts.values())),
        inline=True,
    )

    # Per-bettor breakdown
    if bet_details:
        lines = []
        # Sort: winners first (profit > 0), then losers
        sorted_bettors = sorted(
            bet_details.items(), key=lambda x: x[1]["profit"], reverse=True
        )
        for user_id, detail in sorted_bettors:
            # Summarise what they bet on
            bets_summary = ", ".join(
                f"{outcome} ({format_currency(pos['cost'])})"
                for outcome, pos in detail["bets"].items()
            )
            profit = detail["profit"]
            profit_str = (
                f"+{format_currency(profit)}" if profit >= 0 else format_currency(profit)
            )
            payout = detail["payout"]
            line = (
                f"<@{user_id}>: {bets_summary} → "
                f"{'🎉' if profit >= 0 else '📉'} {profit_str}"
                + (f" (payout: {format_currency(payout)})" if payout > 0 else "")
            )
            lines.append(line)

        embed.add_field(
            name="📋 Bet Breakdown",
            value="\n".join(lines) if lines else "No bets placed",
            inline=False,
        )

    embed.set_footer(text=f"Market ID: {market['id']}")

    return embed


def create_my_markets_embed(markets: List[Dict]) -> discord.Embed:
    """Create embed showing user's created markets."""

    embed = discord.Embed(
        title="📋 Your Markets", color=discord.Color.blue(), timestamp=datetime.now()
    )

    if not markets:
        embed.add_field(
            name="No markets yet",
            value="Create your first market with `/housebets new`",
            inline=False,
        )
        return embed

    for market in markets[:10]:  # Show max 10
        status = "✅ Resolved" if market["resolved"] else "🔴 Active"
        close_time = market["close_time"]
        if isinstance(close_time, str):
            close_time = datetime.fromisoformat(close_time)

        value = f"{status} | Closes: {format_datetime(close_time)}"
        if market["resolved"]:
            value = f"{status} | Winner: **{market['winning_outcome']}**"

        embed.add_field(
            name=f"[{market['id']}] {market['question'][:100]}",
            value=value,
            inline=False,
        )

    return embed
