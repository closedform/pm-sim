const state = {
    data: null
};
let sharpeSession = null;

document.addEventListener('DOMContentLoaded', () => {
    console.log("PM Simulator App Initialized v3");
    initTabs();
    fetchState();
    fetchSavesList();

    document.getElementById('next-turn-btn').addEventListener('click', nextTurn);
    document.getElementById('start-research-btn').addEventListener('click', startResearch);
    document.getElementById('hire-btn').addEventListener('click', hireQuant);
    document.getElementById('close-event-btn').addEventListener('click', closeEventModal);
    document.getElementById('hire-skill').addEventListener('input', updateSalaryHint);
    document.getElementById('hire-salary').addEventListener('input', updateSalaryHint);
    document.getElementById('research-duration').addEventListener('change', updateResearchDurationHint);
    document.getElementById('save-btn').addEventListener('click', saveGame);
    document.getElementById('load-btn').addEventListener('click', loadGame);
    const infraBtn = document.getElementById('hire-infra-btn');
    if (infraBtn) infraBtn.addEventListener('click', hireInfra);
    // Fire actions (delegated via buttons)
    document.body.addEventListener('click', (e) => {
        const target = e.target;
        if (target && target.dataset && target.dataset.fireType) {
            fireStaff(target.dataset.fireType, target.dataset.name);
        }
    });
});

function initTabs() {
    const tabs = document.querySelectorAll('.nav-btn');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            console.log(`Tab clicked: ${tab.dataset.tab}`);
            const targetId = `${tab.dataset.tab}-tab`;
            const targetContent = document.getElementById(targetId);

            if (!targetContent) {
                console.error(`Tab content not found: ${targetId}`);
                return;
            }

            document.querySelectorAll('.nav-btn').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

            tab.classList.add('active');
            targetContent.classList.add('active');
        });
    });
}

async function fetchState() {
    const response = await fetch('/api/state');
    const data = await response.json();
    updateUI(data);
}

async function nextTurn() {
    const response = await fetch('/api/next_turn', { method: 'POST' });
    const data = await response.json();
    updateUI(data.state);
}

async function startResearch() {
    const style = document.getElementById('research-style').value;
    const duration = parseInt(document.getElementById('research-duration').value);

    const response = await fetch('/api/action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type: 'start_research', style, duration })
    });
    const data = await response.json();
    updateUI(data.state);
}

async function hireQuant() {
    const name = document.getElementById('hire-name').value;
    const skill = parseInt(document.getElementById('hire-skill').value);
    const salary = parseInt(document.getElementById('hire-salary').value);

    if (!name) return;

    const response = await fetch('/api/action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type: 'hire_quant', name, skill, salary })
    });
    const data = await response.json();
    if (data.status === 'error') {
        alert(data.message);
    }
    if (data.state) {
        updateUI(data.state);
    }
}

