import random
from minigames.trivia_bank import get_trivia_questions


class MarketTriviaGame:
    def __init__(self, question_count=3):
        self.type = "market_trivia"
        self.question_count = question_count
        self.current_index = 0
        self.score = 0
        self.questions = []
        self.bank = get_trivia_questions()

    def start(self):
        self.current_index = 0
        self.score = 0
        random.shuffle(self.bank)
        self.questions = self.bank[: min(self.question_count, len(self.bank))]
        return self._current_payload()

    def _current_payload(self):
        if self.current_index >= len(self.questions):
            return None
        q = self.questions[self.current_index]
        return {
            "index": self.current_index + 1,
            "total": len(self.questions),
            "prompt": q["prompt"],
            "options": q["options"],
            "score": self.score,
        }

    def submit(self, choice_index):
        if self.current_index >= len(self.questions):
            return {"error": "No active question"}

        q = self.questions[self.current_index]
        correct = choice_index == q["answer"]
        if correct:
            self.score += 20

        result = {
            "correct": correct,
            "answer_index": q["answer"],
            "score": self.score,
        }

        self.current_index += 1
        next_q = self._current_payload()
        game_over = next_q is None
        reward = None
        if game_over:
            if self.score >= 40:
                reward = "XP +50 and Research Insight"
            elif self.score >= 20:
                reward = "XP +30"
            else:
                reward = "No XP this run. Get 1+ correct to start scoring."

        result["next_question"] = next_q
        result["game_over"] = game_over
        result["reward"] = reward
        return result
