"""Discord UI Modal forms."""

import discord
from datetime import datetime
from utils import parse_time_duration


class CreateMarketModal(discord.ui.Modal):
    """Modal for creating a new market."""

    def __init__(self, bot, target_user: discord.User = None):
        super().__init__(title="Create New Market")
        self.bot = bot
        self.target_user = target_user


        # Question
        self.question_input = discord.ui.InputText(
            label="Market Question",
            placeholder="e.g., Will [target] clean their room this week?",
            style=discord.InputTextStyle.long,
            required=True,
            max_length=500,
        )
        self.add_item(self.question_input)

        # Outcomes
        self.outcomes_input = discord.ui.InputText(
            label="Outcomes (comma-separated)",
            placeholder="Yes,No (or custom outcomes)",
            style=discord.InputTextStyle.short,
            required=True,
            value="Yes,No",
        )
        self.add_item(self.outcomes_input)

        # Close time
        self.close_time_input = discord.ui.InputText(
            label="Close Time",
            placeholder="e.g., 1d, 2h, 30m, 1w",
            style=discord.InputTextStyle.short,
            required=True,
            value="1d",
        )
        self.add_item(self.close_time_input)

    async def callback(self, interaction: discord.Interaction):
        """Handle modal submission."""
        await interaction.response.defer(ephemeral=True)
        self.interaction = interaction

        try:
            # Target user is always provided by the slash command option or context menu
            target = self.target_user

            # Validate target is not the creator
            if target.id == interaction.user.id:
                await interaction.followup.send(
                    "You cannot create a market about yourself!", ephemeral=True
                )
                return

            # Parse outcomes
            outcomes = [
                o.strip() for o in self.outcomes_input.value.split(",") if o.strip()
            ]
            if len(outcomes) < 2:
                await interaction.followup.send(
                    "You need at least 2 outcomes!", ephemeral=True
                )
                return

            # Parse close time
            close_time = parse_time_duration(self.close_time_input.value.strip())
            if not close_time:
                await interaction.followup.send(
                    "Invalid time format! Use: 30m, 2h, 1d, 1w", ephemeral=True
                )
                return

            # Get question
            question = self.question_input.value.strip()

            # Store for the cog to handle
            self.result = {
                "creator": interaction.user,
                "target": target,
                "question": question,
                "outcomes": outcomes,
                "close_time": close_time,
            }

            # Let the cog handle the actual creation
            # This will be picked up by the markets cog

        except ValueError as e:
            await interaction.followup.send(f"Error: {str(e)}", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(
                f"Error creating market: {str(e)}", ephemeral=True
            )


class BetAmountModal(discord.ui.Modal):
    """Modal for entering bet amount."""

    def __init__(self, market_id: int, outcome: str, max_amount: float):
        super().__init__(title=f"Buy {outcome}")
        self.market_id = market_id
        self.outcome = outcome
        self.max_amount = max_amount

        self.amount_input = discord.ui.InputText(
            label=f"Amount to spend (max: {max_amount:.2f} Bucks)",
            placeholder="e.g., 10, 50, 100",
            style=discord.InputTextStyle.short,
            required=True,
        )
        self.add_item(self.amount_input)

    async def callback(self, interaction: discord.Interaction):
        """Handle modal submission."""
        try:
            amount = float(self.amount_input.value.strip())

            if amount <= 0:
                await interaction.response.send_message(
                    "Amount must be positive!", ephemeral=True
                )
                return

            if amount > self.max_amount:
                await interaction.response.send_message(
                    f"You only have {self.max_amount:.2f} Bucks!", ephemeral=True
                )
                return

            # Store result for processing
            self.result = {
                "market_id": self.market_id,
                "outcome": self.outcome,
                "amount": amount,
            }

            # Store the interaction so the caller can send followups
            self.interaction = interaction
            await interaction.response.defer(ephemeral=True)

        except ValueError:
            await interaction.response.send_message(
                "Please enter a valid number!", ephemeral=True
            )


class ResolveMarketModal(discord.ui.Modal):
    """Modal for resolving a market."""

    def __init__(self, market_id: int, outcomes: list):
        super().__init__(title="Resolve Market")
        self.market_id = market_id
        self.outcomes = outcomes

        self.outcome_input = discord.ui.InputText(
            label="Winning Outcome",
            placeholder=f"Choose from: {', '.join(outcomes)}",
            style=discord.InputTextStyle.short,
            required=True,
        )
        self.add_item(self.outcome_input)

    async def callback(self, interaction: discord.Interaction):
        """Handle modal submission."""
        winning_outcome = self.outcome_input.value.strip()

        if winning_outcome not in self.outcomes:
            await interaction.response.send_message(
                f"Invalid outcome! Choose from: {', '.join(self.outcomes)}",
                ephemeral=True,
            )
            return

        self.result = {"market_id": self.market_id, "winning_outcome": winning_outcome}

        self.interaction = interaction
        await interaction.response.defer(ephemeral=True)