function updateUI(data) {
    state.data = data;

    // Top Bar
    document.getElementById('week-display').innerText = data.week;
    document.getElementById('year-display').innerText = data.year;
    document.getElementById('cash-display').innerText = formatMoney(data.player.cash);
    document.getElementById('aum-display').innerText = formatMoney(data.player.aum);
    document.getElementById('sharpe-display').innerText = data.player.rolling_sharpe.toFixed(2);

    // Level & XP
    document.getElementById('level-display').innerText = data.player.level;
    const xpPct = (data.player.xp / data.player.xp_to_next_level) * 100;
    document.getElementById('xp-bar-fill').style.width = `${xpPct}%`;

    // Dashboard
    document.getElementById('dd-display').innerText = (data.player.current_drawdown * 100).toFixed(1) + '%';
    document.getElementById('max-dd-display').innerText = (data.player.max_drawdown * 100).toFixed(1) + '%';
    document.getElementById('regime-display').innerText = data.environment.regime;
    document.getElementById('risk-level-display').innerText = data.risk_model.level;
    document.getElementById('quant-count-display').innerText = data.team.length;
    const avgHappy = data.avg_team_happiness;
    const happyDisplay = document.getElementById('happiness-display');
    if (avgHappy === null || avgHappy === undefined) {
        happyDisplay.innerText = '--';
        happyDisplay.style.color = '';
    } else {
        happyDisplay.innerText = avgHappy.toFixed(0);
        happyDisplay.style.color = avgHappy < 35 ? '#ff5252' : '';
    }

    // Team
    const teamList = document.getElementById('team-list');
    teamList.innerHTML = '';
    data.team.forEach(quant => {
        const li = document.createElement('li');
        li.className = 'quant-item';

        // Placeholder avatars mapping
        const avatarMap = {
            'wizard': '🧙‍♂️',
            'robot': '🤖',
            'cat': '🐱',
            'alien': '👽'
        };
        const avatarIcon = avatarMap[quant.avatar] || '👤';

        li.innerHTML = `
            <div class="quant-avatar">${avatarIcon}</div>
            <div>
                <strong>${quant.name}</strong><br>
                <span style="color: #aaa; font-size: 0.8rem;">Skill: ${quant.skill} | Happiness: ${quant.happiness}</span>
            </div>
            <button class="secondary-btn" data-fire-type="quant" data-name="${quant.name}">Fire</button>
        `;
        teamList.appendChild(li);
    });

    // Research
    const researchList = document.getElementById('research-list');
    researchList.innerHTML = '';
    data.alphas.in_research.forEach(alpha => {
        const li = document.createElement('li');
        li.innerText = `${alpha.name} (${alpha.style}) - ${alpha.weeks_remaining} weeks left`;
        researchList.appendChild(li);
    });

    // Risk research
    const riskList = document.getElementById('risk-research-list');
    if (riskList) {
        riskList.innerHTML = '';
        if (data.risk_research && data.risk_research.length > 0) {
            data.risk_research.forEach(r => {
                const li = document.createElement('li');
                li.innerText = `${r.name} - ${r.weeks_remaining} weeks left`;
                riskList.appendChild(li);
            });
        } else {
            riskList.innerHTML = '<li>No active risk-model projects.</li>';
        }
    }

    const completedList = document.getElementById('completed-alphas-list');
    completedList.innerHTML = '';
    data.alphas.stored_for_ensemble.forEach(alpha => {
        const li = document.createElement('li');
        li.innerText = `${alpha.name} - Exp Ret: ${(alpha.base_expected_return * 100).toFixed(1)}%`;
        completedList.appendChild(li);
    });

    // Portfolio
    const portfolioContainer = document.getElementById('portfolio-container');
    portfolioContainer.innerHTML = '';

    // Combine live alphas and ensembles
    const allAlphas = [...data.alphas.live, ...data.alphas.ensembles];

    if (allAlphas.length === 0) {
        portfolioContainer.innerHTML = '<p>No live alphas. Go to Research to create some.</p>';
    } else {
        allAlphas.forEach(alpha => {
            const div = document.createElement('div');
            div.className = 'control-group';
            div.innerHTML = `
                <label>${alpha.name} (Exp Ret: ${(alpha.current_expected_return * 100).toFixed(1)}%)</label>
                <input type="number" class="alpha-weight" data-id="${alpha.id}" value="${getWeight(alpha.id, data.portfolio)}" step="0.01" min="0" max="1">
            `;
            portfolioContainer.appendChild(div);
        });
    }

    // Infra
    const infraList = document.getElementById('infra-list');
    infraList.innerHTML = '';
    Object.entries(data.infrastructure).forEach(([key, value]) => {
        const li = document.createElement('li');
        li.innerHTML = `
            <span>${formatInfraName(key)}: Level ${value}</span>
            <button onclick="upgradeInfra('${key}')" class="secondary-btn">Upgrade ($50k)</button>
        `;
        infraList.appendChild(li);
    });
    // Infra team
    const infraTeamList = document.getElementById('infra-team-list');
    if (infraTeamList) {
        infraTeamList.innerHTML = '';
        if (data.infra_team && data.infra_team.length > 0) {
            data.infra_team.forEach(member => {
                const li = document.createElement('li');
                li.innerHTML = `${member.name} — Skill ${member.skill} | Happiness ${member.happiness} <button class="secondary-btn" data-fire-type="infra" data-name="${member.name}">Fire</button>`;
                infraTeamList.appendChild(li);
            });
        } else {
            infraTeamList.innerHTML = '<li>No infra specialists hired yet.</li>';
        }
        const pendingList = document.getElementById('pending-infra-list');
        if (pendingList) {
            pendingList.innerHTML = '';
            if (data.pending_infra && data.pending_infra.length > 0) {
                data.pending_infra.forEach(m => {
                    const li = document.createElement('li');
                    li.innerHTML = `${m.name} — Skill ${m.skill} | ETA ${m.onboarding_weeks} wk(s)`;
                    pendingList.appendChild(li);
                });
            } else {
                pendingList.innerHTML = '<li>No pending infra hires.</li>';
            }
        }
    }

    // Events
    if (data.events_queue.length > 0) {
        showEvent(data.events_queue[0]);
    }

    // Terminal
    updateTerminal(data.message_log);

    // PnL Chart
    updatePnLChart(data.player.pnl_history);

    // Derived hints
    updateSalaryHint();
    updateResearchDurationHint();
}

