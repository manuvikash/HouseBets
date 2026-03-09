# 📋 HouseBets Deployment Checklist

Use this checklist to ensure proper setup and deployment of your HouseBets bot.

## Pre-Deployment Setup

### 1. Discord Application Setup
- [ ] Go to [Discord Developer Portal](https://discord.com/developers/applications)
- [ ] Create new application
- [ ] Note down Application ID (Client ID)
- [ ] Go to "Bot" section
- [ ] Reset token and copy it (keep it secret!)
- [ ] Enable Privileged Gateway Intents:
  - [ ] SERVER MEMBERS INTENT
  - [ ] MESSAGE CONTENT INTENT
- [ ] Save changes

### 2. Bot Permissions
Required permissions checklist:
- [ ] Send Messages
- [ ] Embed Links
- [ ] Read Message History
- [ ] Manage Channels
- [ ] Use Application Commands

Permission integer: `268528656`

### 3. Local Setup
- [ ] Python 3.8+ installed (`python3 --version`)
- [ ] Git repository cloned/initialized
- [ ] Navigate to project directory

### 4. Configuration
- [ ] Copy example config: `cp .env.example .env`
- [ ] Edit `.env` file
- [ ] Paste bot token into `BOT_TOKEN=`
- [ ] Optionally customize:
  - [ ] `INITIAL_BALANCE` (default: 1000)
  - [ ] `CURRENCY_NAME` (default: Bucks)
  - [ ] `FEED_CHANNEL_NAME` (default: housebets-feed)

### 5. Dependencies
- [ ] Run: `pip install -r requirements.txt`
- [ ] Verify py-cord installed: `python3 -c "import discord; print(discord.__version__)"`
- [ ] Verify python-dotenv installed: `python3 -c "import dotenv"`

### 6. Validation
- [ ] Run: `python3 validate.py`
- [ ] All checks should pass ✅
- [ ] Fix any ❌ issues reported

## Bot Invitation

### 7. Generate Invite URL
```
https://discord.com/api/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=268528656&scope=bot%20applications.commands
```

Replace `YOUR_CLIENT_ID` with your Application ID from step 1.

### 8. Invite to Server
- [ ] Open invite URL in browser
- [ ] Select your Discord server
- [ ] Authorize the bot
- [ ] Verify bot appears in member list
- [ ] Bot should have online status (green)

## First Run

### 9. Start Bot
- [ ] Run: `./start.sh` or `python3 main.py`
- [ ] Check console output for:
  - [ ] "Logged in as [BotName]"
  - [ ] "Connected to X guild(s)"
  - [ ] "Bot is ready!"
- [ ] Check for any error messages
- [ ] Verify `housebets.db` file created
- [ ] Check `housebets.log` for startup logs

### 10. Command Registration
- [ ] Wait up to 1 hour for slash commands to sync (first time only)
- [ ] Or kick and re-invite bot for instant sync
- [ ] Type `/` in Discord and look for `/housebets` commands

## Testing

### 11. Basic Commands
- [ ] Type `/housebets` - autocomplete should show subcommands
- [ ] Test `/housebets balance` - should show 1000 Bucks
- [ ] Test `/housebets leaderboard` - should show empty or initial state
- [ ] Commands respond within 3 seconds

### 12. Market Creation
- [ ] Run `/housebets new`
- [ ] Modal form appears
- [ ] Fill in all fields:
  - [ ] Target: Another user (not yourself)
  - [ ] Question: Test question
  - [ ] Outcomes: Yes,No
  - [ ] Close Time: 1d
- [ ] Submit form
- [ ] Receive confirmation message
- [ ] Check DMs - should have market card

### 13. Betting
- [ ] Open DM from bot
- [ ] Market card displays with:
  - [ ] Question
  - [ ] Outcomes with prices
  - [ ] Balance
  - [ ] Buy buttons
- [ ] Click "Buy Yes" button
- [ ] Modal appears for amount
- [ ] Enter amount (e.g., 100)
- [ ] Submit
- [ ] Receive confirmation
- [ ] Balance updates
- [ ] Prices update

### 14. Context Menu
- [ ] Right-click a user
- [ ] Apps → "Create Market About" appears
- [ ] Modal opens with target pre-filled
- [ ] Test creating market this way

### 15. Position Tracking
- [ ] Click "View Position" in market DM
- [ ] Should show your shares and cost
- [ ] Numbers should match your bet

### 16. Market Resolution
- [ ] Run `/housebets resolve`
- [ ] Dropdown shows your unresolved markets
- [ ] Select a market
- [ ] Modal asks for winning outcome
- [ ] Enter winner (e.g., "Yes")
- [ ] Receive confirmation
- [ ] Check #housebets-feed channel
  - [ ] Channel auto-created (if didn't exist)
  - [ ] Resolution post appears
  - [ ] Shows winner and payouts
- [ ] Winners receive DM notifications
- [ ] Balances updated

### 17. Leaderboard
- [ ] Run `/housebets leaderboard`
- [ ] Should show rankings by profit
- [ ] Click refresh button - updates
- [ ] Verify profits calculated correctly

### 18. My Markets
- [ ] Run `/housebets my_markets`
- [ ] Shows list of markets you created
- [ ] Active markets marked 🔴
- [ ] Resolved markets marked ✅

## Production Readiness

### 19. Error Handling
- [ ] Try invalid inputs in forms
- [ ] Verify helpful error messages
- [ ] Check `housebets.log` for error details
- [ ] Bot doesn't crash on errors

### 20. Privacy Verification
- [ ] Create market about User A
- [ ] Verify User A doesn't receive DM
- [ ] Only after resolution, User A sees in feed
- [ ] Target exclusion working correctly

### 21. Performance
- [ ] Bot responds to commands < 3 seconds
- [ ] DMs sent promptly
- [ ] Database queries fast
- [ ] No lag in UI interactions

### 22. Data Persistence
- [ ] Stop bot: `Ctrl+C`
- [ ] Restart bot: `./start.sh`
- [ ] Balances preserved
- [ ] Markets still accessible
- [ ] Positions unchanged
- [ ] `housebets.db` file intact

## Monitoring

### 23. Logs
- [ ] Check `housebets.log` regularly
- [ ] Look for WARNING or ERROR entries
- [ ] Monitor for repeated failures
- [ ] Set up log rotation if needed

### 24. Database
- [ ] Backup `housebets.db` regularly
- [ ] Test restore from backup
- [ ] Monitor database size growth
- [ ] Consider PostgreSQL for production scale

### 25. Bot Status
- [ ] Bot maintains online status
- [ ] Responds to all commands
- [ ] No random disconnects
- [ ] Stable for 24+ hours

## Troubleshooting Common Issues

### Commands Not Showing
- [ ] Wait 1 hour for global sync
- [ ] Kick and re-invite bot
- [ ] Verify permissions in server settings
- [ ] Check bot has "Use Application Commands" permission

### DMs Not Received
- [ ] User has "Allow DMs from server members" enabled
- [ ] Bot shares server with user
- [ ] User hasn't blocked bot
- [ ] Check bot logs for Forbidden errors

### Database Errors
- [ ] Check file permissions on `housebets.db`
- [ ] Verify disk space available
- [ ] Try deleting and recreating (loses data!)
- [ ] Check `housebets.log` for details

### Bot Crashes
- [ ] Check `housebets.log` for stack trace
- [ ] Verify all dependencies installed
- [ ] Check Python version compatibility
- [ ] Run `python3 validate.py` again

## Optional Enhancements

### 26. Production Deployment
- [ ] Deploy to cloud platform (Railway, Heroku, AWS)
- [ ] Set up process manager (systemd, pm2)
- [ ] Configure auto-restart on crash
- [ ] Set up monitoring alerts

### 27. Database Upgrade
- [ ] Migrate to PostgreSQL for scale
- [ ] Update `config.py` with database URL
- [ ] Test migration with backup data
- [ ] Monitor query performance

### 28. Advanced Features
- [ ] Add scheduled market closing
- [ ] Implement market categories
- [ ] Add betting history command
- [ ] Create admin dashboard
- [ ] Set up analytics tracking

## Security

### 29. Token Safety
- [ ] Never commit `.env` to git
- [ ] Keep bot token secret
- [ ] Rotate token if exposed
- [ ] Use environment variables in production

### 30. Permissions
- [ ] Bot has minimum required permissions only
- [ ] No unnecessary admin permissions
- [ ] Review role hierarchy in server
- [ ] Test with restricted permissions

## Documentation

### 31. User Guide
- [ ] Share README.md with users
- [ ] Post QUICKREF.md in Discord channel
- [ ] Create #housebets-help channel
- [ ] Document any custom rules

### 32. Admin Guide
- [ ] Document backup procedures
- [ ] List troubleshooting steps
- [ ] Share logs location
- [ ] Document configuration options

## Final Verification

### 33. Full Integration Test
- [ ] Create 3+ markets with different outcomes
- [ ] Have 3+ users place bets
- [ ] Resolve markets with different winners
- [ ] Verify all payouts correct
- [ ] Check leaderboard accurate
- [ ] Feed posts all correct

### 34. Load Test (Optional)
- [ ] Create 10+ simultaneous markets
- [ ] Process 50+ bets
- [ ] Resolve all markets
- [ ] Monitor performance
- [ ] Check database integrity

### 35. Go Live!
- [ ] All above checks passed ✅
- [ ] Bot stable for 24+ hours
- [ ] Users understand how to use it
- [ ] Documentation accessible
- [ ] Monitoring in place
- [ ] Backup strategy working

---

## ✅ Deployment Complete!

Once all items are checked, your HouseBets bot is production-ready!

**Need support?**
- Check `housebets.log`
- Run `python3 validate.py`
- Review SETUP.md
- Check EXAMPLES.md for usage

**Enjoy your prediction market!** 🎲
