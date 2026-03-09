# HouseBets - Usage Examples

## Example 1: Simple Yes/No Market

**Scenario**: Will Bob clean his room this week?

### Creating the Market
1. Run: `/housebets new`
2. Fill in modal:
   - **Target**: @Bob
   - **Question**: Will Bob clean his room this week?
   - **Outcomes**: Yes,No
   - **Close Time**: 1w

### Betting
Alice receives DM with buttons:
- Clicks "Buy Yes"
- Enters: 50 Bucks
- Gets ~75 shares at current price of ~0.67 Bucks/share

Bob doesn't see this market (he's the target).

### Resolution
After 1 week:
1. Creator runs: `/housebets resolve`
2. Selects "Will Bob clean his room"
3. Enters: "Yes" (or "No")
4. Payouts distributed automatically

**If Yes wins:**
- Alice gets 75 Bucks (75 shares × 1 Buck)
- Her profit: 75 - 50 = +25 Bucks

---

## Example 2: Multi-Outcome Market

**Scenario**: What will Carol eat for dinner tonight?

### Creating
```
Target: @Carol
Question: What will Carol eat for dinner tonight?
Outcomes: Pizza,Sushi,Pasta,Cooking
Close Time: 8h
```

### Betting Strategy
Dave hedges his bets:
- 20 Bucks on Pizza (thinks it's most likely)
- 10 Bucks on Sushi (as backup)
- 5 Bucks on Pasta (long shot)

Price evolution:
```
Initial:  Pizza 25%, Sushi 25%, Pasta 25%, Cooking 25%
          ↓
After Dave's bets:
          Pizza 35%, Sushi 28%, Pasta 22%, Cooking 15%
          ↓
After more bets:
          Pizza 45%, Sushi 30%, Pasta 15%, Cooking 10%
```

### Resolution
Carol ate Pizza!
- Dave gets: ~30 shares × 1 Buck = 30 Bucks
- Spent: 35 Bucks total
- Loss: -5 Bucks (but less than if he only bet Pizza!)

---

## Example 3: Context Menu Quick Create

**Scenario**: Spontaneous bet about Alice

### Quick Creation
1. Right-click @Alice's name
2. Apps → "Create Market About"
3. Fill modal (target pre-filled):
   - **Question**: Will Alice arrive on time to dinner?
   - **Outcomes**: Yes,No
   - **Close Time**: 3h

Market sent to everyone except Alice instantly!

---

## Example 4: Position Management

**Scenario**: Bob wants to track his bets

### Checking Position
While in a DM with an active market:
1. Click "View Position" button
2. Sees:
   ```
   Your Position:
   Yes: 75.50 shares (cost: 45.00 Bucks)
   No: 25.30 shares (cost: 20.00 Bucks)
   ```

### Understanding Position
- Total spent: 65 Bucks
- If Yes wins: Gets 75.50 Bucks (profit: +10.50)
- If No wins: Gets 25.30 Bucks (loss: -39.70)
- Bob is betting on Yes winning

---

## Example 5: Leaderboard Competition

**Current Standings**
```
/housebets leaderboard

🏆 HouseBets Leaderboard

1. 🥇 @Alice: +150.00 Bucks
2. 🥈 @Dave: +75.50 Bucks
3. 🥉 @Carol: +25.00 Bucks
4. 4. @Bob: -10.00 Bucks
5. 5. @Eve: -50.00 Bucks
```

**How Profit is Calculated**
- Alice: Won 4 markets, lost 1
  - Total winnings: 250 Bucks
  - Total spent: 100 Bucks
  - Profit: +150 Bucks

- Bob: Won 1 market, lost 2
  - Total winnings: 50 Bucks
  - Total spent: 60 Bucks
  - Profit: -10 Bucks

---

## Example 6: Price Movement (AMM in Action)

**Market**: Will Dave go to the gym tomorrow?
**Initial liquidity**: 100 Bucks per outcome

### Price Evolution
```
Time    Action                  Yes Price   No Price
────────────────────────────────────────────────────
0:00    Market created          50%         50%
0:15    Alice bets 50 on Yes    58%         42%
0:30    Bob bets 100 on Yes     68%         32%
1:00    Carol bets 30 on No     65%         35%
2:00    Dave (target) can't see market yet...
```

**Why prices moved:**
- Each Yes bet reduces Yes liquidity → increases Yes price
- No bets increase as Yes becomes more "expensive"
- Later bets get worse prices (slippage)

---

## Example 7: Resolution and Payouts

**Market**: Will Eve finish her project by Friday?
**Total volume**: 300 Bucks bet

### Final Positions
```
User    Outcome   Shares   Cost
────────────────────────────────
Alice   Yes       50       40
Bob     Yes       30       30
Carol   No        75       60
Dave    Yes       100      85
Eve     (target, no bets)
```

### Resolution: Yes wins!
```
Payouts:
────────────────────────────────
Alice:  50 × 1 = 50 Bucks  (+10 profit)
Bob:    30 × 1 = 30 Bucks  (±0 profit)
Carol:  0           (lost)  (-60 profit)
Dave:   100 × 1 = 100      (+15 profit)
```

### Feed Post
```
✅ Market Resolved
Will Eve finish her project by Friday?

🎯 Winning Outcome: Yes
💵 Total Volume: 215.00 Bucks
👥 Total Payouts: 180.00 Bucks

🏆 Top Winners:
@Dave: +15.00 Bucks
@Alice: +10.00 Bucks
@Bob: ±0.00 Bucks
```

---

## Example 8: Hedging Strategy

**Scenario**: Alice is uncertain about an outcome

### The Bet
Market: Will Bob watch the game tonight?

Alice's strategy:
```
Bet 60 on Yes  → Gets ~75 shares at 0.80 price
Bet 40 on No   → Gets ~180 shares at 0.22 price
Total: 100 Bucks spent
```

### Outcomes
**If Yes wins:**
- Gets: 75 Bucks
- Loss: -25 Bucks

**If No wins:**
- Gets: 180 Bucks
- Profit: +80 Bucks

Alice is taking a calculated risk betting more happens on "No" despite Yes being favored!

---

## Example 9: My Markets Management

**Carol checks her created markets:**
```
/housebets my_markets

📋 Your Markets

[42] Will Bob clean his room this week?
🔴 Active | Closes: 2026-03-15 18:00

[41] What will Dave eat for dinner tonight?
✅ Resolved | Winner: Pizza

[40] Will Alice arrive on time to dinner?
✅ Resolved | Winner: Yes
```

Carol can now resolve market #42 when it closes.

---

## Example 10: Balance Tracking

**Bob checks his stats:**
```
/housebets balance

💰 Your Balance

Current Balance: 1,125.50 Bucks
Total Profit/Loss: +125.50 Bucks

[🔄 Refresh]
```

**Bob's history:**
- Started with: 1,000 Bucks
- Won from markets: 250 Bucks
- Spent on bets: 124.50 Bucks
- Current balance: 1,125.50 Bucks
- Net profit: +125.50 Bucks

---

## Pro Tips

### Betting Strategy
1. **Early bird advantage**: First bets get best prices
2. **Hedge uncertain bets**: Spread risk across outcomes
3. **Watch the crowd**: High prices mean consensus
4. **Contrarian plays**: Bet against consensus for high upside

### Market Creation
1. **Clear questions**: Make resolution criteria obvious
2. **Reasonable timeframes**: Give people time to bet
3. **Fun targets**: Pick people everyone knows
4. **Multi-outcome**: More outcomes = more interesting

### Resolution
1. **Be fair**: Resolve based on facts
2. **Timely**: Don't leave markets hanging
3. **Communicate**: Explain controversial resolutions

### Privacy
1. **Target never sees**: Markets hidden until resolved
2. **Public feed**: Resolution shows winner but not all details
3. **DM notifications**: Winners get private payout notification

---

**Ready to start betting? Run `/housebets new` and create your first market!** 🎲