function updateTerminal(logs) {
    const terminal = document.getElementById('terminal-output');

    // Get existing logs to avoid duplicates (simple check)
    const existing = Array.from(terminal.children).map(c => c.innerText);

    logs.forEach(log => {
        if (!existing.includes(log)) {
            const div = document.createElement('div');
            div.className = 'log-line';
            div.innerText = log;
            // Insert before the first child (visual bottom due to column-reverse)
            // Wait, column-reverse means first child is at bottom.
            // So appending adds to top.
            // We want newest at bottom.
            // Standard terminal: Newest at bottom.
            // If flex-direction: column-reverse, then:
            // Container Bottom
            // Child 1
            // Child 2
            // Container Top

            // If we want newest at bottom, we should use standard column and scroll to bottom.
            // But the CSS uses column-reverse.
            // Let's stick to the CSS.
            // If column-reverse, the "Start" of the flex axis is the bottom.
            // So Child 1 is at the bottom.
            // Child 2 is above it.
            // So to add a NEW log at the bottom, we need to prepend it?
            // No, if we want newest at bottom, and it's column-reverse...
            // Visual:
            // [Log 3] (Newest)
            // [Log 2]
            // [Log 1] (Oldest)
            // This is "Newest at Top".

            // The user screenshot shows:
            // > SYSTEM_LOG_
            // DEBUG: Switching...
            // System initialized.

            // It seems "System initialized" (Oldest) is at the bottom?
            // No, "System initialized" is below "DEBUG".
            // So DEBUG (Newest) is at the Top.

            // Let's just append.
            terminal.appendChild(div);
        }
    });
}

let pnlChart = null;

function updatePnLChart(history) {
    const ctx = document.getElementById('pnl-chart').getContext('2d');
    const labels = Array.from({ length: history.length }, (_, i) => `W${i + 1}`);
    const cumPnL = [];
    let sum = 0;
    history.forEach(val => {
        sum += val;
        cumPnL.push(sum);
    });

    if (pnlChart) {
        pnlChart.data.labels = labels;
        pnlChart.data.datasets[0].data = cumPnL;
        pnlChart.update();
    } else {
        pnlChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Cumulative PnL',
                    data: cumPnL,
                    borderColor: '#00d09c',
                    backgroundColor: 'rgba(0, 208, 156, 0.05)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0,
                    pointHoverRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        callbacks: {
                            label: function (context) {
                                return formatMoney(context.raw);
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        display: false,
                        grid: { display: false }
                    },
                    y: {
                        grid: { color: '#333' },
                        ticks: {
                            color: '#a0a0a0',
                            callback: function (value) {
                                return '$' + (value / 1000000).toFixed(1) + 'M';
                            }
                        }
                    }
                },
                interaction: {
                    mode: 'nearest',
                    axis: 'x',
                    intersect: false
                }
            }
        });
    }
}

