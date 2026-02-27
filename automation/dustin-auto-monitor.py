#!/usr/bin/env python3
"""
Dustin Auto-Monitor - Automatic position monitoring and trading
Runs every 15 minutes, applies rules automatically
"""

import os
import sys
import json
import requests
from datetime import datetime

sys.stdout.reconfigure(line_buffering=True)

API_KEY = os.environ.get("SIMMER_API_KEY")
if not API_KEY:
    print("ERROR: SIMMER_API_KEY not set")
    sys.exit(1)

BASE_URL = "https://api.simmer.markets/api/sdk"

def get_headers():
    return {"Authorization": f"Bearer {API_KEY}"}

def get_positions():
    r = requests.get(f"{BASE_URL}/positions", headers=get_headers())
    return r.json().get("positions", [])

def get_balance():
    r = requests.get(f"{BASE_URL}/briefing", headers=get_headers())
    return r.json().get("venues", {}).get("simmer", {}).get("balance", 0)

def sell_position(market_id, amount_or_shares, is_shares=False, reasoning=""):
    """Sell a position."""
    data = {
        "market_id": market_id,
        "side": "yes",
        "action": "sell",
        "reasoning": reasoning
    }
    if is_shares:
        data["shares"] = amount_or_shares
    else:
        data["amount"] = amount_or_shares
    
    r = requests.post(f"{BASE_URL}/trade", json=data, headers=get_headers())
    return r.json()

def check_and_act():
    """Main monitoring loop."""
    print(f"\n{'='*50}")
    print(f"🤖 Dustin Auto-Monitor - {datetime.now().isoformat()}")
    print(f"{'='*50}")
    
    positions = get_positions()
    balance = get_balance()
    
    print(f"💰 Balance: {balance:.2f} $SIM")
    print(f"📊 Positions: {len(positions)}")
    
    actions_taken = []
    
    for pos in positions:
        if pos.get("status") != "active":
            continue
        
        question = pos.get("question", "")[:40]
        prob = pos.get("current_price", 0) * 100
        pnl = pos.get("pnl", 0)
        value = pos.get("current_value", 0)
        market_id = pos.get("market_id")
        shares = pos.get("shares_yes", 0)
        
        print(f"\n📌 {question}...")
        print(f"   Price: {prob:.1f}% | PnL: {pnl:.2f} | Value: {value:.2f}")
        
        # RULE 1: Long Shot Rule - <10% = SELL
        if prob < 10:
            print(f"   🚨 LONG SHOT! ({prob:.1f}%) - SELLING!")
            try:
                # Sell all shares
                result = sell_position(market_id, int(shares), is_shares=True, 
                    reasoning=f"Auto-sell: Long shot at {prob:.1f}%")
                if result.get("success"):
                    recovered = result.get("cost", 0)
                    print(f"   ✅ SOLD! Recovered: {recovered:.2f} $SIM")
                    actions_taken.append(f"Sold {question} for {recovered:.2f}")
                else:
                    print(f"   ❌ Failed: {result.get('error')}")
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        # RULE 2: Concentration > 70% = REDUCE
        # This would need balance info - simplified check
        elif prob > 90:
            print(f"   ⚠️ Too obvious ({prob:.1f}%) - consider taking profit")
    
    print(f"\n{'='*50}")
    if actions_taken:
        print(f"✅ Actions: {len(actions_taken)}")
        for a in actions_taken:
            print(f"   - {a}")
    else:
        print("✅ No actions needed")
    print(f"{'='*50}\n")
    
    return actions_taken

if __name__ == "__main__":
    check_and_act()
