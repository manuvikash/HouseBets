"""Commands cog - all /housebets slash commands in one place."""

import discord
from discord.ext import commands
from discord.commands import SlashCommandGroup
from database import db
from ui import (
    CreateMarketModal,
    create_market_embed,
    create_my_markets_embed,
    MarketView,
    CreatorMarketView,
    create_balance_embed,
    create_leaderboard_embed,
    BalanceView,
    LeaderboardView,
    create_resolved_market_embed,
    MarketSelectionView,
    OutcomeSelectionView,
)
from utils import format_datetime, calculate_payout, format_currency
import config
import logging

logger = logging.getLogger(__name__)


class HouseCommands(commands.Cog):
    """All /housebets slash commands."""

    def __init__(self, bot):
        self.bot = bot

    housebets = SlashCommandGroup("housebets", "HouseBets prediction market commands")

    # ── Markets ──────────────────────────────────────────────────────────────

    @housebets.command(name="new", description="Create a new prediction market")
    @discord.option("target", discord.Member, description="The member this market is about")
    async def create_market(self, ctx: discord.ApplicationContext, target: discord.Member):
        """Open modal to create a new market."""
        if target.id == ctx.user.id:
            await ctx.respond("You cannot create a market about yourself!", ephemeral=True)
            return
        if target.bot:
            await ctx.respond("You cannot create a market about a bot!", ephemeral=True)
            return
        modal = CreateMarketModal(self.bot, target_user=target)
        await ctx.send_modal(modal)
        await modal.wait()
        if hasattr(modal, "result") and hasattr(modal, "interaction"):
            await self._process_market_creation(modal.interaction, modal.result)

    @housebets.command(name="my_markets", description="View your created markets")
    async def my_markets(self, ctx: discord.ApplicationContext):
        """Show user's created markets."""
        await ctx.defer(ephemeral=True)
        guild_id = str(ctx.guild_id)
        markets = db.get_user_markets(str(ctx.user.id), guild_id)
        embed = create_my_markets_embed(markets)
        await ctx.followup.send(embed=embed, ephemeral=True)

    async def _process_market_creation(self, interaction: discord.Interaction, result):
        """Process market creation from modal result."""
        try:
            creator = result["creator"]
            target = result["target"]
            question = result["question"]
            outcomes = result["outcomes"]
            close_time = result["close_time"]
            guild_id = str(interaction.guild_id)

            db.get_or_create_user(str(creator.id), guild_id)
            db.get_or_create_user(str(target.id), guild_id)

            market_id = db.create_market(
                guild_id=guild_id,
                creator_id=str(creator.id),
                target_id=str(target.id),
                question=question,
                outcomes=outcomes,
                close_time=close_time,
            )

            market = db.get_market(market_id)

            await interaction.followup.send(
                f"✅ Market created! ID: {market_id}\n"
                f"Question: {question}\n"
                f"Closes: {format_datetime(close_time)}\n\n"
                f"Sending DMs to eligible users...",
                ephemeral=True,
            )

            guild = interaction.guild
            if guild:
                sent_count = 0
                failed_count = 0
                for member in guild.members:
                    if member.bot or member.id == target.id:
                        continue
                    try:
                        user_data = db.get_or_create_user(str(member.id), guild_id)
                        if member.id == creator.id:
                            # Creator gets buy buttons + resolve button
                            embed = create_market_embed(market, user_balance=user_data["balance"])
                            view = CreatorMarketView(market, user_data["balance"])
                        else:
                            embed = create_market_embed(market, user_balance=user_data["balance"])
                            view = MarketView(market, user_data["balance"])
                        await member.send(embed=embed, view=view)
                        sent_count += 1
                    except discord.Forbidden:
                        failed_count += 1
                        logger.warning(
                            f"Could not DM {member.name} (ID: {member.id}) — "
                            f"they likely have DMs disabled from server members."
                        )
                    except Exception as e:
                        failed_count += 1
                        logger.error(
                            f"Unexpected error sending DM to {member.name} (ID: {member.id}): "
                            f"{type(e).__name__}: {e}",
                            exc_info=True,
                        )
                logger.info(
                    f"Market {market_id}: DMed {sent_count} member(s), "
                    f"{failed_count} failed."
                )

        except Exception as e:
            logger.error(f"Error creating market: {e}", exc_info=True)
            await interaction.followup.send(f"❌ Error creating market: {str(e)}", ephemeral=True)

    @discord.user_command(name="Create Market About")
    async def create_market_context(
        self, ctx: discord.ApplicationContext, user: discord.User
    ):
        """Create a market about a user via context menu."""
        if user.id == ctx.user.id:
            await ctx.respond("You cannot create a market about yourself!", ephemeral=True)
            return
        if user.bot:
            await ctx.respond("You cannot create a market about a bot!", ephemeral=True)
            return
        modal = CreateMarketModal(self.bot, target_user=user)
        await ctx.send_modal(modal)
        await modal.wait()
        if hasattr(modal, "result") and hasattr(modal, "interaction"):
            await self._process_market_creation(modal.interaction, modal.result)

    # ── Leaderboard ──────────────────────────────────────────────────────────

    @housebets.command(name="balance", description="Check your balance")
    async def balance(self, ctx: discord.ApplicationContext):
        """Show user balance."""
        await ctx.defer(ephemeral=True)
        guild_id = str(ctx.guild_id)
        user_data = db.get_or_create_user(str(ctx.user.id), guild_id)
        embed = create_balance_embed(ctx.user, user_data["balance"], user_data["total_profit"])
        view = BalanceView()
        await ctx.followup.send(embed=embed, view=view, ephemeral=True)

    @housebets.command(name="leaderboard", description="View the leaderboard")
    async def leaderboard(self, ctx: discord.ApplicationContext):
        """Show leaderboard."""
        await ctx.defer()
        guild_id = str(ctx.guild_id)
        users = db.get_leaderboard(guild_id)
        embed = create_leaderboard_embed(users, self.bot)
        view = LeaderboardView()
        await ctx.followup.send(embed=embed, view=view)

    # ── Resolution ───────────────────────────────────────────────────────────

    @housebets.command(name="resolve", description="Resolve a market you created")
    async def resolve_market(self, ctx: discord.ApplicationContext):
        """Resolve a market."""
        await ctx.defer(ephemeral=True)
        guild_id = str(ctx.guild_id)

        markets = db.get_user_markets(str(ctx.user.id), guild_id)
        unresolved = [m for m in markets if not m["resolved"]]

        if not unresolved:
            await ctx.followup.send("You don't have any unresolved markets!", ephemeral=True)
            return

        view = MarketSelectionView(unresolved)
        await ctx.followup.send("Select a market to resolve:", view=view, ephemeral=True)
        await view.wait()

        if not view.selected_market_id:
            return

        market = db.get_market(view.selected_market_id)
        outcome_view = OutcomeSelectionView(market["id"], market["outcomes"])
        # view.interaction is the select interaction — respond to it
        await view.interaction.response.send_message(
            "Select the winning outcome:", view=outcome_view, ephemeral=True
        )
        await outcome_view.wait()
        if outcome_view.selected_outcome:
            result = {
                "market_id": market["id"],
                "winning_outcome": outcome_view.selected_outcome,
            }
            # outcome_view.interaction was deferred; use followup
            await self._process_resolution(outcome_view.interaction, result)

    async def _process_resolution(self, interaction: discord.Interaction, result):
        """Process market resolution."""
        try:
            market_id = result["market_id"]
            winning_outcome = result["winning_outcome"]

            market = db.get_market(market_id)
            if not market:
                await interaction.followup.send("Market not found!", ephemeral=True)
                return

            if market["creator_id"] != str(interaction.user.id):
                await interaction.followup.send(
                    "You can only resolve markets you created!", ephemeral=True
                )
                return

            guild_id = market["guild_id"]

            bets = db.get_market_bets(market_id)
            payouts = {}
            total_volume = 0
            # bet_details: {user_id: {bets: {outcome: {shares, cost}}, total_cost}}
            bet_details = {}

            for bet in bets:
                user_id = bet["user_id"]
                outcome = bet["outcome"]
                cost = bet["cost"]
                shares = bet["shares"]
                total_volume += cost

                if user_id not in bet_details:
                    bet_details[user_id] = {"bets": {}, "total_cost": 0}
                if outcome not in bet_details[user_id]["bets"]:
                    bet_details[user_id]["bets"][outcome] = {"shares": 0, "cost": 0}
                bet_details[user_id]["bets"][outcome]["shares"] += shares
                bet_details[user_id]["bets"][outcome]["cost"] += cost
                bet_details[user_id]["total_cost"] += cost

                payout = calculate_payout(shares, outcome == winning_outcome)
                if payout > 0:
                    payouts[user_id] = payouts.get(user_id, 0) + payout

            # Annotate profit/loss per bettor
            for user_id, detail in bet_details.items():
                payout = payouts.get(user_id, 0)
                detail["payout"] = payout
                detail["profit"] = payout - detail["total_cost"]

            for user_id, payout in payouts.items():
                user_data = db.get_or_create_user(user_id, guild_id)
                db.update_balance(user_id, guild_id, user_data["balance"] + payout)
                user_bets = [b for b in bets if b["user_id"] == user_id]
                profit = payout - sum(b["cost"] for b in user_bets)
                db.update_profit(user_id, guild_id, profit)

            db.resolve_market(market_id, winning_outcome)

            await interaction.followup.send(
                f"✅ Market resolved!\n"
                f"Winning outcome: **{winning_outcome}**\n"
                f"Total volume: {format_currency(total_volume)}\n"
                f"Payouts distributed: {format_currency(sum(payouts.values()))}",
                ephemeral=True,
            )

            await self._post_to_feed(interaction, market, payouts, bet_details, total_volume)

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
            await interaction.followup.send(f"Error resolving market: {str(e)}", ephemeral=True)

    async def _post_to_feed(self, interaction: discord.Interaction, market, payouts, bet_details, total_volume):
        """Post resolved market to feed channel."""
        try:
            guild = interaction.guild or self.bot.get_guild(int(market["guild_id"]))
            if not guild:
                return

            feed_channel = discord.utils.get(guild.text_channels, name=config.FEED_CHANNEL_NAME)
            if not feed_channel:
                try:
                    feed_channel = await guild.create_text_channel(
                        config.FEED_CHANNEL_NAME,
                        topic="HouseBets resolved markets feed",
                    )
                    logger.info(f"Created feed channel: {config.FEED_CHANNEL_NAME}")
                except discord.Forbidden:
                    logger.error("Missing permissions to create feed channel")
                    return

            resolution_embed = create_resolved_market_embed(market, payouts, bet_details, total_volume)
            await feed_channel.send(
                f"📢 **Market #{market['id']} has been resolved!**\n"
                f"> {market['question']}\n"
                f"🎯 Winner: **{market['winning_outcome']}**  "
                f"| 💵 Volume: {format_currency(total_volume)}  "
                f"| 💸 Paid out: {format_currency(sum(payouts.values()))}",
                embed=resolution_embed,
            )

            leaderboard_users = db.get_leaderboard(market["guild_id"])
            leaderboard_embed = create_leaderboard_embed(leaderboard_users, self.bot)
            leaderboard_embed.title = "🏆 Updated Leaderboard"
            await feed_channel.send(embed=leaderboard_embed)

            logger.info(f"Posted market {market['id']} resolution to feed")

        except Exception as e:
            logger.error(f"Error posting to feed: {e}", exc_info=True)


def setup(bot):
    bot.add_cog(HouseCommands(bot))