function getWeight(alphaId, portfolio) {
    const pos = portfolio.positions.find(p => p.alpha_id === alphaId);
    return pos ? pos.weight : 0;
}

function formatInfraName(key) {
    return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

async function upgradeInfra(type) {
    const response = await fetch('/api/action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type: 'upgrade_infra', infra_type: type })
    });
    const data = await response.json();
    updateUI(data.state);
}

async function updatePortfolio() {
    const inputs = document.querySelectorAll('.alpha-weight');
    const positions = [];
    inputs.forEach(input => {
        const weight = parseFloat(input.value);
        if (weight > 0) {
            positions.push({ alpha_id: input.dataset.id, weight: weight });
        }
    });

    const response = await fetch('/api/action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type: 'update_portfolio', positions })
    });
    const data = await response.json();
    updateUI(data.state);
}

// Add event listener for update portfolio button
document.getElementById('update-portfolio-btn').addEventListener('click', updatePortfolio);

// Mini-game listeners
document.getElementById('start-sharpe-game-btn').addEventListener('click', startSharpeGame);
document.getElementById('submit-guess-btn').addEventListener('click', submitSharpeGuess);
document.getElementById('close-minigame-btn').addEventListener('click', closeMinigameModal);
document.getElementById('start-trivia-game-btn').addEventListener('click', startTriviaGame);
document.getElementById('close-trivia-btn').addEventListener('click', closeTriviaModal);

let sharpeChart = null;

async function startSharpeGame() {
    const response = await fetch('/api/action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type: 'start_mini_game' })
    });
    const data = await response.json();

    if (data.status === 'ok') {
        document.getElementById('minigame-modal').classList.remove('hidden');
        document.getElementById('minigame-result').classList.add('hidden');
        document.getElementById('sharpe-guess').value = '';
        sharpeSession = {
            round: data.game_data.round,
            total_rounds: data.game_data.total_rounds,
            score: data.game_data.score,
            leaderboard: data.game_data.leaderboard || []
        };
        updateSharpeHUD();
        renderSharpeChart(data.game_data.cumulative);
        renderSharpeLeaderboard(sharpeSession.leaderboard);
    }
}

function renderSharpeChart(dataPoints) {
    const ctx = document.getElementById('sharpe-chart').getContext('2d');

    if (sharpeChart) {
        sharpeChart.destroy();
    }

    sharpeChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: Array.from({ length: dataPoints.length }, (_, i) => i + 1),
            datasets: [{
                label: 'Cumulative Return',
                data: dataPoints,
                borderColor: '#00d09c',
                backgroundColor: 'rgba(0, 208, 156, 0.1)',
                borderWidth: 2,
                tension: 0.1,
                pointRadius: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: { display: false },
                y: {
                    grid: { color: '#333' },
                    ticks: { color: '#a0a0a0' }
                }
            }
        }
    });
}

