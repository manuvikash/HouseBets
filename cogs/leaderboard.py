"""Leaderboard cog - balance and leaderboard commands."""

import discord
from discord.ext import commands
from discord.commands import SlashCommandGroup
from database import db
from ui import (
    create_balance_embed,
    create_leaderboard_embed,
    BalanceView,
    LeaderboardView,
)


class Leaderboard(commands.Cog):
    """Balance and leaderboard commands."""

    def __init__(self, bot):
        self.bot = bot

    housebets = SlashCommandGroup("housebets", "HouseBets prediction market commands")

    @housebets.command(name="balance", description="Check your balance")
    async def balance(self, ctx: discord.ApplicationContext):
        """Show user balance."""
        await ctx.defer(ephemeral=True)

        user_data = db.get_or_create_user(str(ctx.user.id))
        embed = create_balance_embed(
            ctx.user, user_data["balance"], user_data["total_profit"]
        )
        view = BalanceView()

        await ctx.followup.send(embed=embed, view=view, ephemeral=True)

    @housebets.command(name="leaderboard", description="View the leaderboard")
    async def leaderboard(self, ctx: discord.ApplicationContext):
        """Show leaderboard."""
        await ctx.defer()

        users = db.get_leaderboard()
        embed = create_leaderboard_embed(users, self.bot)
        view = LeaderboardView()

        await ctx.followup.send(embed=embed, view=view)


def setup(bot):
    bot.add_cog(Leaderboard(bot))
