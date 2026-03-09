# Quick Setup Guide

## 1. Get Your Discord Bot Token

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application"
3. Give it a name (e.g., "HouseBets")
4. Go to "Bot" section in the left sidebar
5. Click "Reset Token" and copy the token
6. **Enable these Privileged Gateway Intents:**
   - ✅ SERVER MEMBERS INTENT
   - ✅ MESSAGE CONTENT INTENT

## 2. Configure Your Bot

```bash
# Copy the example config
cp .env.example .env

# Edit .env and paste your bot token
nano .env  # or use your favorite editor
```

Replace `your_discord_bot_token_here` with your actual token.

## 3. Invite Bot to Your Server

Go to "OAuth2" → "URL Generator" and select:

**Scopes:**
- ✅ bot
- ✅ applications.commands

**Bot Permissions:**
- ✅ Send Messages
- ✅ Embed Links
- ✅ Read Message History
- ✅ Manage Channels
- ✅ Use Application Commands

Copy the generated URL and open it in your browser to invite the bot.

## 4. Install and Run

```bash
# Option 1: Use the quick start script
./start.sh

# Option 2: Manual installation
pip install -r requirements.txt
python main.py
```

## 5. Test the Bot

In your Discord server:

1. Type `/housebets` - you should see the available commands
2. Try `/housebets new` to create your first market
3. Fill in the modal form that appears
4. Check your DMs - you should receive the market card with buttons

## Troubleshooting

### Commands not showing up
- Wait up to 1 hour for slash commands to sync globally
- Try kicking and re-inviting the bot
- Make sure bot has "Use Application Commands" permission

### Can't send DMs
- Make sure "Allow direct messages from server members" is enabled in your Discord privacy settings
- Bot must share a server with you

### Bot crashes on start
- Check your `.env` file has valid token
- Verify Python 3.8+ is installed: `python3 --version`
- Check logs in `housebets.log`

## Next Steps

- Read the full README.md for detailed usage
- Create test markets with friends
- Check the leaderboard with `/housebets leaderboard`
- Resolve markets with `/housebets resolve`

## Need Help?

Check `housebets.log` for detailed error messages.

---

**Happy betting!** 🎲