async function submitSharpeGuess() {
    const guess = parseFloat(document.getElementById('sharpe-guess').value);
    if (isNaN(guess)) return;

    const response = await fetch('/api/action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type: 'submit_mini_game', guess: guess })
    });
    const data = await response.json();

    const resultDiv = document.getElementById('minigame-result');
    const resultText = document.getElementById('result-text');

    resultDiv.classList.remove('hidden');

    const res = data.result;
    const scoreLine = `Points: +${res.points} | Total Score: ${res.cumulative_score}`;
    resultText.innerHTML = `
        True Sharpe: ${res.true_sharpe.toFixed(2)}<br>
        Your guess error: ${res.error.toFixed(2)}<br>
        ${scoreLine}<br>
        Reward: ${res.reward}
    `;

    if (res.game_over) {
        if (res.leaderboard) {
            renderSharpeLeaderboard(res.leaderboard);
        }
        document.getElementById('sharpe-round').innerText = res.round_finished;
        document.getElementById('sharpe-score').innerText = res.cumulative_score;
        document.getElementById('sharpe-total').innerText = sharpeSession ? sharpeSession.total_rounds : res.round_finished;
        updateUI(data.state);
    } else if (res.next_round) {
        sharpeSession.round = res.next_round.round;
        sharpeSession.total_rounds = res.next_round.total_rounds;
        sharpeSession.score = res.cumulative_score;
        updateSharpeHUD();
        renderSharpeChart(res.next_round.cumulative);
        document.getElementById('sharpe-guess').value = '';
    }
}

function closeMinigameModal() {
    document.getElementById('minigame-modal').classList.add('hidden');
}

// Trivia
let triviaSession = null;

async function startTriviaGame() {
    const response = await fetch('/api/action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type: 'start_trivia_game' })
    });
    const data = await response.json();
    if (data.status === 'ok') {
        triviaSession = data.game_data;
        renderTriviaQuestion(triviaSession);
        document.getElementById('trivia-modal').classList.remove('hidden');
        document.getElementById('trivia-result').classList.add('hidden');
        document.getElementById('close-trivia-btn').classList.add('hidden');
    }
}

function renderTriviaQuestion(payload) {
    if (!payload) return;
    document.getElementById('trivia-round').innerText = payload.index;
    document.getElementById('trivia-total').innerText = payload.total;
    document.getElementById('trivia-score').innerText = triviaSession ? triviaSession.score : payload.score;
    document.getElementById('trivia-question').innerText = payload.prompt;
    const list = document.getElementById('trivia-options');
    list.innerHTML = '';
    payload.options.forEach((opt, idx) => {
        const li = document.createElement('li');
        const btn = document.createElement('button');
        btn.className = 'secondary-btn';
        btn.style.width = '100%';
        btn.innerText = opt;
        btn.onclick = () => submitTriviaAnswer(idx);
        li.appendChild(btn);
        list.appendChild(li);
    });
}

async function submitTriviaAnswer(choice) {
    const response = await fetch('/api/action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type: 'submit_trivia_game', choice })
    });
    const data = await response.json();
    const res = data.result;
    if (res.error) return;
    triviaSession.score = res.score;
    const resultDiv = document.getElementById('trivia-result');
    resultDiv.classList.remove('hidden');
    resultDiv.innerText = res.correct ? 'Correct!' : `Incorrect. Answer was option ${res.answer_index + 1}.`;
    if (res.game_over) {
        updateUI(data.state);
        document.getElementById('trivia-score').innerText = res.score;
        document.getElementById('trivia-options').innerHTML = '';
        resultDiv.innerText += ` Reward: ${res.reward}`;
        document.getElementById('close-trivia-btn').classList.remove('hidden');
    } else if (res.next_question) {
        renderTriviaQuestion(res.next_question);
    }
}

function closeTriviaModal() {
    document.getElementById('trivia-modal').classList.add('hidden');
}

// MM Game listeners
document.getElementById('start-mm-game-btn').addEventListener('click', startMMGame);
document.getElementById('submit-mm-btn').addEventListener('click', submitMMAction);
document.getElementById('close-mm-btn').addEventListener('click', closeMMModal);

async function startMMGame() {
    const response = await fetch('/api/action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type: 'start_mm_game' })
    });
    const data = await response.json();

    if (data.status === 'ok') {
        document.getElementById('mm-game-modal').classList.remove('hidden');
        document.getElementById('mm-result').classList.add('hidden');
        document.getElementById('mm-log').innerHTML = '';
        updateMMUI(data.game_data);
    }
}

