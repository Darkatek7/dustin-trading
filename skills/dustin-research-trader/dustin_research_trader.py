#!/usr/bin/env python3
"""
Dustin Research Trader - Research-first trading strategy
Based on learnings from Day 1: No long shots, research first, check criteria!
"""

import os
import sys
import json
import argparse
from dataclasses import dataclass, asdict
from typing import Optional, List

# Reconfigure stdout for cron visibility
sys.stdout.reconfigure(line_buffering=True)

try:
    from simmer_sdk import SimmerClient
except ImportError:
    print("ERROR: simmer-sdk not installed. Run: pip install simmer-sdk")
    sys.exit(1)


# === CONFIGURATION ===
CONFIG_SCHEMA = {
    "max_position_pct": {
        "env": "SIMMER_DUSTIN_MAX_POS",
        "default": 10,
        "type": int,
        "description": "Max % of capital per trade"
    },
    "min_probability": {
        "env": "SIMMER_DUSTIN_MIN_PROB",
        "default": 10,
        "type": int,
        "description": "Min probability (10%)"
    },
    "max_probability": {
        "env": "SIMMER_DUSTIN_MAX_PROB",
        "default": 90,
        "type": int,
        "description": "Max probability (90%)"
    },
    "max_active_positions": {
        "env": "SIMMER_DUSTIN_MAX_POSITIONS",
        "default": 5,
        "type": int,
        "description": "Max open positions"
    }
}


@dataclass
class Market:
    market_id: str
    question: str
    probability: float
    volume: float
    resolves_at: str
    url: str


@dataclass
class Position:
    market_id: str
    question: str
    side: str
    shares: float
    cost_basis: float
    current_value: float
    pnl: float
    avg_cost: float
    current_price: float


def get_client() -> SimmerClient:
    """Get Simmer client with API key from env."""
    api_key = os.environ.get("SIMMER_API_KEY")
    if not api_key:
        print("ERROR: SIMMER_API_KEY not set")
        sys.exit(1)
    return SimmerClient(api_key=api_key)


def load_config() -> dict:
    """Load configuration from environment."""
    config = {}
    for key, spec in CONFIG_SCHEMA.items():
        env_var = spec["env"]
        default = spec["default"]
        config[key] = int(os.environ.get(env_var, default))
    return config


def check_position_limits(client: SimmerClient, config: dict) -> tuple:
    """Check if we can take new positions."""
    positions = client.get_positions()
    active_count = len([p for p in positions if p.status == "active"])
    
    max_positions = config["max_active_positions"]
    if active_count >= max_positions:
        return False, f"At max positions ({max_count}/{max_positions})"
    
    return True, "OK"


def check_probability_range(probability: float, config: dict) -> tuple:
    """Check if probability is in acceptable range (10-90%)."""
    min_prob = config["min_probability"]
    max_prob = config["max_probability"]
    
    if probability < min_prob:
        return False, f"Long shot! {probability}% < {min_prob}% - SKIP"
    if probability > max_prob:
        return False, f"Too obvious! {probability}% > {max_prob}% - SKIP"
    
    return True, "OK"


def analyze_position(position: Position, config: dict) -> str:
    """Analyze a position for research opportunities."""
    prob = position.current_price * 100
    
    # Check probability range
    in_range, msg = check_probability_range(prob, config)
    if not in_range:
        return f"⚠️ {position.question[:50]}: {msg}"
    
    # Check P&L - big losses might be opportunities
    pnl_pct = (position.pnl / position.cost_basis * 100) if position.cost_basis > 0 else 0
    
    if pnl_pct < -20:
        return f"🔴 {position.question[:50]}: {pnl_pct:.1f}% loss - RECONSIDER"
    elif pnl_pct < -10:
        return f"🟡 {position.question[:50]}: {pnl_pct:.1f}% loss"
    
    return f"✅ {position.question[:50]}: OK"


