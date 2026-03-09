# HouseBets - Discord Prediction Market Bot

A UI-driven Discord bot that creates private prediction markets where roommates can bet on each other with mock currency.

## Features

- **UI-First Design**: Almost all interactions use Discord's interactive components (buttons, modals, dropdowns)
- **Private Markets**: Markets are sent via DM, targets don't see markets about themselves until resolved
- **Mock Currency**: Users start with 1000 Bucks and can bet on market outcomes
- **AMM Pricing**: Automated Market Maker with dynamic pricing based on liquidity
- **Public Feed**: Resolved markets are announced in a dedicated feed channel
- **Leaderboards**: Track top performers by total profit

## Commands

### Market Creation
- `/housebets new` - Opens a modal form to create a new prediction market
- **Context Menu**: Right-click a user → Apps → "Create Market About" - Quick market creation

### Betting
Markets are sent via DM with interactive buttons:
- **Buy Yes/No** - Click to open betting modal
- **View Position** - Check your current holdings

### Information
- `/housebets balance` - View your balance and total profit
- `/housebets leaderboard` - See top players
- `/housebets my_markets` - View markets you've created

### Resolution
- `/housebets resolve` - Resolve a market you created (shows selection UI)

## Setup

### Prerequisites
- Python 3.8+
- Discord Bot Token
- Discord Bot Permissions:
  - Send Messages
  - Embed Links
  - Read Message History
  - Manage Channels (for auto-creating feed channel)
  - Use Application Commands

### Installation

1. **Clone the repository**
```bash
cd housebets
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure the bot**

Edit `.env` file:
```env
BOT_TOKEN=your_discord_bot_token_here
INITIAL_BALANCE=1000
CURRENCY_NAME=Bucks
FEED_CHANNEL_NAME=housebets-feed
```

4. **Create Discord Application**

- Go to [Discord Developer Portal](https://discord.com/developers/applications)
- Create New Application
- Go to "Bot" section
- Click "Reset Token" and copy your bot token
- Enable these Privileged Gateway Intents:
  - SERVER MEMBERS INTENT
  - MESSAGE CONTENT INTENT

5. **Invite Bot to Server**

Generate invite URL with these scopes:
- `bot`
- `applications.commands`

And these permissions:
- Send Messages
- Embed Links
- Read Message History
- Manage Channels
- Use Application Commands

Example URL:
```
https://discord.com/api/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=268528656&scope=bot%20applications.commands
```

6. **Run the bot**
```bash
python main.py
```

## Usage Guide

### Creating a Market

**Method 1: Slash Command**
1. Type `/housebets new`
2. Fill in the modal form:
   - Target user (username or ID)
   - Market question
   - Outcomes (comma-separated, default: "Yes,No")
   - Close time (e.g., "1d", "2h", "30m", "1w")
3. Submit

**Method 2: Context Menu**
1. Right-click on a user
2. Apps → "Create Market About"
3. Fill in the modal (target is pre-filled)
4. Submit

### Placing Bets

1. Check your DMs for market notifications
2. Click a "Buy" button for your preferred outcome
3. Enter amount to spend in the modal
4. Confirm

Your balance updates automatically and prices adjust based on AMM.

### Resolving Markets

1. Type `/housebets resolve`
2. Select your market from the dropdown
3. Enter the winning outcome
4. Payouts are distributed automatically
5. Result is posted to the feed channel

### Checking Stats

- **Balance**: `/housebets balance`
- **Leaderboard**: `/housebets leaderboard`
- **Your Markets**: `/housebets my_markets`

## Project Structure

```
housebets/
├── main.py              # Bot entry point
├── config.py            # Configuration
├── requirements.txt     # Dependencies
├── .env                 # Environment variables
├── housebets.db        # SQLite database (auto-created)
├── database/
│   ├── __init__.py
│   └── db.py           # Database operations
├── cogs/
│   ├── __init__.py
│   ├── markets.py      # Market creation/management
│   ├── betting.py      # Betting interactions
│   ├── leaderboard.py  # Balance/leaderboard commands
│   └── resolution.py   # Market resolution
├── ui/
│   ├── __init__.py
│   ├── modals.py       # Modal forms
│   ├── embeds.py       # Embed builders
│   └── buttons.py      # Button/view handlers
└── utils/
    ├── __init__.py
    ├── pricing.py      # AMM pricing logic
    └── helpers.py      # Utility functions
```

## How It Works

### Market Creation Flow
1. User opens modal via slash command or context menu
2. Bot validates inputs and creates market in database
3. Bot sends market card with buttons to all eligible users via DM
4. Target user is excluded from seeing the market

### Betting Flow
1. User clicks "Buy" button on market card in DM
2. Modal opens asking for amount to spend
3. Bot calculates shares using AMM pricing
4. Bet is recorded, balance updated, liquidity adjusted
5. Market card updates with new prices

### Resolution Flow
1. Creator selects market to resolve
2. Bot calculates payouts (1 Buck per winning share)
3. Balances updated for all winners
4. Profit/loss tracked for leaderboard
5. Resolution posted to public feed channel

### AMM Pricing
Uses a simplified constant product formula:
- Each outcome has liquidity pool
- Price = liquidity[outcome] / total_liquidity
- Buying shares reduces liquidity (increases price)
- Creates natural price discovery mechanism

## Configuration Options

Edit `config.py` or `.env` to customize:

- `INITIAL_BALANCE` - Starting balance for new users (default: 1000)
- `CURRENCY_NAME` - Name of mock currency (default: "Bucks")
- `FEED_CHANNEL_NAME` - Channel for resolved markets (default: "housebets-feed")
- `INITIAL_LIQUIDITY` - AMM liquidity parameter (default: 100)

## Troubleshooting

### Bot not responding to commands
- Ensure bot has proper permissions
- Check if slash commands are synced (may take 1 hour for global commands)
- Verify bot token is correct in `.env`

### Can't send DMs
- Users must allow DMs from server members
- Bot must share a server with the user

### Feed channel not created
- Bot needs "Manage Channels" permission
- Manually create `#housebets-feed` channel as fallback

### Database errors
- Delete `housebets.db` to reset (WARNING: deletes all data)
- Check file permissions

## Development

### Adding New Features
1. Create new cog in `cogs/` directory
2. Add UI components in `ui/` if needed
3. Load cog in `main.py`

### Testing
- Test in a private Discord server first
- Use `/housebets new` to create test markets
- Verify DMs are being sent
- Test resolution and payouts

## Privacy & Security

- Markets are sent via DM (private)
- Target users don't see markets about themselves until resolved
- No real money involved (mock currency only)
- All data stored locally in SQLite

## License

MIT License - feel free to modify and use for your server!

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review Discord bot permissions
3. Check logs in `housebets.log`

## Credits

Built with:
- [py-cord](https://github.com/Pycord-Development/pycord) - Discord API wrapper
- [python-dotenv](https://github.com/theskumar/python-dotenv) - Environment configuration
- SQLite - Database

---

Made for roommates who like to bet on each other 🎲