async function submitMMAction() {
    const spread = parseFloat(document.getElementById('mm-spread').value);
    if (isNaN(spread)) return;

    const response = await fetch('/api/action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type: 'submit_mm_action', spread: spread })
    });
    const data = await response.json();

    updateMMUI(data.result.state);

    if (data.result.game_over) {
        const resultDiv = document.getElementById('mm-result');
        const resultText = document.getElementById('mm-result-text');
        resultDiv.classList.remove('hidden');
        const xpText = data.result.xp_gain ? `<br>XP: +${data.result.xp_gain}` : '';
        resultText.innerHTML = `Game Over!<br>Final PnL: ${data.result.state.pnl.toFixed(2)}<br>Reward: ${data.result.reward}${xpText}`;
        updateUI(data.state); // Update main game state for rewards
    }
}

function updateMMUI(state) {
    document.getElementById('mm-round').innerText = state.round;
    if (state.max_rounds) {
        document.getElementById('mm-total').innerText = state.max_rounds;
    }
    document.getElementById('mm-price').innerText = state.mid_price.toFixed(2);
    document.getElementById('mm-inventory').innerText = state.inventory;
    document.getElementById('mm-cash').innerText = state.cash.toFixed(2);
    document.getElementById('mm-pnl').innerText = state.pnl.toFixed(2);

    if (state.last_action) {
        const log = document.getElementById('mm-log');
        const entry = document.createElement('div');
        entry.className = 'log-entry';
        const buyText = state.last_action.buy_filled ? '<span style="color:#00d09c">BUY FILLED</span>' : 'Buy Missed';
        const sellText = state.last_action.sell_filled ? '<span style="color:#00d09c">SELL FILLED</span>' : 'Sell Missed';
        entry.innerHTML = `Round ${state.round - 1}: Bid ${state.last_action.bid.toFixed(2)} (${buyText}) | Ask ${state.last_action.ask.toFixed(2)} (${sellText})`;
        log.prepend(entry);
    }
}

function closeMMModal() {
    document.getElementById('mm-game-modal').classList.add('hidden');
}

function showEvent(event) {
    const modal = document.getElementById('event-modal');
    document.getElementById('event-title').innerText = event.title;
    document.getElementById('event-desc').innerText = event.description;

    const choicesContainer = document.getElementById('event-choices');
    choicesContainer.innerHTML = '';

    if (event.choices && event.choices.length > 0) {
        event.choices.forEach(choice => {
            const btn = document.createElement('button');
            btn.className = 'primary-btn';
            btn.innerText = choice.text;
            btn.style.marginRight = '10px';
            btn.onclick = () => handleEventChoice(choice.effect);
            choicesContainer.appendChild(btn);
        });
        document.getElementById('close-event-btn').classList.add('hidden');
    } else {
        document.getElementById('close-event-btn').classList.remove('hidden');
    }

    modal.classList.remove('hidden');
}

async function handleEventChoice(effect) {
    if (effect === 'restart') {
        const response = await fetch('/api/action', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ type: 'restart_game' })
        });
        const data = await response.json();
        updateUI(data.state);
        document.getElementById('event-modal').classList.add('hidden');
    } else if (effect === 'continue') {
        closeEventModal();
    } else if (effect && typeof effect === 'object' && effect.type === 'reset_offer') {
        const response = await fetch('/api/action', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ type: 'handle_reset_offer', decision: effect.decision })
        });
        const data = await response.json();
        if (data.message) {
            console.log(data.message);
        }
        updateUI(data.state);
        document.getElementById('event-modal').classList.add('hidden');
    } else if (effect && typeof effect === 'object' && effect.type && effect.type.includes('infra')) {
        const response = await fetch('/api/action', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ type: 'handle_infra_request', effect })
        });
        const data = await response.json();
        updateUI(data.state);
        document.getElementById('event-modal').classList.add('hidden');
    }
}

function closeEventModal() {
    document.getElementById('event-modal').classList.add('hidden');
    // Call backend to clear event
    fetch('/api/action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type: 'clear_event' })
    });
}

