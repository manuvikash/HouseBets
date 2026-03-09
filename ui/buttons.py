"""Discord UI buttons and views."""

import discord
from typing import Dict, Optional
from ui.modals import BetAmountModal


class MarketView(discord.ui.View):
    """View with buttons for betting on a market."""

    def __init__(self, market: Dict, user_balance: float):
        super().__init__(timeout=None)  # Persistent view
        self.market = market
        self.user_balance = user_balance

        # Add a button for each outcome
        for outcome in market["outcomes"]:
            button = BuyButton(
                market_id=market["id"], outcome=outcome, user_balance=user_balance
            )
            self.add_item(button)

        # Add position view button
        self.add_item(ViewPositionButton(market["id"]))


class BuyButton(discord.ui.Button):
    """Button to buy shares of an outcome."""

    def __init__(self, market_id: int, outcome: str, user_balance: float):
        super().__init__(
            label=f"Buy {outcome}",
            style=discord.ButtonStyle.primary,
            custom_id=f"buy_{market_id}_{outcome}",
        )
        self.market_id = market_id
        self.outcome = outcome
        self.user_balance = user_balance

    async def callback(self, interaction: discord.Interaction):
        """Handle buy button click."""
        modal = BetAmountModal(self.market_id, self.outcome, self.user_balance)
        await interaction.response.send_modal(modal)
        await modal.wait()

        if hasattr(modal, "result") and hasattr(modal, "interaction"):
            betting_cog = interaction.client.cogs.get("Betting")
            if betting_cog:
                await betting_cog._process_bet(modal.interaction, modal.result)


class ViewPositionButton(discord.ui.Button):
    """Button to view current position in a market."""

    def __init__(self, market_id: int):
        super().__init__(
            label="View Position",
            style=discord.ButtonStyle.secondary,
            custom_id=f"position_{market_id}",
        )
        self.market_id = market_id

    async def callback(self, interaction: discord.Interaction):
        """Handle view position button click."""
        from database import db
        from utils import format_currency

        position = db.get_user_position(str(interaction.user.id), self.market_id)

        if not position:
            await interaction.response.send_message(
                "You don't have any position in this market yet.", ephemeral=True
            )
            return

        position_text = "**Your Position:**\n"
        for outcome, pos in position.items():
            position_text += f"**{outcome}**: {pos['shares']:.2f} shares (cost: {format_currency(pos['cost'])})\n"

        await interaction.response.send_message(position_text, ephemeral=True)


class LeaderboardView(discord.ui.View):
    """View with refresh button for leaderboard."""

    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(RefreshLeaderboardButton())


class RefreshLeaderboardButton(discord.ui.Button):
    """Button to refresh leaderboard."""

    def __init__(self):
        super().__init__(
            label="🔄 Refresh",
            style=discord.ButtonStyle.secondary,
            custom_id="refresh_leaderboard",
        )

    async def callback(self, interaction: discord.Interaction):
        """Handle refresh button click."""
        from database import db
        from ui.embeds import create_leaderboard_embed

        users = db.get_leaderboard()
        embed = create_leaderboard_embed(users, interaction.client)

        await interaction.response.edit_message(embed=embed, view=self.view)


class BalanceView(discord.ui.View):
    """View with refresh button for balance."""

    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(RefreshBalanceButton())


class RefreshBalanceButton(discord.ui.Button):
    """Button to refresh balance."""

    def __init__(self):
        super().__init__(
            label="🔄 Refresh",
            style=discord.ButtonStyle.secondary,
            custom_id="refresh_balance",
        )

    async def callback(self, interaction: discord.Interaction):
        """Handle refresh button click."""
        from database import db
        from ui.embeds import create_balance_embed

        user_data = db.get_or_create_user(str(interaction.user.id))
        embed = create_balance_embed(
            interaction.user, user_data["balance"], user_data["total_profit"]
        )

        await interaction.response.edit_message(embed=embed, view=self.view)


class ResolveButton(discord.ui.Button):
    """Button that lets the market creator trigger resolution from their DM."""

    def __init__(self, market_id: int):
        super().__init__(
            label="⚖️ Resolve Market",
            style=discord.ButtonStyle.danger,
            custom_id=f"resolve_{market_id}",
        )
        self.market_id = market_id

    async def callback(self, interaction: discord.Interaction):
        """Open the resolution modal directly."""
        from database import db

        market = db.get_market(self.market_id)
        if not market:
            await interaction.response.send_message("Market not found!", ephemeral=True)
            return

        if market["creator_id"] != str(interaction.user.id):
            await interaction.response.send_message(
                "Only the market creator can resolve this market!", ephemeral=True
            )
            return

        if market["resolved"]:
            await interaction.response.send_message(
                "This market has already been resolved!", ephemeral=True
            )
            return

        outcome_view = OutcomeSelectionView(market["id"], market["outcomes"])
        await interaction.response.send_message(
            "Select the winning outcome:", view=outcome_view, ephemeral=True
        )
        await outcome_view.wait()
        if outcome_view.selected_outcome:
            commands_cog = interaction.client.cogs.get("HouseCommands")
            if commands_cog:
                result = {
                    "market_id": market["id"],
                    "winning_outcome": outcome_view.selected_outcome,
                }
                await commands_cog._process_resolution(outcome_view.interaction, result)


class CreatorMarketView(discord.ui.View):
    """Market view for the creator: buy buttons + resolve button."""

    def __init__(self, market: Dict, user_balance: float):
        super().__init__(timeout=None)
        self.market = market
        self.user_balance = user_balance

        for outcome in market["outcomes"]:
            self.add_item(BuyButton(market["id"], outcome, user_balance))

        self.add_item(ViewPositionButton(market["id"]))
        self.add_item(ResolveButton(market["id"]))


class OutcomeSelectionView(discord.ui.View):
    """Dropdown for picking the winning outcome when resolving a market."""

    def __init__(self, market_id: int, outcomes: list):
        super().__init__(timeout=60)
        self.market_id = market_id
        self.selected_outcome = None
        self.interaction = None

        options = [
            discord.SelectOption(label=outcome, value=outcome)
            for outcome in outcomes[:25]
        ]
        select = discord.ui.Select(
            placeholder="Choose the winning outcome...",
            options=options,
        )
        select.callback = self._select_callback
        self.add_item(select)

    async def _select_callback(self, interaction: discord.Interaction):
        self.selected_outcome = interaction.data["values"][0]
        self.interaction = interaction
        await interaction.response.defer(ephemeral=True)
        self.stop()


class MarketSelectionView(discord.ui.View):
    """View for selecting a market to resolve."""

    def __init__(self, markets: list):
        super().__init__(timeout=60)

        # Create select menu with markets
        options = []
        for market in markets[:25]:  # Discord limit
            options.append(
                discord.SelectOption(
                    label=f"[{market['id']}] {market['question'][:80]}",
                    value=str(market["id"]),
                    description=f"Closes: {market['close_time']}",
                )
            )

        select = discord.ui.Select(
            placeholder="Choose a market to resolve...", options=options
        )
        select.callback = self.select_callback
        self.add_item(select)

        self.selected_market_id = None

    async def select_callback(self, interaction: discord.Interaction):
        """Handle market selection."""
        self.selected_market_id = int(interaction.data["values"][0])
        self.interaction = interaction  # caller will send_modal on this
        self.stop()
