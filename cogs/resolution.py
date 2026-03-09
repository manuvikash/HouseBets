"""Resolution cog - handles market resolution."""

import discord
from discord.ext import commands
from discord.commands import SlashCommandGroup
from database import db
from ui import create_resolved_market_embed, MarketSelectionView, ResolveMarketModal
from utils import calculate_payout, format_currency
import config
import logging

logger = logging.getLogger(__name__)


class Resolution(commands.Cog):
    """Market resolution commands."""

    def __init__(self, bot):
        self.bot = bot

    housebets = SlashCommandGroup("housebets", "HouseBets prediction market commands")

    @housebets.command(name="resolve", description="Resolve a market you created")
    async def resolve_market(self, ctx: discord.ApplicationContext):
        """Resolve a market."""
        await ctx.defer(ephemeral=True)

        # Get user's unresolved markets
        markets = db.get_user_markets(str(ctx.user.id))
        unresolved = [m for m in markets if not m["resolved"]]

        if not unresolved:
            await ctx.followup.send(
                "You don't have any unresolved markets!", ephemeral=True
            )
            return

        # Show selection view
        view = MarketSelectionView(unresolved)
        await ctx.followup.send(
            "Select a market to resolve:", view=view, ephemeral=True
        )

        # Wait for selection
        await view.wait()

        if view.selected_market_id:
            market = db.get_market(view.selected_market_id)

            # Show modal to select winning outcome
            modal = ResolveMarketModal(market["id"], market["outcomes"])
            await ctx.send_modal(modal)

            # Wait for modal
            await modal.wait()

            if hasattr(modal, "result"):
                await self._process_resolution(ctx, modal.result)

    async def _process_resolution(self, ctx, result):
        """Process market resolution."""
        try:
            market_id = result["market_id"]
            winning_outcome = result["winning_outcome"]

            # Get market
            market = db.get_market(market_id)
            if not market:
                await ctx.followup.send("Market not found!", ephemeral=True)
                return

            # Verify user is creator
            if market["creator_id"] != str(ctx.user.id):
                await ctx.followup.send(
                    "You can only resolve markets you created!", ephemeral=True
                )
                return

            # Get all bets for this market
            bets = db.get_market_bets(market_id)

            # Calculate payouts
            payouts = {}
            total_volume = 0

            for bet in bets:
                user_id = bet["user_id"]
                outcome = bet["outcome"]
                shares = bet["shares"]
                cost = bet["cost"]

                total_volume += cost

                # Calculate payout
                payout = calculate_payout(shares, outcome == winning_outcome)

                if payout > 0:
                    if user_id not in payouts:
                        payouts[user_id] = 0
                    payouts[user_id] += payout

            # Update user balances and profits
            for user_id, payout in payouts.items():
                user_data = db.get_or_create_user(user_id)
                new_balance = user_data["balance"] + payout
                db.update_balance(user_id, new_balance)

                # Calculate profit (payout - cost)
                user_bets = [b for b in bets if b["user_id"] == user_id]
                total_cost = sum(b["cost"] for b in user_bets)
                profit = payout - total_cost
                db.update_profit(user_id, profit)

            # Resolve market
            db.resolve_market(market_id, winning_outcome)

            # Send confirmation to creator
            await ctx.followup.send(
                f"✅ Market resolved!\n"
                f"Winning outcome: **{winning_outcome}**\n"
                f"Total volume: {format_currency(total_volume)}\n"
                f"Payouts distributed: {format_currency(sum(payouts.values()))}",
                ephemeral=True,
            )

            # Post to feed channel
            await self._post_to_feed(ctx, market, payouts, total_volume)

            # Send DM notifications to winners
            for user_id, payout in payouts.items():
                try:
                    user = await self.bot.fetch_user(int(user_id))
                    await user.send(
                        f"🎉 You won {format_currency(payout)} from market:\n"
                        f"**{market['question']}**\n"
                        f"Winning outcome: **{winning_outcome}**"
                    )
                except Exception as e:
                    logger.error(f"Could not send DM to user {user_id}: {e}")

        except Exception as e:
            logger.error(f"Error resolving market: {e}", exc_info=True)
            await ctx.followup.send(f"Error resolving market: {str(e)}", ephemeral=True)

    async def _post_to_feed(self, ctx, market, payouts, total_volume):
        """Post resolved market to feed channel."""
        try:
            guild = ctx.guild
            if not guild:
                return

            # Find or create feed channel
            feed_channel = discord.utils.get(
                guild.text_channels, name=config.FEED_CHANNEL_NAME
            )

            if not feed_channel:
                # Try to create the channel
                try:
                    feed_channel = await guild.create_text_channel(
                        config.FEED_CHANNEL_NAME,
                        topic="HouseBets resolved markets feed",
                    )
                    logger.info(f"Created feed channel: {config.FEED_CHANNEL_NAME}")
                except discord.Forbidden:
                    logger.error("Missing permissions to create feed channel")
                    return

            # Create and send embed
            embed = create_resolved_market_embed(market, payouts, total_volume)
            await feed_channel.send(embed=embed)

            logger.info(f"Posted market {market['id']} resolution to feed")

        except Exception as e:
            logger.error(f"Error posting to feed: {e}", exc_info=True)


def setup(bot):
    bot.add_cog(Resolution(bot))