function formatMoney(amount) {
    return '$' + amount.toLocaleString();
}

async function hireInfra() {
    const name = document.getElementById('hire-infra-name').value;
    const skill = parseInt(document.getElementById('hire-infra-skill').value);
    if (!name || isNaN(skill)) return;
    const response = await fetch('/api/action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type: 'hire_infra', name, skill })
    });
    const data = await response.json();
    if (data.message) alert(data.message);
    if (data.state) updateUI(data.state);
}

function updateSharpeHUD() {
    if (!sharpeSession) return;
    document.getElementById('sharpe-round').innerText = sharpeSession.round;
    document.getElementById('sharpe-total').innerText = sharpeSession.total_rounds;
    document.getElementById('sharpe-score').innerText = sharpeSession.score;
}

function renderSharpeLeaderboard(board) {
    const list = document.getElementById('sharpe-leaderboard');
    list.innerHTML = '';
    if (!board || board.length === 0) {
        list.innerHTML = '<li>No scores yet. Finish a full run to post.</li>';
        return;
    }
    board.forEach((entry, idx) => {
        const li = document.createElement('li');
        li.innerText = `${idx + 1}. Score ${entry.score} | Avg error ${entry.avg_error.toFixed(2)} (Y${entry.year} W${entry.week})`;
        list.appendChild(li);
    });
}

function getMinimumSalary(skill) {
    return 40000 + Math.floor(skill * 1200);
}

function updateSalaryHint() {
    const skill = parseInt(document.getElementById('hire-skill').value || '0');
    const salaryInput = document.getElementById('hire-salary');
    const offered = parseInt(salaryInput.value || '0');
    const minSalary = getMinimumSalary(skill);
    const hint = document.getElementById('salary-hint');
    hint.innerText = `Suggested salary for skill ${skill}: ${formatMoney(minSalary)} (offer more for happier hires).`;
    if (offered < minSalary) {
        salaryInput.style.borderColor = '#ff5252';
    } else {
        salaryInput.style.borderColor = '';
    }
}

function updateResearchDurationHint() {
    if (!state.data) return;
    const base = parseInt(document.getElementById('research-duration').value);
    const teamBonus = 0.05 * state.data.team.length;
    const infra = state.data.infrastructure;
    const infraBonus = 0.05 * (infra.data_quality - 1);
    const computeBonus = 0.03 * (infra.compute_level - 1);
    const reduction = Math.min(0.5, teamBonus + infraBonus + computeBonus);
    const multiplier = 1 - reduction;
    const effective = Math.max(1, Math.round(base * multiplier));
    const hint = document.getElementById('research-duration-hint');
    hint.innerText = `Estimated duration: ${effective} weeks with current team/infra`;
}

async function fetchSavesList() {
    const response = await fetch('/api/action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type: 'list_saves' })
    });
    const data = await response.json();
    if (data.status === 'ok' && data.saves) {
        const select = document.getElementById('load-select');
        select.innerHTML = '';
        const defaultOpt = document.createElement('option');
        defaultOpt.value = 'savegame';
        defaultOpt.innerText = 'savegame (default)';
        select.appendChild(defaultOpt);
        data.saves.forEach(name => {
            if (name === 'savegame') return;
            const opt = document.createElement('option');
            opt.value = name;
            opt.innerText = name;
            select.appendChild(opt);
        });
    }
}

async function saveGame() {
    const nameInput = document.getElementById('save-name-input');
    const name = (nameInput.value || 'savegame').trim();
    const response = await fetch('/api/action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type: 'save_game', name })
    });
    const data = await response.json();
    if (data.state) {
        updateUI(data.state);
    }
    await fetchSavesList();
    alert(data.message || "Game saved");
}

async function loadGame() {
    const select = document.getElementById('load-select');
    const name = select.value || 'savegame';
    const response = await fetch('/api/action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type: 'load_game', name })
    });
    const data = await response.json();
    updateUI(data.state);
    alert(data.message || "Game loaded!");
}
