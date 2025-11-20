import random
import numpy as np
import json
import os

class GameState:
    def __init__(self):
        self.week = 1
        self.year = 1
        self.player = Player()
        self.team = []
        self.infra_team = []
        self.pending_hires = []  # list of Quant not yet onboarded
        self.pending_infra = []  # infra specialists onboarding
        self.portfolio = Portfolio()
        self.infrastructure = Infrastructure()
        self.risk_model = RiskModel()
        self.risk_research = []
        self.alphas = {
            "live": [],
            "in_research": [],
            "stored_for_ensemble": [],
            "ensembles": []
        }
        self.events_queue = []
        self.message_log = ["System initialized.", "Welcome to the fund, PM.", "Market data feed connected..."]
        self.environment = {
            "regime": "Trendy",
            "weeks_in_regime": 0
        }
        self.active_minigame_instance = None

    def log(self, message):
        self.message_log.append(f"[W{self.week}] {message}")
        if len(self.message_log) > 50:
            self.message_log.pop(0)

    def process_start_of_week(self):
        # Story / Hints
        if self.week == 1 and self.year == 1:
            self.log("Hint: Hire a quant and start research immediately.")
        if self.player.cash < 100_000:
            self.log("WARNING: Cash reserves critical.")
        
        # 1. Regime evolution
        if random.random() < 0.05: # 5% chance to change regime
            regimes = ["Trendy", "MeanReverting", "HighVol", "LowVol"]
            new_regime = random.choice(regimes)
            self.environment["regime"] = new_regime
            self.environment["weeks_in_regime"] = 0
            self.log(f"MARKET REGIME CHANGE DETECTED: Now {new_regime}")
        else:
            self.environment["weeks_in_regime"] += 1

        # 2. Alpha decay
        for alpha in self.alphas["live"] + self.alphas["stored_for_ensemble"]:
            alpha.decay(self.environment["regime"])

        # 3. Process research
        completed_research = []
        for alpha in self.alphas["in_research"]:
            alpha.weeks_remaining -= 1
            if alpha.weeks_remaining <= 0:
                completed_research.append(alpha)
        
        for alpha in completed_research:
            self.alphas["in_research"].remove(alpha)
            # Roll for success
            success_prob = getattr(alpha, "success_prob", 0.5 + (self.infrastructure.data_quality * 0.05))
            if random.random() < success_prob:
                alpha.status = "stored_for_ensemble" # Or ready to deploy
                # Generate stats
                if random.random() < getattr(alpha, "potential_super", 0.02):
                    alpha.base_expected_return = random.uniform(0.18, 0.35)
                    alpha.current_expected_return = alpha.base_expected_return
                    alpha.volatility = random.uniform(0.08, 0.18)
                    alpha.decay_rate = max(0.003, 0.01 * (1 - alpha.resilience))
                    self.apply_alpha_penalty_to_stats(alpha)
                    self.events_queue.append(Event("Breakthrough Alpha", f"{alpha.name} looks extraordinary. Guard it well.", []))
                    self.log(f"Breakthrough: {alpha.name} discovered (Exp Ret: {alpha.base_expected_return:.1%})")
                    self.player.gain_xp(150)
                    self.bump_team_happiness(6, "Breakthrough research lit up the desk.")
                else:
                    alpha.base_expected_return = random.uniform(0.05, 0.18)
                    alpha.current_expected_return = alpha.base_expected_return
                    alpha.volatility = random.uniform(0.05, 0.15)
                    alpha.decay_rate = max(0.005, 0.015 * (1 - alpha.resilience))
                    self.apply_alpha_penalty_to_stats(alpha)
                    self.events_queue.append(Event("Research Complete", f"Alpha {alpha.name} finished research successfully!", []))
                    self.log(f"Research SUCCESS: {alpha.name} discovered (Exp Ret: {alpha.base_expected_return:.1%})")
                    self.bump_team_happiness(3, "Research win energized the team.")
                    self.player.gain_xp(100)
                self.alphas["stored_for_ensemble"].append(alpha)
            else:
                self.events_queue.append(Event("Research Failed", f"Alpha {alpha.name} failed to produce results.", []))
                self.log(f"Research FAILURE: {alpha.name} yielded no signal.")

        # Process risk model research
        completed_risk = []
        for proj in self.risk_research:
            proj.weeks_remaining -= 1
            if proj.weeks_remaining <= 0:
                completed_risk.append(proj)
        for proj in completed_risk:
            self.risk_research.remove(proj)
            success_bonus = 0.1 * (self.infrastructure.data_quality - 1)
            avg_skill = self.avg_team_skill() or 50
            avg_happy = self.avg_team_happiness() or 50
            p_success = min(0.95, 0.6 + success_bonus + avg_skill * 0.002 + max(0, (avg_happy - 50) * 0.002))
            if random.random() < p_success:
                self.risk_model.level += 1
                self.player.gain_xp(120)
                self.events_queue.append(Event("Risk Model Upgrade", f"{proj.name} completed. Risk model level is now {self.risk_model.level}.", []))
                self.log(f"Risk research success: {proj.name}. Risk level {self.risk_model.level}.")
                self.player.reputation_infra = min(100, self.player.reputation_infra + 2)
            else:
                self.events_queue.append(Event("Risk Research Failed", f"{proj.name} stalled; revisit later.", []))
                self.log(f"Risk research failed: {proj.name}.")

        # 4. Random events
        if random.random() < 0.1:
            self.events_queue.append(Event("Market News", "Something happened in the market.", []))
        # 5. Infra outages (chance reduced by resilience)
        self.maybe_infra_outage()
        # 5. Team requests (infra/data tooling) with small chance weekly
        if random.random() < 0.1 and self.team:
            self.enqueue_infra_request()

    def to_dict(self):
        avg_happiness = self.avg_team_happiness()
        return {
            "week": self.week,
            "year": self.year,
            "player": self.player.to_dict(),
            "team": [q.to_dict() for q in self.team],
            "pending_hires": [q.to_dict() for q in self.pending_hires],
            "infra_team": [m.to_dict() for m in self.infra_team],
            "pending_infra": [m.to_dict() for m in self.pending_infra],
            "portfolio": self.portfolio.to_dict(),
            "infrastructure": self.infrastructure.to_dict(),
            "risk_model": self.risk_model.to_dict(),
            "risk_research": [r.to_dict() for r in self.risk_research],
            "resilience_score": self.resilience_score(),
            "alphas": {
                "live": [a.to_dict() for a in self.alphas["live"]],
                "in_research": [a.to_dict() for a in self.alphas["in_research"]],
                "stored_for_ensemble": [a.to_dict() for a in self.alphas["stored_for_ensemble"]],
                "ensembles": [a.to_dict() for a in self.alphas["ensembles"]]
            },
            "events_queue": [e.to_dict() for e in self.events_queue],
            "message_log": self.message_log,
            "environment": self.environment,
            "avg_team_happiness": avg_happiness
        }

    def save(self, name="savegame"):
        os.makedirs("saves", exist_ok=True)
        safe = "".join(c for c in name if c.isalnum() or c in ['_', '-']).strip()
        if not safe:
            safe = "savegame"
        filename = os.path.join("saves", f"{safe}.json")
        with open(filename, 'w') as f:
            json.dump(self.to_dict(), f, indent=4)

    @classmethod
    def load(cls, name="savegame"):
        safe = "".join(c for c in name if c.isalnum() or c in ['_', '-']).strip()
        if not safe:
            safe = "savegame"
        filename = os.path.join("saves", f"{safe}.json")
        if not os.path.exists(filename):
            return cls()
        
        with open(filename, 'r') as f:
            data = json.load(f)
        
        game = cls()
        game.week = data['week']
        game.year = data['year']
        
        # Restore Player
        game.player.__dict__.update(data['player'])
        if not hasattr(game.player, "minigame_stats"):
            game.player.minigame_stats = {"guess_sharpe_leaderboard": []}
        if not hasattr(game.player, "reputation_infra"):
            game.player.reputation_infra = 50
        if not hasattr(game.player, "startup_grace_weeks"):
            game.player.startup_grace_weeks = 4
        if not hasattr(game.player, "starting_aum"):
            game.player.starting_aum = game.player.aum
        if not hasattr(game.player, "alpha_difficulty"):
            game.player.alpha_difficulty = 1.0
        if not hasattr(game.player, "reset_offer_used"):
            game.player.reset_offer_used = False
        if not hasattr(game.player, "reset_offer_active"):
            game.player.reset_offer_active = False
        if not hasattr(game.player, "reset_offer_cooldown"):
            game.player.reset_offer_cooldown = 0
        
        # Restore Team
        game.team = []
        for q_data in data['team']:
            q = Quant(q_data['name'], q_data['skill'], q_data['salary'])
            q.__dict__.update(q_data)
            game.team.append(q)
        # Restore pending hires
        game.pending_hires = []
        if 'pending_hires' in data:
            for q_data in data['pending_hires']:
                q = Quant(q_data['name'], q_data['skill'], q_data['salary'])
                q.__dict__.update(q_data)
                game.pending_hires.append(q)
        # Restore Infra Team
        game.infra_team = []
        if 'infra_team' in data:
            for m_data in data['infra_team']:
                m = InfraSpecialist(m_data['name'], m_data.get('skill', 50))
                m.__dict__.update(m_data)
                game.infra_team.append(m)
        # Restore pending infra
        game.pending_infra = []
        if 'pending_infra' in data:
            for m_data in data['pending_infra']:
                m = InfraSpecialist(m_data['name'], m_data.get('skill', 50))
                m.__dict__.update(m_data)
                game.pending_infra.append(m)
            
        # Restore Portfolio
        game.portfolio.positions = data['portfolio']['positions']
        
        # Restore Infra & Risk
        game.infrastructure.__dict__.update(data['infrastructure'])
        game.risk_model.__dict__.update(data['risk_model'])
        if not hasattr(game.risk_model, "market_neutral"):
            game.risk_model.market_neutral = False
        if not hasattr(game.risk_model, "factor_neutral"):
            game.risk_model.factor_neutral = False
        if not hasattr(game, "risk_research"):
            game.risk_research = []
        if 'risk_research' in data:
            game.risk_research = []
            for r_data in data['risk_research']:
                r = RiskResearch(r_data['name'], r_data['duration'])
                r.__dict__.update(r_data)
                game.risk_research.append(r)
        
        # Restore Alphas
        # Helper to restore alpha list
        def restore_alphas(alpha_list_data):
            alphas = []
            for a_data in alpha_list_data:
                a = AlphaStrategy(a_data['name'], a_data['style'], a_data['research_duration'])
                a.__dict__.update(a_data)
                alphas.append(a)
            return alphas

        game.alphas['live'] = restore_alphas(data['alphas']['live'])
        game.alphas['in_research'] = restore_alphas(data['alphas']['in_research'])
        game.alphas['stored_for_ensemble'] = restore_alphas(data['alphas']['stored_for_ensemble'])
        # Ensembles not fully implemented yet, but structure is there
        
        # Restore Environment
        game.environment = data['environment']
        
        return game

    @staticmethod
    def list_saves():
        os.makedirs("saves", exist_ok=True)
        saves = []
        for fname in os.listdir("saves"):
            if fname.endswith(".json"):
                saves.append(fname.replace(".json", ""))
        saves.sort()
        return saves

    def restart(self):
        self.__init__()
        self.process_start_of_week()

    def process_end_of_week(self):
        # Calculate returns
        weekly_pnl = 0.0
        portfolio_value = self.player.aum
        market_ret = generate_market_return(self.environment["regime"])
        hedge_beta_effect = 0 if self.is_market_shielded() else 1
        
        for position in self.portfolio.positions:
            alpha = self.get_alpha_by_id(position["alpha_id"])
            if alpha:
                alpha_beta = getattr(alpha, "beta", 1.0)
                ret = simulate_alpha_return(alpha, self.environment["regime"])
                ret += market_ret * alpha_beta * hedge_beta_effect
                pnl = portfolio_value * position["weight"] * ret
                weekly_pnl += pnl
        
        # Update player stats
        self.player.cash += weekly_pnl # Simplified: PnL goes to cash? Or AUM? Usually AUM.
        self.player.aum += weekly_pnl
        self.player.pnl_history.append(weekly_pnl)
        self.player.yearly_pnl += weekly_pnl
        # Update drawdowns
        self.update_drawdowns()
        
        if weekly_pnl > 0:
            xp_gain = int(weekly_pnl / 10000) # 1 XP per 10k profit
            self.player.gain_xp(xp_gain)
            boost = min(4, 1 + int(weekly_pnl / 100000))
            if boost > 0:
                self.bump_team_happiness(boost, "Strong signals boosted team confidence.")
                self.player.reputation_quants = min(100, self.player.reputation_quants + 1)
        elif weekly_pnl < 0 and weekly_pnl > -50_000:
            # Calm leadership through choppy weeks helps morale modestly
            self.bump_team_happiness(1, "Team appreciated steady leadership in a tough week.")
            self.player.reputation_management = min(100, self.player.reputation_management + 1)

        # Weekly compensation (salaries)
        weekly_pay = self.pay_weekly_salaries()
        # Annual bonuses at end of week 52
        bonus_pay = self.pay_year_end_bonuses()
        # Hiring pipeline and mentoring
        self.process_hiring_pipeline()
        self.process_infra_hiring()
        self.mentor_quants()
        self.management_reaction(weekly_pnl)

        # Story log for the turn
        self.log_week_story(weekly_pnl, weekly_pay, bonus_pay, market_ret)
        
        # Update week
        self.week += 1
        if self.week > 52:
            self.week = 1
            self.year += 1
            self.player.yearly_pnl = 0.0
        if self.player.startup_grace_weeks > 0:
            self.player.startup_grace_weeks -= 1

        # Team morale effects (can impact job security)
        self.apply_team_morale_effects()
        self.maybe_team_meeting()
        self.check_reset_offer()

        # Check Win/Loss
        if self.player.job_security <= 0:
            self.events_queue.append(Event("GAME OVER", "You have been fired. Your fund collapsed.", [{"text": "Restart", "effect": "restart"}]))
        elif self.player.aum < 10_000_000 and not self.player.reset_offer_active:
            self.events_queue.append(Event("GAME OVER", "AUM dropped too low. The fund has been shut down.", [{"text": "Restart", "effect": "restart"}]))
        elif self.player.aum > 1_000_000_000:
            self.events_queue.append(Event("YOU WIN!", "You reached $1B AUM! You are a legend.", [{"text": "Continue", "effect": "continue"}]))

    def get_alpha_by_id(self, alpha_id):
        for group in self.alphas.values():
            for alpha in group:
                if alpha.id == alpha_id:
                    return alpha
        return None

    def start_research(self, style, duration):
        if style == "RiskModel":
            return self.start_risk_model_research(duration)
        effective_duration = self.calculate_research_duration(duration)
        new_alpha = AlphaStrategy(f"Alpha {len(self.alphas['in_research']) + len(self.alphas['live']) + 1}", style, effective_duration)
        new_alpha.base_research_duration = duration
        new_alpha.weeks_remaining = effective_duration

        # Success probability boosted by infra, team skill, and morale
        base_success = 0.5 + (self.infrastructure.data_quality * 0.05)
        avg_skill = self.avg_team_skill() or 50
        avg_happy = self.avg_team_happiness() or 50
        infra_bonus = 0.02 * (self.infrastructure.compute_level - 1)
        skill_bonus = min(0.2, avg_skill * 0.002)
        morale_bonus = max(0, (avg_happy - 50) * 0.002)
        success_prob = min(0.95, base_success + infra_bonus + skill_bonus + morale_bonus)
        success_prob = self.apply_alpha_success_penalty(success_prob)

        self.alphas["in_research"].append(new_alpha)
        if effective_duration < duration:
            self.log(f"Research acceleration applied ({duration} -> {effective_duration} weeks).")

        # Determine on-complete stats now to bake in team/infra quality
        new_alpha.success_prob = success_prob
        new_alpha.potential_super = self.super_alpha_chance(avg_skill, avg_happy)
        new_alpha.resilience = self.alpha_resilience(avg_skill, avg_happy)
        return new_alpha

    def start_risk_model_research(self, duration):
        effective_duration = self.calculate_research_duration(duration)
        project = RiskResearch(f"Risk Model Upgrade {len(self.risk_research)+1}", effective_duration)
        project.base_duration = duration
        project.weeks_remaining = effective_duration
        self.risk_research.append(project)
        self.log(f"Risk research started: {project.name} ({effective_duration} weeks).")
        return project

    def hire_quant(self, name, skill, salary):
        if not name:
            return False, "Please provide a name."
        min_salary = self.minimum_salary_for_skill(skill)
        if salary < min_salary:
            return False, f"Salary too low for skill {skill}. Offer at least ${min_salary:,.0f}."
        signing_bonus = int(salary * 0.2)
        if self.player.cash < signing_bonus:
            return False, "Not enough cash for signing bonus."
        new_quant = Quant(name, skill, salary)
        # Assign random avatar (placeholder for now)
        avatars = ["wizard", "robot", "cat", "alien"]
        new_quant.avatar = random.choice(avatars)
        new_quant.happiness = min(100, 65 + int((salary - min_salary) / 3000))
        # Hiring pipeline: time depends on skill
        base_weeks = 1 if skill < 40 else 2 if skill < 70 else 4
        if self.player.reputation_management >= 70:
            base_weeks = max(1, base_weeks - 1)
        elif self.player.reputation_management <= 30:
            base_weeks += 1
        new_quant.onboarding_weeks = base_weeks
        new_quant.status = "onboarding"
        self.pending_hires.append(new_quant)
        self.player.cash -= signing_bonus
        self.log(f"Hiring {name} (Skill {skill}) started. ETA {base_weeks} weeks. Signing bonus ${signing_bonus:,.0f}.")
        return True, "Quant search started"

    def upgrade_infra(self, infra_type):
        cost = 50000
        if self.player.cash < cost:
            return False
        self.player.cash -= cost
        current_level = getattr(self.infrastructure, infra_type)
        setattr(self.infrastructure, infra_type, current_level + 1)
        if self.infra_team:
            avg_skill = sum(m.skill for m in self.infra_team) / len(self.infra_team)
            discount = min(0.2, avg_skill / 500)
            refund = int(cost * discount)
            self.player.cash += refund
            self.log(f"Infrastructure squad optimized the spend. Saved ${refund:,.0f}.")
            # Small morale bump to infra team
            for m in self.infra_team:
                m.happiness = min(100, m.happiness + 2)
        return True

    def hire_infra_specialist(self, name, skill):
        if not name:
            return False, "Please provide a name."
        cost = 30000 + int(skill * 1500)
        if self.player.cash < cost:
            return False, "Not enough cash for infra hire."
        new_member = InfraSpecialist(name, skill)
        base_weeks = 1 if skill < 50 else 2 if skill < 75 else 4
        if self.player.reputation_management >= 70:
            base_weeks = max(1, base_weeks - 1)
        elif self.player.reputation_management <= 30:
            base_weeks += 1
        new_member.onboarding_weeks = base_weeks
        new_member.status = "onboarding"
        self.pending_infra.append(new_member)
        self.player.cash -= cost
        self.log(f"Infra hire started: {name} (Skill {skill}) cost ${cost:,.0f}, ETA {new_member.onboarding_weeks} weeks.")
        return True, "Infra hire started"

    def fire_staff(self, staff_type, name):
        if staff_type == "quant":
            target_list = self.team
        elif staff_type == "infra":
            target_list = self.infra_team
        else:
            return False, "Unknown staff type"
        member = next((m for m in target_list if m.name == name), None)
        if not member:
            return False, "Staff not found"
        target_list.remove(member)
        # Morale penalty scales with how abrupt the firing is
        self.bump_team_happiness(-5, f"Fired {name} ({staff_type}). Team morale dropped.")
        self.player.reputation_management = max(0, self.player.reputation_management - 3)
        self.log(f"Fired {name} ({staff_type}).")
        return True, "Staff fired"

    def update_portfolio(self, positions):
        # Validate weights sum <= 1 (or allow leverage? let's stick to 1 for now)
        total_weight = sum(p['weight'] for p in positions)
        if total_weight > 1.0:
            # Normalize or reject? Let's normalize for UX
            for p in positions:
                p['weight'] /= total_weight
        
        self.portfolio.positions = positions
        
        # Move alphas to live if they are in stored
        for pos in positions:
            alpha = self.get_alpha_by_id(pos['alpha_id'])
            if alpha and alpha.status == "stored_for_ensemble":
                alpha.status = "live"
                self.alphas["stored_for_ensemble"].remove(alpha)
                self.alphas["live"].append(alpha)

    def clear_event(self):
        if self.events_queue:
            self.events_queue.pop(0)

    def apply_team_morale_effects(self):
        if not self.team:
            return
        total = 0
        for quant in self.team:
            min_salary = self.minimum_salary_for_skill(quant.skill)
            if quant.salary < min_salary:
                drop = min(15, 3 + int((min_salary - quant.salary) / 5000))
                quant.happiness = max(0, quant.happiness - drop)
                quant.loyalty = max(0, quant.loyalty - drop // 2)
            else:
                bump = 1 if quant.happiness < 95 else 0
                quant.happiness = min(100, quant.happiness + bump)
                quant.loyalty = min(100, quant.loyalty + bump)
            if quant.happiness < 25:
                quant.loyalty = max(0, quant.loyalty - 2)
            total += quant.happiness
            if quant.happiness < 40:
                self.player.reputation_quants = max(0, self.player.reputation_quants - 1)
            else:
                self.player.reputation_quants = min(100, self.player.reputation_quants + 0.2)

        avg = total / len(self.team)
        if avg < 35:
            penalty = max(5, int((35 - avg) * 0.8))
            self.player.job_security -= penalty
            self.log(f"Team morale warning: avg happiness {avg:.0f}. Management trust -{penalty}.")
            if avg < 20 and random.random() < 0.35:
                revolt_penalty = 20
                self.player.job_security -= revolt_penalty
                self.events_queue.append(Event("Desk Revolt", "Unhappy quants escalated to management. You were reprimanded hard. Fix morale or risk termination.", []))
                self.player.reputation_management = max(0, self.player.reputation_management - 3)
        # Attrition risk: very unhappy quants can leave
        if avg < 30 and random.random() < 0.2 and self.team:
            flight_risks = [q for q in self.team if q.happiness < 30]
            if flight_risks:
                departed = random.choice(flight_risks)
                self.team.remove(departed)
                self.events_queue.append(Event(
                    "Talent Poached",
                    f"{departed.name} was hired away by a competing fund after prolonged unhappiness. Remaining team is unsettled.",
                    []
                ))
                for q in self.team:
                    q.happiness = max(0, q.happiness - 5)
                    q.loyalty = max(0, q.loyalty - 3)
                self.log(f"Attrition hit: {departed.name} left for a competitor. Team morale dipped.")
                self.player.reputation_management = max(0, self.player.reputation_management - 2)

    def resilience_score(self):
        infra = self.infrastructure
        base = 30
        base += (infra.compute_level + infra.data_quality + infra.devops_tooling + infra.risk_tools_level + infra.optimization_tool_level) * 6
        if self.infra_team:
            avg_skill = sum(m.skill for m in self.infra_team) / len(self.infra_team)
            avg_happy = sum(m.happiness for m in self.infra_team) / len(self.infra_team)
            base += avg_skill * 0.1
            base += max(0, (avg_happy - 50) * 0.1)
        return max(0, min(100, int(base)))

    def process_hiring_pipeline(self):
        if not self.pending_hires:
            return
        completed = []
        for q in self.pending_hires:
            q.onboarding_weeks -= 1
            if q.onboarding_weeks <= 0:
                completed.append(q)
        for q in completed:
            q.status = "active"
            self.pending_hires.remove(q)
            self.team.append(q)
            self.log(f"{q.name} joined the team. Skill {q.skill}.")

    def process_infra_hiring(self):
        if not self.pending_infra:
            return
        completed = []
        for m in self.pending_infra:
            m.onboarding_weeks -= 1
            if m.onboarding_weeks <= 0:
                completed.append(m)
        for m in completed:
            m.status = "active"
            self.pending_infra.remove(m)
            self.infra_team.append(m)
            self.log(f"{m.name} joined the infra team. Skill {m.skill}.")
    def mentor_quants(self):
        # Simple mentoring: modest skill growth if morale is good
        avg_h = self.avg_team_happiness()
        if not self.team or avg_h is None or avg_h < 60:
            return
        for q in self.team:
            gain = random.choice([0, 1, 1])
            if gain:
                q.skill = min(100, q.skill + gain)
                if random.random() < 0.4:
                    q.happiness = min(100, q.happiness + 1)

    def maybe_infra_outage(self):
        res = self.resilience_score()
        # Factor in infra reputation; low rep increases risk
        rep_infra = getattr(self.player, "reputation_infra", 50)
        base_chance = 0.18 + max(0, (60 - rep_infra)) * 0.002
        chance = max(0.02, base_chance - (res / 400))
        if random.random() < chance:
            for alpha in self.alphas["in_research"]:
                alpha.weeks_remaining += 1
            if self.infra_team:
                for m in self.infra_team:
                    m.happiness = max(0, m.happiness - 1)
            self.events_queue.append(Event(
                "Infra Outage",
                "A systems outage slowed research by a week. Stronger infra and a happy infra team reduce this risk.",
                []
            ))
            self.log(f"Infra outage hit (resilience {res}). Research delayed.")

    def enqueue_infra_request(self):
        askers = random.sample(self.team, k=min(len(self.team), max(1, len(self.team)//2)))
        requested = random.choice(["compute_level", "data_quality", "devops_tooling", "risk_tools_level"])
        description = f"Team is pushing for {requested.replace('_', ' ')} upgrade to clear blockers."
        choices = [
            {"text": "Approve upgrade", "effect": {"type": "approve_infra", "infra": requested}},
            {"text": "Delay", "effect": {"type": "delay_infra", "infra": requested}},
            {"text": "Reject", "effect": {"type": "reject_infra", "infra": requested}}
        ]
        self.events_queue.append(Event("Infrastructure Ask", description, choices))

    def handle_infra_request(self, action, infra):
        if action == "approve_infra":
            if self.upgrade_infra(infra):
                self.bump_team_happiness(4, "Team thrilled at fast infra approval.")
                return "Upgrade approved"
            else:
                self.bump_team_happiness(-2, "Approval failed due to cash limits.")
                return "Not enough cash for upgrade"
        elif action == "delay_infra":
            self.bump_team_happiness(-1, "Team frustrated by delay.")
            return "Upgrade delayed"
        elif action == "reject_infra":
            self.bump_team_happiness(-4, "Rejection angered the team.")
            return "Upgrade rejected"
        return "No action"

    def avg_team_happiness(self):
        if not self.team:
            return None
        return sum(q.happiness for q in self.team) / len(self.team)

    def avg_team_skill(self):
        if not self.team:
            return None
        return sum(q.skill for q in self.team) / len(self.team)

    def bump_team_happiness(self, delta, reason=None):
        if not self.team or delta == 0:
            return
        for q in self.team:
            q.happiness = max(0, min(100, q.happiness + delta))
            q.loyalty = max(0, min(100, q.loyalty + (delta // 2 if delta > 0 else delta)))
        if reason:
            self.log(reason)

    def maybe_team_meeting(self):
        """Occasional team/infra sync that depends on morale."""
        if not self.team:
            return
        if random.random() > 0.25:  # roughly one meeting every ~4 weeks
            return
        avg = self.avg_team_happiness()
        if avg is None:
            return

        if avg >= 70:
            self.player.gain_xp(60)
            self.events_queue.append(Event(
                "Strategy Council",
                "The desk jammed on new ideas, infra and quant leads aligned, and you walked away with sharper plans. XP gained.",
                []
            ))
            self.log("Team harmony unlocked fresh ideas. +60 XP.")
        elif avg >= 45:
            self.events_queue.append(Event(
                "Planning Session",
                "Mixed feedback and a pile of asks for infra and data. No crisis, but expectations are rising.",
                []
            ))
            self.log("Planning session surfaced competing priorities. Keep morale healthy to gain momentum.")
        else:
            hit = 10
            self.player.job_security -= hit
            for q in self.team:
                q.loyalty = max(0, q.loyalty - 2)
            self.events_queue.append(Event(
                "Contentious Town Hall",
                "Frustrated quants and infra leads argued over priorities. Management noticed the chaos. Job security fell.",
                []
            ))
            self.log(f"Team discord spilled into a meeting. Job security -{hit}. Fix morale fast.")
            self.player.reputation_management = max(0, self.player.reputation_management - 2)

    def calculate_research_duration(self, base_weeks):
        team_bonus = 0.05 * len(self.team)
        infra_bonus = 0.05 * (self.infrastructure.data_quality - 1)
        compute_bonus = 0.03 * (self.infrastructure.compute_level - 1)
        reduction = min(0.5, team_bonus + infra_bonus + compute_bonus)
        multiplier = 1 - reduction

        # Workload penalty: too many projects per quant slows progress
        if self.team:
            load = (len(self.alphas["in_research"]) + len(self.risk_research)) / len(self.team)
            if load > 1:
                multiplier *= (1 + 0.15 * (load - 1))

        # Morale factor: happier teams work faster, unhappy teams slower
        avg_h = self.avg_team_happiness()
        if avg_h is not None:
            if avg_h >= 75:
                multiplier *= 0.9
            elif avg_h <= 40:
                multiplier *= 1.1

        effective = max(1, int(round(base_weeks * multiplier)))
        return effective

    def alpha_handicap(self):
        return max(1.0, getattr(self.player, "alpha_difficulty", 1.0))

    def apply_alpha_success_penalty(self, success_prob):
        adjusted = success_prob / self.alpha_handicap()
        return max(0.05, min(0.95, adjusted))

    def apply_alpha_penalty_to_stats(self, alpha):
        penalty = self.alpha_handicap()
        alpha.base_expected_return *= 1.0 / penalty
        alpha.current_expected_return *= 1.0 / penalty
        alpha.decay_rate *= penalty

    def is_market_neutral_enabled(self):
        return self.risk_model.market_neutral or self.infrastructure.risk_tools_level >= 2

    def is_factor_neutral_enabled(self):
        return self.risk_model.factor_neutral or self.infrastructure.risk_tools_level >= 3

    def is_market_shielded(self):
        return self.is_market_neutral_enabled() or self.is_factor_neutral_enabled()

    def super_alpha_chance(self, avg_skill, avg_happy):
        base = 0.02
        base += (avg_skill or 50) * 0.0002
        base += max(0, (avg_happy or 50) - 50) * 0.0001
        base += 0.01 * max(0, self.infrastructure.data_quality - 1)
        base += 0.005 * len(self.infra_team)
        base = min(0.2, base)
        penalty = self.alpha_handicap()
        return max(0.0, base / penalty)

    def alpha_resilience(self, avg_skill, avg_happy):
        base = 0.2
        base += (avg_skill or 50) * 0.002
        base += max(0, (avg_happy or 50) - 50) * 0.002
        base += 0.05 * max(0, self.infrastructure.devops_tooling - 1)
        base += 0.05 * max(0, self.infrastructure.risk_tools_level - 1)
        if self.infra_team:
            base += 0.05
        penalty = self.alpha_handicap()
        base = base / penalty
        return max(0.05, min(0.9, base))

    def pay_weekly_salaries(self):
        total = 0
        if self.team:
            total += sum(q.salary for q in self.team) / 52
        if self.infra_team:
            total += sum(getattr(m, "salary", 80_000) for m in self.infra_team) / 52
        if total > 0:
            self.player.cash -= total
            self.player.aum -= total
            self.log(f"Payroll: Paid ${total:,.0f} in salaries.")
        return total

    def pay_year_end_bonuses(self):
        if self.week != 52:
            return 0
        bonuses = 0
        if self.player.yearly_pnl <= 0:
            self.log("No bonuses paid due to negative or zero yearly PnL.")
            return 0
        for q in self.team:
            if q.happiness >= 80:
                rate = 0.10
            elif q.happiness >= 50:
                rate = 0.05
            else:
                rate = 0.0
            bonuses += q.salary * rate
        for m in self.infra_team:
            base_salary = getattr(m, "salary", 80_000)
            if m.happiness >= 80:
                rate = 0.06
            elif m.happiness >= 50:
                rate = 0.03
            else:
                rate = 0.0
            bonuses += base_salary * rate
        if bonuses > 0:
            self.player.cash -= bonuses
            self.player.aum -= bonuses
            self.log(f"Year-end bonuses paid: ${bonuses:,.0f}.")
        return bonuses

    def log_week_story(self, weekly_pnl, weekly_pay, bonus_pay, market_ret):
        morale = self.avg_team_happiness()
        resilience = self.resilience_score()
        story_bits = [
            f"Regime {self.environment['regime']}",
            f"Resilience {resilience}",
            f"PnL {weekly_pnl:,.0f}",
            f"Payroll {weekly_pay:,.0f}",
            f"RepQ {self.player.reputation_quants:.0f}",
            f"RepM {self.player.reputation_management:.0f}",
        ]
        if bonus_pay:
            story_bits.append(f"Bonuses {bonus_pay:,.0f}")
        if morale is not None:
            story_bits.append(f"Avg morale {morale:.0f}")
        story_bits.append(f"Market move {market_ret:.3f}")
        self.log("Story: " + " | ".join(story_bits))

    def update_drawdowns(self):
        # Track peak AUM and compute drawdowns
        self.player.peak_aum = max(self.player.peak_aum, self.player.aum)
        if self.player.peak_aum > 0:
            dd = (self.player.peak_aum - self.player.aum) / self.player.peak_aum
            self.player.current_drawdown = dd
            self.player.max_drawdown = max(self.player.max_drawdown, dd)

    def management_reaction(self, weekly_pnl):
        # Management reacts to drawdowns and bad streaks
        dd = self.player.current_drawdown
        if self.player.startup_grace_weeks > 0:
            # Grace period: lighter scrutiny
            if dd > 0.3:
                self.player.reputation_management = max(0, self.player.reputation_management - 1)
            return
        if dd > 0.25:
            penalty = 5
            self.player.job_security -= penalty
            self.player.reputation_management = max(0, self.player.reputation_management - 4)
            self.bump_team_happiness(-3, "Management alarm spooked the desk.")
            self.events_queue.append(Event("Management Alarm", "Severe drawdown triggered scrutiny. Fix risk or face termination.", []))
            self.log(f"Management Alarm: drawdown {dd:.1%}, job security -{penalty}.")
        elif dd > 0.15:
            self.player.reputation_management = max(0, self.player.reputation_management - 2)
        if weekly_pnl < -100_000:
            drop = 3
            self.player.job_security -= drop
            self.player.reputation_management = max(0, self.player.reputation_management - 2)
            self.bump_team_happiness(-2, "Weekly loss eroded confidence.")
            self.log(f"Management unhappy with weekly loss {weekly_pnl:,.0f}. Job security -{drop}.")

    def check_reset_offer(self):
        if self.player.reset_offer_used or self.player.reset_offer_active:
            return
        if getattr(self.player, "reset_offer_cooldown", 0) > 0:
            self.player.reset_offer_cooldown -= 1
            return

        severe_drawdown = self.player.current_drawdown >= 0.35
        capital_crushed = self.player.aum <= self.player.starting_aum * 0.1
        if not (severe_drawdown or capital_crushed):
            return

        desc = (
            "Competing hedge fund offers you $50MM to walk away from this drawdown and reboot. "
            "Accepting resets PnL/AUM but unlocks a tougher market where alpha generation is harder."
        )
        choices = [
            {"text": "Take the offer, reboot with $50MM", "effect": {"type": "reset_offer", "decision": "accept"}},
            {"text": "Stay and grind it out", "effect": {"type": "reset_offer", "decision": "decline"}},
        ]
        self.events_queue.append(Event("Competing Hedge Fund Call", desc, choices))
        self.player.reset_offer_active = True

    def handle_reset_offer(self, decision):
        if self.events_queue:
            self.clear_event()
        self.player.reset_offer_active = False

        if decision == "accept":
            self.apply_reset_hard_mode()
            return "Offer accepted. Fresh $50MM, but alpha discovery got tougher."

        # Decline: short cooldown to avoid spamming, but keep option alive if pain persists later
        self.player.reset_offer_cooldown = max(6, getattr(self.player, "reset_offer_cooldown", 0))
        self.log("You declined the rival fund lifeline. Pressure remains high.")
        return "Offer declined."

    def apply_reset_hard_mode(self):
        self.player.reset_offer_used = True
        self.player.reset_offer_cooldown = 0
        self.player.alpha_difficulty = max(self.player.alpha_difficulty, 1.35)

        # Reset capital stack
        self.player.cash = 1_000_000
        self.player.aum = 50_000_000
        self.player.pnl_history = []
        self.player.yearly_pnl = 0.0
        self.player.current_drawdown = 0.0
        self.player.max_drawdown = 0.0
        self.player.peak_aum = self.player.aum
        self.player.rolling_sharpe = 0.0
        self.player.starting_aum = self.player.aum

        # Clean positions and brace for tougher alpha quality
        self.portfolio.positions = []
        self.apply_alpha_penalty_to_all()

        # Mixed reputation/journey reset
        self.player.job_security = max(70, self.player.job_security)
        self.player.reputation_management = max(0, self.player.reputation_management - 6)
        self.player.reputation_quants = max(0, self.player.reputation_quants - 3)

        self.bump_team_happiness(-4, "Desk rattled by wholesale reboot. Confidence shaken.")
        self.events_queue.append(Event(
            "Fresh Start: Hard Mode",
            "You took the rival fund's $50MM reboot. PnL reset; alpha research now faces headwinds and decay hits harder.",
            [{"text": "Continue", "effect": "continue"}]
        ))
        self.log("You accepted the $50MM rival offer. PnL reset; alpha discovery handicap applied.")

    def apply_alpha_penalty_to_all(self):
        for group in self.alphas.values():
            for alpha in group:
                self.apply_alpha_penalty_to_stats(alpha)

    def minimum_salary_for_skill(self, skill):
        return 40_000 + int(skill * 1_200)

    # Mini-game: Guess that Sharpe
    def generate_sharpe_challenge(self):
        from minigames.guess_sharpe import GuessSharpeGame
        self.active_minigame_instance = GuessSharpeGame(rounds=5)
        game_data = self.active_minigame_instance.start()

        self.current_mini_game = {
            "type": "guess_sharpe",
            "data": game_data
        }
        # Send leaderboard snapshot for UI
        game_data["leaderboard"] = self.player.minigame_stats.get("guess_sharpe_leaderboard", [])
        return self.current_mini_game["data"]

    def submit_sharpe_guess(self, guess):
        if not hasattr(self, 'active_minigame_instance') or not self.active_minigame_instance:
            return {"error": "No active game"}
        
        result = self.active_minigame_instance.submit(guess)
        if result["game_over"]:
            avg_error = sum(r["error"] for r in result["history"]) / len(result["history"])
            final_score = result["cumulative_score"]
            xp_gain = max(25, int(final_score / 20))
            self.player.gain_xp(xp_gain)
            self.log(f"Sharpe Challenge complete. Score {final_score} (+{xp_gain} XP).")
            self.player.record_guess_sharpe_score(final_score, avg_error, self.week, self.year)
            result["leaderboard"] = self.player.minigame_stats["guess_sharpe_leaderboard"]
            self.current_mini_game = None
            self.active_minigame_instance = None
        return result

    # Mini-game: Market Making
    def start_market_making(self):
        from minigames.market_making import MarketMakingGame
        self.active_minigame_instance = MarketMakingGame()
        game_data = self.active_minigame_instance.start()
        
        self.current_mini_game = {
            "type": "market_making",
            "data": game_data
        }
        return self.current_mini_game["data"]

    def submit_market_making(self, spread):
        if not hasattr(self, 'active_minigame_instance') or not self.active_minigame_instance:
            return {"error": "No active game"}
            
        result = self.active_minigame_instance.submit(spread)
        
        if result["game_over"]:
            xp_gain = result.get("xp_gain", 0)
            if xp_gain > 0:
                self.player.gain_xp(xp_gain)
                self.log(f"Market Making Result: +{xp_gain} XP")
            
            self.current_mini_game = None
            self.active_minigame_instance = None
            
        return result

    # Mini-game: Market Trivia
    def start_market_trivia(self):
        from minigames.market_trivia import MarketTriviaGame
        self.active_minigame_instance = MarketTriviaGame()
        game_data = self.active_minigame_instance.start()

        self.current_mini_game = {
            "type": "market_trivia",
            "data": game_data
        }
        return self.current_mini_game["data"]

    def submit_market_trivia(self, choice_index):
        if not hasattr(self, 'active_minigame_instance') or not self.active_minigame_instance:
            return {"error": "No active game"}
        result = self.active_minigame_instance.submit(choice_index)
        if result.get("game_over"):
            xp = 0
            if result["score"] >= 80:
                xp = 50
            elif result["score"] >= 40:
                xp = 30
            elif result["score"] >= 20:
                xp = 30
            self.player.gain_xp(xp)
            if xp > 0:
                self.log(f"Trivia session complete. Score {result['score']} (+{xp} XP).")
            else:
                self.log(f"Trivia session complete. Score {result['score']} (no XP).")
            self.current_mini_game = None
            self.active_minigame_instance = None
        return result

class Player:
    def __init__(self):
        self.cash = 1_000_000
        self.aum = 50_000_000
        self.pnl_history = []
        self.current_drawdown = 0.0
        self.max_drawdown = 0.0
        self.peak_aum = self.aum
        self.rolling_sharpe = 0.0
        self.reputation_management = 50
        self.reputation_risk = 50
        self.relationship_quants = 50
        self.job_security = 100
        
        # Gamification
        self.level = 1
        self.xp = 0
        self.xp_to_next_level = 1000
        self.ability_points = 0
        self.abilities = [] # List of strings
        self.reputation_infra = 50
        self.reputation_quants = 50
        self.minigame_stats = {
            "guess_sharpe_leaderboard": []
        }
        self.yearly_pnl = 0.0
        self.startup_grace_weeks = 4
        self.starting_aum = self.aum
        self.alpha_difficulty = 1.0  # >=1.0, higher = harder to land/keep good alphas
        self.reset_offer_used = False
        self.reset_offer_active = False
        self.reset_offer_cooldown = 0

    def gain_xp(self, amount):
        self.xp += amount
        if self.xp >= self.xp_to_next_level:
            self.level_up()

    def level_up(self):
        self.level += 1
        self.xp -= self.xp_to_next_level
        self.xp_to_next_level = int(self.xp_to_next_level * 1.2)
        self.ability_points += 1
        # We could trigger an event here, but for now just state update is fine

    def record_guess_sharpe_score(self, score, avg_error, week, year):
        board = self.minigame_stats.get("guess_sharpe_leaderboard", [])
        board.append({
            "score": score,
            "avg_error": avg_error,
            "week": week,
            "year": year
        })
        # Keep top 5 by score
        board.sort(key=lambda x: x["score"], reverse=True)
        self.minigame_stats["guess_sharpe_leaderboard"] = board[:5]
        
    def to_dict(self):
        return self.__dict__

class Quant:
    def __init__(self, name, skill, salary):
        self.name = name
        self.skill = skill # 0-100
        self.happiness = 70 # 0-100
        self.salary = salary
        self.workload = 0 # 0-100
        self.loyalty = 50 # 0-100
        self.avatar = "robot" # Default placeholder

    def to_dict(self):
        return self.__dict__

class Infrastructure:
    def __init__(self):
        self.compute_level = 1
        self.data_quality = 1
        self.devops_tooling = 1
        self.risk_tools_level = 1
        self.optimization_tool_level = 1

    def to_dict(self):
        return self.__dict__

class RiskModel:
    def __init__(self):
        self.level = 1
        self.market_neutral = False
        self.factor_neutral = False

    def to_dict(self):
        return self.__dict__

class InfraSpecialist:
    def __init__(self, name, skill):
        self.name = name
        self.skill = skill
        self.happiness = 70
        self.loyalty = 50
        self.role = "Infra"
        self.salary = 80_000

    def to_dict(self):
        return self.__dict__

class RiskResearch:
    def __init__(self, name, duration):
        self.name = name
        self.duration = duration
        self.weeks_remaining = duration

    def to_dict(self):
        return self.__dict__

class Portfolio:
    def __init__(self):
        self.positions = [] # List of dicts {alpha_id, weight}

    def to_dict(self):
        return self.__dict__

class AlphaStrategy:
    def __init__(self, name, style, duration):
        self.id = f"alpha_{random.randint(1000,9999)}"
        self.name = name
        self.style = style
        self.status = "in_research"
        self.research_duration = duration
        self.weeks_remaining = duration
        self.base_expected_return = 0.0
        self.current_expected_return = 0.0
        self.volatility = 0.0
        self.factor_exposures = {}
        self.capacity = 0
        self.decay_rate = 0.01
        self.beta = 1.0

    def decay(self, regime):
        self.current_expected_return *= (1 - self.decay_rate)
        # Regime penalty could be added here

    def to_dict(self):
        return self.__dict__

class Event:
    def __init__(self, title, description, choices):
        self.title = title
        self.description = description
        self.choices = choices # List of dicts {text, effect_code}

    def to_dict(self):
        return self.__dict__

# Import utils at the end to avoid circular imports if any (though here it's fine)
from utils import simulate_alpha_return, generate_market_return
