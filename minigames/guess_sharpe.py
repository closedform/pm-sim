import random
import numpy as np

class GuessSharpeGame:
    def __init__(self, rounds=5):
        self.type = "guess_sharpe"
        self.total_rounds = rounds
        self.current_round = 0
        self.score = 0
        self.history = []
        self.data = {}

    def _generate_round(self):
        weeks = 52
        scenario = random.choices(
            ["positive", "negative", "flat"],
            weights=[0.6, 0.25, 0.15],
            k=1
        )[0]

        vol = random.uniform(0.10, 0.22)
        if scenario == "flat":
            true_sharpe = 0.0
            vol = random.uniform(0.04, 0.12)
            mean_ret = random.uniform(-0.0005, 0.0005)
        elif scenario == "negative":
            true_sharpe = random.uniform(-1.5, -0.25)
            mean_ret = true_sharpe * vol / np.sqrt(52)
        else:
            true_sharpe = random.uniform(0.35, 2.5)
            mean_ret = true_sharpe * vol / np.sqrt(52)

        returns = np.random.normal(mean_ret, vol / np.sqrt(52), weeks)
        cumulative_returns = np.cumprod(1 + returns) - 1

        # Nudge paths to reflect the intended scenario
        if scenario == "negative" and cumulative_returns[-1] > 0:
            bias = (cumulative_returns[-1] + 0.02) / weeks
            returns -= abs(bias)
            cumulative_returns = np.cumprod(1 + returns) - 1
        elif scenario == "flat":
            bias = cumulative_returns[-1] / weeks
            returns -= bias
            cumulative_returns = np.cumprod(1 + returns) - 1

        return {
            "returns": returns.tolist(),
            "cumulative": cumulative_returns.tolist(),
            "true_sharpe": true_sharpe
        }

    def _score_points(self, error):
        if error <= 0.05:
            return 150
        if error <= 0.15:
            return 120
        if error <= 0.30:
            return 80
        if error <= 0.50:
            return 40
        return 15

    def _round_payload(self):
        return {
            "round": self.current_round,
            "total_rounds": self.total_rounds,
            "score": self.score,
            "cumulative": self.data["cumulative"]
        }

    def start(self):
        self.current_round = 1
        self.score = 0
        self.history = []
        self.data = self._generate_round()
        return self._round_payload()

    def submit(self, guess):
        true_sharpe = self.data['true_sharpe']
        error = abs(guess - true_sharpe)

        points = self._score_points(error)
        self.score += points

        self.history.append({
            "round": self.current_round,
            "true_sharpe": true_sharpe,
            "guess": guess,
            "error": error,
            "points": points
        })

        finished_round = self.current_round
        game_over = self.current_round >= self.total_rounds

        next_round_payload = None
        if not game_over:
            self.current_round += 1
            self.data = self._generate_round()
            next_round_payload = self._round_payload()

        tolerance = max(0.05, abs(true_sharpe) * 0.05)  # allow 5% relative error, with a small floor
        success = error <= tolerance
        reward = "Precision Bonus" if success else "Practice Makes Perfect"

        return {
            "success": success,
            "true_sharpe": true_sharpe,
            "error": error,
            "points": points,
            "cumulative_score": self.score,
            "round_finished": finished_round,
            "game_over": game_over,
            "next_round": next_round_payload,
            "history": self.history,
            "reward": reward
        }
