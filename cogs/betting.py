"""Betting cog - handles bet placement and interactions."""

import discord
from discord.ext import commands
from database import db
from ui import create_market_embed, MarketView
from utils import calculate_cost, shares_for_amount, format_currency
import logging

logger = logging.getLogger(__name__)


class Betting(commands.Cog):
    """Betting interaction handlers."""

    def __init__(self, bot):
        self.bot = bot

    async def _process_bet(self, interaction: discord.Interaction, bet_data: dict):
        """Process a bet placement."""
        try:
            market_id = bet_data["market_id"]
            outcome = bet_data["outcome"]
            amount = bet_data["amount"]

            # Get market
            market = db.get_market(market_id)
            if not market:
                await interaction.followup.send("Market not found!", ephemeral=True)
                return

            # Check if market is closed
            from utils import is_market_closed
            from datetime import datetime

            close_time = market["close_time"]
            if isinstance(close_time, str):
                close_time = datetime.fromisoformat(close_time)

            if is_market_closed(close_time):
                await interaction.followup.send(
                    "This market is closed!", ephemeral=True
                )
                return

            # Check if market is resolved
            if market["resolved"]:
                await interaction.followup.send(
                    "This market has already been resolved!", ephemeral=True
                )
                return

            guild_id = market["guild_id"]

            # Get user balance
            user_data = db.get_or_create_user(str(interaction.user.id), guild_id)
            balance = user_data["balance"]

            if amount > balance:
                await interaction.followup.send(
                    f"Insufficient balance! You have {format_currency(balance)}",
                    ephemeral=True,
                )
                return

            # Derive shares from spend amount using AMM inverse formula
            try:
                shares = shares_for_amount(market["liquidity"], outcome, amount)
                cost, new_liquidity = calculate_cost(market["liquidity"], outcome, shares)
            except ValueError as e:
                await interaction.followup.send(f"Error: {str(e)}", ephemeral=True)
                return

            # Place bet
            db.place_bet(
                user_id=str(interaction.user.id),
                guild_id=guild_id,
                market_id=market_id,
                outcome=outcome,
                shares=shares,
                cost=cost,
            )

            # Update user balance
            new_balance = balance - cost
            db.update_balance(str(interaction.user.id), guild_id, new_balance)

            # Update market liquidity
            db.update_market_liquidity(market_id, new_liquidity)

            # Send confirmation
            await interaction.followup.send(
                f"✅ Bet placed!\n"
                f"Bought {shares:.2f} shares of **{outcome}** for {format_currency(cost)}\n"
                f"New balance: {format_currency(new_balance)}",
                ephemeral=True,
            )

            # Update the original message with new prices
            try:
                market = db.get_market(market_id)  # Get updated market
                user_data = db.get_or_create_user(str(interaction.user.id), guild_id)
                position = db.get_user_position(str(interaction.user.id), market_id)

                embed = create_market_embed(
                    market, user_balance=user_data["balance"], user_position=position
                )
                view = MarketView(market, user_data["balance"])

                await interaction.message.edit(embed=embed, view=view)
            except Exception as e:
                logger.error(f"Error updating market message: {e}")

        except Exception as e:
            logger.error(f"Error processing bet: {e}", exc_info=True)
            await interaction.followup.send(
                f"Error placing bet: {str(e)}", ephemeral=True
            )


def setup(bot):
    bot.add_cog(Betting(bot))
