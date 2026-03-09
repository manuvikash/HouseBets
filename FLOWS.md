# HouseBets User Flows

## 📊 Market Creation Flow

```
User Action                    Bot Response                      Result
──────────────────────────────────────────────────────────────────────────
/housebets new          →     Opens Modal Form            →     User fills in:
                                                                 - Target user
                                                                 - Question
                                                                 - Outcomes
                                                                 - Close time
                              ↓
User submits form       →     Bot validates inputs        →     Creates market in DB
                              ↓
                              Sends DMs to all            →     Each eligible user
                              eligible members                  receives:
                              (except target & creator)         - Market embed
                                                                - Buy buttons
                              ↓
                              Confirms to creator         →     "Market created! ID: X"
```

## 🎲 Betting Flow

```
User sees DM           →      Market card with           →     Shows:
                              interactive buttons               - Question
                                                               - Current prices
                                                               - Your balance
                              ↓
Click "Buy Yes"        →      Opens Amount Modal         →     User enters amount
                              ↓
User submits          →       Bot calculates:            →     - Shares to buy
                              - Shares                         - Updated price
                              - New price                      - New balance
                              - Liquidity update
                              ↓
                              Updates:                   →     - Deducts from balance
                              - User balance                   - Records bet
                              - Market liquidity              - Updates embed
                              ↓
                              Confirmation message       →     "Bet placed! Bought
                                                               X shares for Y Bucks"
```

## ✅ Resolution Flow

```
Creator Action                Bot Response                      Result
──────────────────────────────────────────────────────────────────────────
/housebets resolve     →      Shows dropdown menu        →     Lists unresolved
                              with creator's markets           markets
                              ↓
Selects market        →       Opens Modal                →     "Select winning outcome"
                              ↓
Submits winner        →       Bot processes:             →     - Calculates payouts
                              - Gets all bets                  - Updates balances
                              - Calculates payouts             - Updates profits
                              ↓
                              Distributes payouts        →     Each winner receives:
                              & updates stats                  - 1 Buck per share
                                                              - Profit tracked
                              ↓
                              Posts to feed channel      →     Public announcement:
                                                              - Question
                                                              - Winner
                                                              - Top payouts
                              ↓
                              Sends DM to winners       →     "You won X Bucks!"
```

## 🏆 Balance & Leaderboard Flow

```
/housebets balance     →      Shows embed with:          →     - Current balance
                              - Balance                       - Total profit/loss
                              - Profit                        - Refresh button
                              - Refresh button

/housebets leaderboard →      Shows embed with:          →     - Top 10 users
                              - Rankings                      - By total profit
                              - Refresh button                - Refresh button
```

## 📋 Context Menu Flow

```
Right-click user      →       Context menu appears       →     "Apps" → 
                                                              "Create Market About"
                              ↓
Click option          →       Opens Modal Form           →     Target pre-filled
                              (same as /housebets new)
                              ↓
                              [Same as Market Creation Flow]
```

## 🔄 Real-Time Updates

### Price Updates (AMM)
```
Initial State:         After 100 Buck bet on "Yes":       After another 100 Buck bet:
Yes: 50%              Yes: 60% (+10%)                    Yes: 68% (+8%)
No: 50%               No: 40% (-10%)                     No: 32% (-8%)

Prices increase as more people buy that outcome.
```

### Balance Tracking
```
User starts with:     1000 Bucks
                      ↓
Places bet:          -100 Bucks (bought 150 shares of Yes at ~0.66/share)
                      ↓
Current balance:      900 Bucks
                      ↓
Market resolves:     +150 Bucks (Yes won, 150 shares × 1 Buck)
                      ↓
Final balance:        1050 Bucks
Total profit:        +50 Bucks
```

## 🎯 Privacy Model

```
Market Created About:    Alice
Sent to:                Bob, Carol, Dave (everyone except Alice & creator)
Alice sees:             Nothing (until resolved)

After Resolution:
Feed Channel Posts:     Question (public-safe)
                       Winner
                       Payouts
Alice sees:            Full resolution in feed
```

## 💡 Tips for Users

1. **Early bets = better prices**: First betters get better odds
2. **Diversify**: Bet on multiple outcomes if you're uncertain
3. **Watch liquidity**: Large bets move prices significantly
4. **Track profit**: Total profit matters more than balance for leaderboard
5. **Time markets well**: Set close times that give people time to bet

---

This bot uses Discord's modern interaction framework for a smooth, UI-driven experience!
