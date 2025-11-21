import pytest

from game_engine import AlphaStrategy, GameState, Quant


class TestPortfolio:
    def test_update_portfolio_promotes_researched_alpha(self, game_state):
        alpha = AlphaStrategy("Stored Alpha", "Trend", 3)
        alpha.status = "stored_for_ensemble"
        alpha.current_expected_return = 0.12
        game_state.alphas["stored_for_ensemble"].append(alpha)

        positions = [{"alpha_id": alpha.id, "weight": 0.3}]

        game_state.update_portfolio(positions)

        assert alpha.status == "live"
        assert alpha in game_state.alphas["live"]
        assert alpha not in game_state.alphas["stored_for_ensemble"]
        assert game_state.portfolio.positions == positions

    def test_update_portfolio_normalizes_weights_when_overweight(self, game_state):
        alpha_one = AlphaStrategy("Alpha One", "Trend", 3)
        alpha_two = AlphaStrategy("Alpha Two", "Value", 3)
        for alpha in (alpha_one, alpha_two):
            alpha.status = "live"
            game_state.alphas["live"].append(alpha)

        positions = [
            {"alpha_id": alpha_one.id, "weight": 0.6},
            {"alpha_id": alpha_two.id, "weight": 0.8},
        ]

        game_state.update_portfolio(positions)

        weights = [p["weight"] for p in game_state.portfolio.positions]
        assert sum(weights) == pytest.approx(1.0)
        # Weights should stay proportional after normalization
        ratio = weights[0] / 0.6
        assert weights[1] / 0.8 == pytest.approx(ratio)


class TestResearch:
    def test_calculate_research_duration_reflects_team_and_infra(self, game_state):
        game_state.team = [
            Quant("Alice", 70, 120_000),
            Quant("Bob", 65, 110_000),
        ]
        game_state.infrastructure.compute_level = 2
        game_state.infrastructure.data_quality = 2

        effective = game_state.calculate_research_duration(base_weeks=6)

        assert effective == 5

    def test_start_research_sets_expected_probabilities(self, game_state):
        alpha = game_state.start_research("Trend", 6)

        assert alpha in game_state.alphas["in_research"]
        assert alpha.weeks_remaining == 6
        assert alpha.success_prob == pytest.approx(0.65)
        assert alpha.potential_super == pytest.approx(0.03)
        assert alpha.resilience == pytest.approx(0.3)
