import pytest

from game_engine import InfraSpecialist, Quant


class TestHiring:
    def test_hire_quant_rejects_below_min_salary(self, game_state):
        min_salary = game_state.minimum_salary_for_skill(50)
        success, message = game_state.hire_quant("Alice", 50, min_salary - 20_000)

        assert success is False
        assert "Salary too low" in message
        assert game_state.pending_hires == []

    def test_hire_quant_enqueues_and_deducts_signing_bonus(self, game_state):
        min_salary = game_state.minimum_salary_for_skill(50)
        offer = min_salary + 20_000

        success, message = game_state.hire_quant("Bob", 50, offer)

        assert success is True
        assert "Quant search started" in message
        assert len(game_state.pending_hires) == 1
        hire = game_state.pending_hires[0]
        assert hire.status == "onboarding"
        assert hire.onboarding_weeks == 2
        assert hire.salary == offer
        assert game_state.player.cash == 1_000_000 - int(offer * 0.2)

    def test_hire_infra_specialist_enqueues_and_deducts_cost(self, game_state):
        success, message = game_state.hire_infra_specialist("Ops", 60)

        assert success is True
        assert "Infra hire started" in message
        assert len(game_state.pending_infra) == 1
        hire = game_state.pending_infra[0]
        assert hire.status == "onboarding"
        assert hire.onboarding_weeks == 2
        expected_cost = 30_000 + int(60 * 1_500)
        assert game_state.player.cash == 1_000_000 - expected_cost


class TestInfrastructure:
    def test_upgrade_infra_levels_up_and_applies_refund(self, game_state):
        specialist = InfraSpecialist("Eve", 100)
        game_state.infra_team.append(specialist)

        success = game_state.upgrade_infra("compute_level")

        assert success is True
        assert game_state.infrastructure.compute_level == 2
        # Refund with 20% skill discount: 50k - 10k
        assert game_state.player.cash == 960_000
        assert specialist.happiness == 72


class TestFinance:
    def test_pay_weekly_salaries_reduces_cash_and_aum(self, game_state):
        game_state.team.append(Quant("Alice", 70, 52_000))
        infra_member = InfraSpecialist("Ops", 50)
        infra_member.salary = 52_000
        game_state.infra_team.append(infra_member)

        total = game_state.pay_weekly_salaries()

        assert total == pytest.approx(2_000)
        assert game_state.player.cash == pytest.approx(998_000)
        assert game_state.player.aum == pytest.approx(49_998_000)

    def test_pay_year_end_bonuses_require_positive_pnl(self, game_state):
        game_state.week = 52
        game_state.player.yearly_pnl = 1_000_000
        game_state.team.append(Quant("Alice", 70, 100_000))
        game_state.team[0].happiness = 80
        infra_member = InfraSpecialist("Ops", 50)
        infra_member.happiness = 50
        game_state.infra_team.append(infra_member)

        bonuses = game_state.pay_year_end_bonuses()

        assert bonuses == pytest.approx(12_400)
        assert game_state.player.cash == pytest.approx(987_600)
        assert game_state.player.aum == pytest.approx(49_987_600)

    def test_pay_year_end_bonuses_no_payout_when_pnl_negative(self, game_state):
        game_state.week = 52
        game_state.player.yearly_pnl = -100_000
        starting_cash = game_state.player.cash

        bonuses = game_state.pay_year_end_bonuses()

        assert bonuses == 0
        assert game_state.player.cash == starting_cash
