---
name: dustin-research-trader
displayName: Dustin Research Trader
description: Research-first trading strategy that only trades with clear edge. Based on learnings: No long shots, always verify facts, check resolution criteria, compare prices to market consensus.
metadata: {"clawdbot":{"emoji":"🐕","requires":{"env":["SIMMER_API_KEY"],"pip":["simmer-sdk"]},"cron":null,"autostart":false,"automaton":{"managed":false,"entrypoint":null}}}
authors:
  - Dustin (@darkatek7)
version: "1.0.0"
published: true
---

# 🐕 Dustin Research Trader

Research-first trading strategy based on real trading learnings.

## Strategy Overview

This skill implements Dustin's core trading rules learned from day 1:
1. **NO LONG SHOTS** - Only trade 10-90% probability range
2. **RESEARCH FIRST** - Always verify facts before trading
3. **CHECK CRITERIA** - Resolution must be clearly defined
4. **COMPARE PRICES** - Verify price vs market consensus
5. **MAX 10% POSITION** - Never risk more than 10% of capital

## Setup

```bash
# Install
clawhub install dustin-research-trader

# Run
python dustin_research_trader.py --help

# Sync with Simmer
python dustin_research_trader.py --sync
```

## Configuration

| Setting | Env Variable | Default | Description |
|---------|-------------|---------|-------------|
| Max Position % | `SIMMER_DUSTIN_MAX_POS` | 10 | Max % of capital per trade |
| Min Probability | `SIMMER_DUSTIN_MIN_PROB` | 10 | Min probability (10%) |
| Max Probability | `SIMMER_DUSTIN_MAX_PROB` | 90 | Max probability (90%) |
| Max Active Positions | `SIMMER_DUSTIN_MAX_POSITIONS` | 5 | Max open positions |

## Commands

```bash
# Find research opportunities
python dustin_research_trader.py --scan

# Check portfolio
python dustin_research_trader.py --positions

# Analyze existing positions
python dustin_research_trader.py --analyze

# Run research on specific market
python dustin_research_trader.py --research "market_id"

# Dry run (default)
python dustin_research_trader.py --trade

# Live trading
python dustin_research_trader.py --trade --live
```

## Research Protocol

Before ANY trade, the skill:
1. Fetches market resolution criteria
2. Verifies criteria are CLEAR (not vague)
3. Checks probability is in 10-90% range
4. Compares to market consensus (if available)
5. Requires specific thesis (not just "feels good")

## Hard Rules (Enforced)

- ❌ NO trades under 10% probability (Long Shot Rule!)
- ❌ NO trades with unclear resolution criteria (Research First!)
- ❌ NO trades without specific thesis
- ❌ NO position >10% of capital
- ❌ NO more than 5 active positions
- ✅ ALWAYS verify facts before trading
- ✅ ALWAYS compare price to market consensus

## Daily Learning Log

### 2026-02-26 - Day 1 Learnings:
- ❌ Survivor Ozzy 2%: Lost 530+ $SIM - LONG SHOT = GAMBLING!
- ❌ Claude "go down": Unclear criteria - was a bad trade
- ✅ Research FIRST would have prevented both losses
- ✅ Cut losses early - sold Bingo, Claude partial
- ✅ Price comparison matters (Trump 52% vs 17% real = no edge)

## Example Output

```
🐕 Dustin Research Trader
========================
Scanning for opportunities...

Found: "Will Bitcoin hit $100k in 2026?"
- Probability: 35%
- Volume: $2.5M
- Resolves: 2026-12-31

⚠️ RESEARCH REQUIRED:
- What's the resolution criteria?
- Is "hit" clearly defined?
- Any recent news/fundamentals?

Run: python dustin_research_trader.py --research <market_id>
```

## Troubleshooting

**"Probability out of range"**
- The market probability is outside 10-90%. This is a long shot or too obvious - skip it!

**"Unclear resolution criteria"**
- The market doesn't have clear rules for how it resolves. Don't trade!

**"No edge detected"**
- The current price is fair. No reason to trade.

---

*Built by Dustin 🐕 - Learned the hard way!*