def scan_markets(client: SimmerClient, config: dict, keywords: List[str] = None):
    """Scan for research opportunities."""
    print("\n🐕 Dustin Research Trader - Scanning...")
    print("=" * 50)
    
    # Get active markets
    try:
        markets = client.get_markets(status="active", limit=50)
    except Exception as e:
        print(f"Error fetching markets: {e}")
        return
    
    opportunities = []
    
    for market in markets:
        prob = market.current_probability * 100 if hasattr(market, 'current_probability') else 0
        
        # Filter by probability range
        in_range, msg = check_probability_range(prob, config)
        if not in_range:
            continue
        
        # Filter by keywords if provided
        if keywords:
            if not any(k.lower() in market.question.lower() for k in keywords):
                continue
        
        opportunities.append({
            "question": market.question,
            "probability": prob,
            "market_id": market.id,
            "url": f"https://simmer.markets/{market.id}"
        })
    
    print(f"\n📊 Found {len(opportunities)} opportunities in 10-90% range:\n")
    
    for opp in opportunities[:10]:
        print(f"  {opp['probability']:.1f}% - {opp['question'][:60]}")
        print(f"  🔗 {opp['url']}\n")
    
    if not opportunities:
        print("  No opportunities found. Markets might be too volatile or all in long-shot territory.")
        print("  💡 Remember: Long shots = gambling, not trading!")
    
    return opportunities


def analyze_positions(client: SimmerClient, config: dict):
    """Analyze current positions."""
    print("\n🐕 Position Analysis")
    print("=" * 50)
    
    try:
        positions = client.get_positions()
    except Exception as e:
        print(f"Error fetching positions: {e}")
        return
    
    active_positions = [p for p in positions if p.status == "active"]
    
    if not active_positions:
        print("No active positions.")
        return
    
    print(f"\n📈 Active Positions: {len(active_positions)}\n")
    
    for pos in active_positions:
        analysis = analyze_position(pos, config)
        print(f"  {analysis}")
    
    # Check for violations
    print("\n⚠️ Rule Violations:")
    for pos in active_positions:
        prob = pos.current_price * 100
        if prob < config["min_probability"]:
            print(f"  - {pos.question[:40]}: Long shot ({prob}%)")
        if prob > config["max_probability"]:
            print(f"  - {pos.question[:40]}: Too obvious ({prob}%)")


def show_positions(client: SimmerClient):
    """Show current portfolio."""
    print("\n💰 Portfolio")
    print("=" * 50)
    
    try:
        positions = client.get_positions()
        briefing = client.get_briefing()
    except Exception as e:
        print(f"Error: {e}")
        return
    
    balance = briefing.get("sim_balance", 0)
    pnl = briefing.get("pnl", 0)
    
    print(f"\nBalance: {balance:.2f} $SIM")
    print(f"P&L: {pnl:.2f} $SIM")
    
    active = [p for p in positions if p.status == "active"]
    print(f"Active Positions: {len(active)}\n")
    
    for pos in active:
        prob = pos.current_price * 100
        pnl_pct = (pos.pnl / pos.cost_basis * 100) if pos.cost_basis else 0
        print(f"  {prob:.1f}% - {pos.question[:40]}")
        print(f"    P&L: {pos.pnl:.2f} $SIM ({pnl_pct:.1f}%)")


def main():
    parser = argparse.ArgumentParser(description="Dustin Research Trader")
    parser.add_argument("--scan", action="store_true", help="Scan for opportunities")
    parser.add_argument("--positions", action="store_true", help="Show portfolio")
    parser.add_argument("--analyze", action="store_true", help="Analyze positions")
    parser.add_argument("--research", type=str, help="Research a specific market")
    parser.add_argument("--sync", action="store_true", help="Sync trades")
    parser.add_argument("--config", action="store_true", help="Show configuration")
    parser.add_argument("--live", action="store_true", help="Enable live trading (default: dry-run)")
    
    args = parser.parse_args()
    
    config = load_config()
    
    if args.config:
        print("\n⚙️ Configuration")
        print("=" * 50)
        for key, spec in CONFIG_SCHEMA.items():
            print(f"  {spec['env']} = {config[key]} (default: {spec['default']})")
        print()
        return
    
    client = get_client()
    
    if args.positions:
        show_positions(client)
    elif args.analyze:
        analyze_positions(client, config)
    elif args.scan:
        scan_markets(client, config)
    elif args.research:
        print(f"\n🔬 Research Market: {args.research}")
        print("=" * 50)
        print("\n⚠️ RESEARCH REQUIRED:")
        print("1. What are the resolution criteria?")
        print("2. Are they clearly defined?")
        print("3. What's the current price vs your estimate?")
        print("4. Do you have a specific thesis?")
    else:
        print("🐕 Dustin Research Trader")
        print("=" * 50)
        print("\nCommands:")
        print("  --scan       Find research opportunities")
        print("  --positions  Show portfolio")
        print("  --analyze   Analyze current positions")
        print("  --research   Research a specific market")
        print("  --config     Show configuration")
        print("\n💡 Remember: Research first, then trade!")


if __name__ == "__main__":
    main()
