"""Markets cog - handles market creation and management."""

import discord
from discord.ext import commands
from discord.commands import SlashCommandGroup
from database import db
from ui import (
    CreateMarketModal,
    create_market_embed,
    create_my_markets_embed,
    MarketView,
)
from utils import format_datetime
import logging

logger = logging.getLogger(__name__)


class Markets(commands.Cog):
    """Market creation and management commands."""

    def __init__(self, bot):
        self.bot = bot

    housebets = SlashCommandGroup("housebets", "HouseBets prediction market commands")

    @housebets.command(name="new", description="Create a new prediction market")
    async def create_market(self, ctx: discord.ApplicationContext):
        """Open modal to create a new market."""
        modal = CreateMarketModal(self.bot)
        await ctx.send_modal(modal)

        # Wait for modal submission
        await modal.wait()

        if hasattr(modal, "result"):
            await self._process_market_creation(ctx, modal.result)

    @housebets.command(name="my_markets", description="View your created markets")
    async def my_markets(self, ctx: discord.ApplicationContext):
        """Show user's created markets."""
        await ctx.defer(ephemeral=True)

        markets = db.get_user_markets(str(ctx.user.id))
        embed = create_my_markets_embed(markets)

        await ctx.followup.send(embed=embed, ephemeral=True)

    async def _process_market_creation(self, ctx, result):
        """Process market creation from modal result."""
        try:
            creator = result["creator"]
            target = result["target"]
            question = result["question"]
            outcomes = result["outcomes"]
            close_time = result["close_time"]

            # Ensure both users exist in database
            db.get_or_create_user(str(creator.id))
            db.get_or_create_user(str(target.id))

            # Create market
            market_id = db.create_market(
                creator_id=str(creator.id),
                target_id=str(target.id),
                question=question,
                outcomes=outcomes,
                close_time=close_time,
            )

            market = db.get_market(market_id)

            # Send confirmation to creator
            await ctx.followup.send(
                f"✅ Market created! ID: {market_id}\n"
                f"Question: {question}\n"
                f"Closes: {format_datetime(close_time)}\n\n"
                f"Sending DMs to eligible users...",
                ephemeral=True,
            )

            # Send market to all guild members except target and creator
            guild = ctx.guild
            if guild:
                sent_count = 0
                for member in guild.members:
                    # Skip bots, target, and creator
                    if member.bot or member.id == target.id or member.id == creator.id:
                        continue

                    try:
                        # Ensure user exists in database
                        user_data = db.get_or_create_user(str(member.id))

                        # Create market embed with user's balance
                        embed = create_market_embed(
                            market, user_balance=user_data["balance"]
                        )

                        # Create view with buy buttons
                        view = MarketView(market, user_data["balance"])

                        # Send DM
                        await member.send(embed=embed, view=view)
                        sent_count += 1

                    except discord.Forbidden:
                        logger.warning(f"Could not send DM to {member.name}")
                        continue
                    except Exception as e:
                        logger.error(f"Error sending DM to {member.name}: {e}")
                        continue

                logger.info(f"Market {market_id} sent to {sent_count} users")

        except Exception as e:
            logger.error(f"Error creating market: {e}", exc_info=True)
            await ctx.followup.send(
                f"❌ Error creating market: {str(e)}", ephemeral=True
            )

    # Context menu command for creating market about a user
    @discord.user_command(name="Create Market About")
    async def create_market_context(
        self, ctx: discord.ApplicationContext, user: discord.User
    ):
        """Create a market about a user via context menu."""
        if user.id == ctx.user.id:
            await ctx.respond(
                "You cannot create a market about yourself!", ephemeral=True
            )
            return

        if user.bot:
            await ctx.respond("You cannot create a market about a bot!", ephemeral=True)
            return

        # Open modal with target pre-filled
        modal = CreateMarketModal(self.bot, target_user=user)
        await ctx.send_modal(modal)

        # Wait for modal submission
        await modal.wait()

        if hasattr(modal, "result"):
            await self._process_market_creation(ctx, modal.result)


def setup(bot):
    bot.add_cog(Markets(bot))
