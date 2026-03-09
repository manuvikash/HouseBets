"""HouseBets Discord Bot - Main entry point."""

import discord
from discord.ext import commands
import logging
import sys
import config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler("housebets.log")],
)

logger = logging.getLogger(__name__)

# Bot configuration
intents = discord.Intents.default()
intents.members = True  # Required to see guild members
intents.message_content = True  # For any message-based features

bot = discord.Bot(
    intents=intents,
    description="HouseBets - Private prediction markets for your Discord server",
)


@bot.event
async def on_ready():
    """Called when the bot is ready."""
    logger.info(f"Logged in as {bot.user.name} ({bot.user.id})")
    logger.info(f"Connected to {len(bot.guilds)} guild(s)")

    # Log guilds and cached member counts
    for guild in bot.guilds:
        cached = len([m for m in guild.members if not m.bot])
        logger.info(
            f"  - {guild.name} (ID: {guild.id}, "
            f"Total: {guild.member_count}, Cached non-bots: {cached})"
        )
        if cached == 0:
            logger.warning(
                f"  ⚠ No members cached for {guild.name} — "
                "Server Members Intent may not be enabled in the Developer Portal."
            )

    logger.info("Bot is ready!")


@bot.event
async def on_guild_join(guild):
    """Called when bot joins a new guild."""
    logger.info(f"Joined new guild: {guild.name} (ID: {guild.id})")


@bot.event
async def on_application_command_error(
    ctx: discord.ApplicationContext, error: discord.DiscordException
):
    """Handle command errors."""
    logger.error(f"Command error in {ctx.command}: {error}", exc_info=True)

    if isinstance(error, commands.CommandOnCooldown):
        await ctx.respond(
            f"This command is on cooldown. Try again in {error.retry_after:.1f}s",
            ephemeral=True,
        )
    elif isinstance(error, commands.MissingPermissions):
        await ctx.respond(
            "You don't have permission to use this command!", ephemeral=True
        )
    else:
        await ctx.respond(f"An error occurred: {str(error)}", ephemeral=True)


@bot.event
async def on_error(event, *args, **kwargs):
    """Handle general errors."""
    logger.error(f"Error in {event}", exc_info=True)


# Load cogs
cogs_to_load = ["cogs.commands", "cogs.betting"]

for cog in cogs_to_load:
    try:
        bot.load_extension(cog)
        logger.info(f"Loaded cog: {cog}")
    except Exception as e:
        logger.error(f"Failed to load cog {cog}: {e}", exc_info=True)


def main():
    """Main entry point."""
    if not config.BOT_TOKEN:
        logger.error("BOT_TOKEN not found in environment variables!")
        logger.error("Please set BOT_TOKEN in your .env file")
        sys.exit(1)

    try:
        logger.info("Starting HouseBets bot...")
        bot.run(config.BOT_TOKEN)
    except discord.LoginFailure:
        logger.error("Invalid bot token!")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
