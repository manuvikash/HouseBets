<p align="center">
  <img src="logo.png" alt="HouseBets Logo" width="300"/>
</p>

# HouseBets - Discord Prediction Market Bot

A UI-driven Discord bot that creates private prediction markets where friends can bet on each other with mock currency.

## Features

- **UI-First Design**: All interactions use Discord's native components — buttons, dropdowns, and modals
- **Private Markets**: Markets are sent via DM; targets don't see markets about themselves until resolved
- **Mock Currency**: Users start with 1000 Bucks and bet on outcomes
- **AMM Pricing**: Automated Market Maker with dynamic pricing based on liquidity
- **Public Feed**: Resolved markets are announced in a dedicated feed channel with full bet breakdown and updated leaderboard
- **Leaderboards**: Track top performers by total profit

## Commands

### Market Creation
- `/housebets new @target` — Pick a target from the member picker, then fill in the market details
- **Context Menu**: Right-click a user → Apps → "Create Market About"

### Betting
Markets are sent via DM with interactive buttons:
- **Buy [Outcome]** — Click to enter a bet amount
- **View Position** — Check your current holdings

### Resolution
- `/housebets resolve` — Select a market you created, then pick the winning outcome from a dropdown
- **⚖️ Resolve Market button** — Available on the market card in your DM

### Information
- `/housebets balance` — View your balance and total profit
- `/housebets leaderboard` — See top players
- `/housebets my_markets` — View markets you've created

## Setup

### 1. Create a Discord Application

- Go to the [Discord Developer Portal](https://discord.com/developers/applications)
- Create a New Application → go to the **Bot** tab
- Click **Reset Token** and copy your bot token
- Enable all three **Privileged Gateway Intents**:
  - Presence Intent
  - Server Members Intent
  - Message Content Intent

### 2. Invite the Bot to Your Server

Use this URL (replace `YOUR_CLIENT_ID` with your app's ID):
```
https://discord.com/oauth2/authorize?client_id=YOUR_CLIENT_ID&scope=bot+applications.commands&permissions=268528656
```

Required permissions: Send Messages, Embed Links, Read Message History, Manage Channels, Use Application Commands.

### 3. Configure Environment

Create a `.env` file in the project root:
```env
BOT_TOKEN=your_discord_bot_token_here
INITIAL_BALANCE=1000
CURRENCY_NAME=Bucks
FEED_CHANNEL_NAME=housebets-feed
```

### 4. Run with Docker

```bash
# Start the bot (builds automatically on first run)
docker compose up -d

# View live logs
docker compose logs -f

# Stop the bot
docker compose down

# Deploy an update
git pull && docker compose up -d --build
```

The SQLite database is stored in a named Docker volume and persists across restarts and rebuilds.

## Usage Guide

### Creating a Market

**Method 1: Slash Command**
1. Type `/housebets new` and select a target member from the `@`-mention picker
2. Fill in the modal: question, outcomes (comma-separated), close time (`1d`, `2h`, `30m`, `1w`)
3. Submit — eligible server members get a DM with the market card

**Method 2: Context Menu**
1. Right-click a user → Apps → "Create Market About"
2. Fill in the modal (target is pre-filled)

### Placing Bets

1. Open the market card in your DMs
2. Click a **Buy** button for your chosen outcome
3. Enter the amount to spend
4. Prices adjust automatically based on the AMM

### Resolving Markets

1. `/housebets resolve` (or click **⚖️ Resolve Market** in your DM)
2. Select your market from the dropdown
3. Select the winning outcome from the dropdown
4. Payouts are distributed automatically; a full breakdown and updated leaderboard post to the feed channel

## Project Structure

```
housebets/
├── main.py              # Bot entry point
├── config.py            # Configuration
├── requirements.txt     # Dependencies
├── Dockerfile
├── docker-compose.yml
├── .env                 # Environment variables (not committed)
├── reset_db.py          # Database reset utility
├── database/
│   └── db.py            # Database operations
├── cogs/
│   ├── commands.py      # All /housebets slash commands
│   └── betting.py       # Bet placement logic
├── ui/
│   ├── modals.py        # Modal forms
│   ├── embeds.py        # Embed builders
│   └── buttons.py       # Button/view handlers
└── utils/
    ├── pricing.py       # AMM pricing logic
    └── helpers.py       # Utility functions
```

## How It Works

### Market Creation Flow
1. Creator runs `/housebets new @target` and fills in the modal
2. Bot creates the market and DMs all eligible guild members (excluding the target)
3. Creator receives the market card with buy buttons **and** a resolve button

### Betting Flow
1. User clicks a **Buy** button on the market card in their DM
2. Modal opens for the amount to spend
3. Bot calculates shares using AMM pricing and records the bet
4. Market card updates with new prices and balance

### Resolution Flow
1. Creator selects a market and picks the winning outcome via dropdown
2. Bot calculates payouts (1 Buck per winning share)
3. Balances and profit/loss updated for all bettors
4. Resolution embed (with full bet breakdown) + updated leaderboard posted to the feed channel
5. Winners receive a DM notification

### AMM Pricing
Uses a simplified constant-product formula:
- Each outcome has its own liquidity pool
- Price = liquidity[outcome] / total_liquidity
- Buying shares reduces liquidity, increasing the price naturally

## Configuration

| Variable | Default | Description |
|---|---|---|
| `BOT_TOKEN` | — | Your Discord bot token |
| `INITIAL_BALANCE` | `1000` | Starting balance for new users |
| `CURRENCY_NAME` | `Bucks` | Name of the mock currency |
| `FEED_CHANNEL_NAME` | `housebets-feed` | Channel for resolved market announcements |
| `INITIAL_LIQUIDITY` | `100` | AMM liquidity parameter |

## Database Reset

```bash
# Wipe all data, keep schema
python reset_db.py

# Delete the database file entirely and recreate
python reset_db.py --hard
```

## Troubleshooting

**Bot not responding to commands** — Verify the bot token in `.env` and check Docker logs with `docker compose logs -f`.

**DMs not being sent** — Check per-server privacy settings: right-click the server → Privacy Settings → enable Direct Messages. Also ensure the Server Members Intent is enabled in the Developer Portal.

**0 members cached at startup** — Server Members Intent is not enabled in the Developer Portal. See Setup step 1.

**Feed channel not created** — Bot needs the Manage Channels permission. You can also create `#housebets-feed` manually.

## Privacy & Security

- Markets are distributed via DM — other users can't see what markets exist
- Target users are excluded from markets about themselves until resolution
- No real money involved — mock currency only
- All data stored locally in SQLite via a Docker volume

## License

MIT License — feel free to modify and use for your server!
