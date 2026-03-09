# 🎲 HouseBets Quick Reference

## Commands

```
/housebets new          Create new market (opens modal)
/housebets balance      Check your balance
/housebets leaderboard  View top players
/housebets my_markets   See your created markets
/housebets resolve      Resolve a market
```

## Context Menu
```
Right-click user → Apps → "Create Market About"
```

## Market Creation Modal Fields
```
Target User:    Who the market is about (username or ID)
Question:       The prediction question
Outcomes:       Comma-separated (e.g., "Yes,No" or "Pizza,Sushi,Pasta")
Close Time:     When betting closes (e.g., "1d", "2h", "30m", "1w")
```

## Time Format
```
30m  = 30 minutes
2h   = 2 hours
1d   = 1 day
1w   = 1 week
```

## Betting in DMs
```
1. Market card appears with buttons
2. Click "Buy [Outcome]"
3. Enter amount to spend
4. Confirm
```

## Price Display
```
Yes: 65%  = 65 Bucks to win 100 Bucks if Yes wins
No: 35%   = 35 Bucks to win 100 Bucks if No wins
```

## Resolution
```
1. /housebets resolve
2. Select market from dropdown
3. Enter winning outcome
4. Payouts distributed automatically
```

## Payouts
```
Winning shares: 1 Buck per share
Losing shares: 0 Bucks
```

## Example Bet
```
Spent: 50 Bucks on Yes (at 50% price)
Got: 100 shares
If Yes wins: 100 Bucks (profit: +50)
If No wins: 0 Bucks (loss: -50)
```

## Privacy Rules
```
✅ Markets sent via DM (private)
✅ Target can't see until resolved
✅ Feed shows only resolved markets
❌ No identifying info before resolution
```

## Starting Balance
```
Every user starts with: 1000 Bucks
```

## Leaderboard Ranking
```
Ranked by: Total Profit (not balance)
Profit = Winnings - Costs
```

## Setup (First Time)
```bash
1. cp .env.example .env
2. # Add your BOT_TOKEN to .env
3. python3 validate.py
4. ./start.sh
```

## File Locations
```
Database:     housebets.db
Logs:         housebets.log
Config:       .env
```

## Troubleshooting
```
Commands not showing?
→ Wait 1 hour for sync or re-invite bot

Can't send DMs?
→ Enable "Allow DMs from server members"

Bot not starting?
→ Check housebets.log for errors

Database issues?
→ Delete housebets.db to reset
```

## Support Files
```
README.md          Full documentation
SETUP.md           Setup instructions
FLOWS.md           User flow diagrams
EXAMPLES.md        Usage examples
IMPLEMENTATION.md  Technical details
```

## Discord Permissions Required
```
✅ Send Messages
✅ Embed Links
✅ Read Message History
✅ Manage Channels (for feed)
✅ Use Application Commands
```

## Gateway Intents Required
```
✅ SERVER MEMBERS INTENT
✅ MESSAGE CONTENT INTENT
```

## Bot Invite URL Template
```
https://discord.com/api/oauth2/authorize?
  client_id=YOUR_CLIENT_ID
  &permissions=268528656
  &scope=bot%20applications.commands
```

---

**Quick Links:**
- [Discord Developer Portal](https://discord.com/developers/applications)
- [py-cord Docs](https://docs.pycord.dev/)
- [GitHub Issues](https://github.com/yourusername/housebets/issues)

**Need help?** Check housebets.log or run: `python3 validate.py`
