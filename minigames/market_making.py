import random
import numpy as np

class MarketMakingGame:
    def __init__(self):
        self.type = "market_making"
        self.rounds = 10
        self.current_round = 0
        self.mid_price = 100.0
        self.inventory = 0
        self.cash = 0.0
        self.history = []
        self.volatility = 1.0

    def start(self):
        self.current_round = 1
        self.mid_price = 100.0
        self.inventory = 0
        self.cash = 0.0
        self.history = [{
            "round": 0,
            "mid_price": self.mid_price,
            "inventory": 0,
            "cash": 0,
            "pnl": 0
        }]
        return self.get_state()

    def get_state(self):
        return {
            "round": self.current_round,
            "max_rounds": self.rounds,
            "mid_price": self.mid_price,
            "inventory": self.inventory,
            "cash": self.cash,
            "pnl": self.cash + (self.inventory * self.mid_price),
            "history": self.history
        }

    def submit(self, spread):
        # Player submits a half-spread (e.g. 0.5 means bid=mid-0.5, ask=mid+0.5)
        half_spread = float(spread)
        bid = self.mid_price - half_spread
        ask = self.mid_price + half_spread
        
        # Simulate market move
        move = np.random.normal(0, self.volatility)
        new_mid = self.mid_price + move
        
        # Simulate order flow
        # Probability of fill depends on spread and volatility
        # Tighter spread -> higher prob fill
        # Simple model: prob = exp(-k * half_spread)
        fill_prob = np.exp(-0.5 * half_spread)
        
        buy_filled = False
        sell_filled = False
        
        # Market sell order hits our bid?
        if random.random() < fill_prob:
            self.inventory += 1
            self.cash -= bid
            buy_filled = True
            
        # Market buy order hits our ask?
        if random.random() < fill_prob:
            self.inventory -= 1
            self.cash += ask
            sell_filled = True
            
        self.mid_price = new_mid
        self.current_round += 1
        
        state = self.get_state()
        state["last_action"] = {
            "bid": bid,
            "ask": ask,
            "buy_filled": buy_filled,
            "sell_filled": sell_filled
        }
        self.history.append(state)
        
        game_over = self.current_round > self.rounds
        reward = "None"
        xp_gain = 0
        
        if game_over:
            final_pnl = state["pnl"]
            if final_pnl >= 10:
                xp_gain = max(25, int(final_pnl / 2))
                reward = f"XP +{xp_gain} for solid PnL"
            elif final_pnl >= 0:
                xp_gain = 15
                reward = "XP +15 for breakeven grind"
            else:
                xp_gain = 5
                reward = "XP +5 for lessons learned"
        
        return {
            "game_over": game_over,
            "state": state,
            "reward": reward,
            "xp_gain": xp_gain
        }
