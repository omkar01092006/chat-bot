// ── Globals ────────────────────────────────────────────────────
const messagesEl   = document.getElementById('messages');
const inputEl      = document.getElementById('userInput');
const logEntriesEl = document.getElementById('logEntries');
const logCounterEl = document.getElementById('logCounter');
let logCount = 0;

// ── Starfield ──────────────────────────────────────────────────
(function buildStars() {
    const field = document.getElementById('starfield');
    for (let i = 0; i < 120; i++) {
        const star = document.createElement('div');
        star.className = 'star';
        const size = Math.random() * 2.5 + 0.5;
        star.style.cssText = `
            left: ${Math.random() * 100}%;
            top: ${Math.random() * 100}%;
            width: ${size}px;
            height: ${size}px;
            --dur: ${Math.random() * 4 + 2}s;
            --delay: ${Math.random() * 6}s;
            --bright: ${Math.random() * 0.7 + 0.2};
        `;
        field.appendChild(star);
    }
})();

// ── Init ───────────────────────────────────────────────────────
window.addEventListener('load', () => {
    sendIntent('greet', 'hello');
});

// ── Key handler ────────────────────────────────────────────────
function handleKey(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
}

function autoResize(el) {
    el.style.height = 'auto';
    el.style.height = Math.min(el.scrollHeight, 120) + 'px';
}

// ── Send user text ─────────────────────────────────────────────
function sendMessage() {
    const text = inputEl.value.trim();
    if (!text) return;
    appendUserBubble(text);
    inputEl.value = '';
    inputEl.style.height = 'auto';
    sendToServer(text, '');
}

// ── Mood chip ──────────────────────────────────────────────────
function logMood(mood) {
    const labels = {
        happy:'Happy', calm:'Calm', neutral:'Neutral', grateful:'Grateful',
        excited:'Excited', anxious:'Anxious', sad:'Sad',
        stressed:'Stressed', tired:'Tired', angry:'Angry'
    };
    const label = labels[mood] || mood;
    appendUserBubble(`I'm feeling ${label}`);
    document.querySelectorAll('.mood-chip').forEach(c => c.classList.remove('active'));
    const chip = document.querySelector(`.mood-chip[data-mood="${mood}"]`);
    if (chip) chip.classList.add('active');
    sendToServer(`I'm feeling ${label}`, '');
}

// ── Quick action buttons ───────────────────────────────────────
function quickSend(intent) {
    const labels = {
        breathing: 'Breathing exercise',
        strategies: 'Coping strategies',
        affirm: 'Give me an affirmation',
        summary: 'Show my mood log'
    };
    const label = labels[intent] || intent;
    appendUserBubble(label);
    sendIntent(intent, label);
}

function sendIntent(intent, text) {
    showTyping();
    fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, intent: intent })
    })
    .then(r => r.json())
    .then(data => {
        removeTyping();
        renderResponse(data);
    })
    .catch(() => {
        removeTyping();
        appendBotText("Something went wrong. Please try again. 💙");
    });
}

function sendToServer(text, intent) {
    showTyping();
    fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text, intent: intent })
    })
    .then(r => r.json())
    .then(data => {
        removeTyping();
        renderResponse(data);
    })
    .catch(() => {
        removeTyping();
        appendBotText("Something went wrong. Please try again. 💙");
    });
}

// ── Render responses ───────────────────────────────────────────
function renderResponse(data) {
    switch (data.type) {
        case 'greeting':
            appendBotText(data.message);
            break;
        case 'text':
        case 'prompt':
            appendBotText(data.message, true);
            break;
        case 'mood_logged':
            renderMoodCard(data);
            break;
        case 'strategies':
            appendBotText(data.message);
            renderStrategies(data.strategies, data.mood_info);
            break;
        case 'summary':
            appendBotText("Here's your mood journey so far today 🌙");
            renderSummary(data.summary);
            break;
        case 'breathing':
            appendBotText(data.message);
            renderBreathing();
            break;
        case 'affirmation':
            renderAffirmation(data.message);
            break;
        default:
            appendBotText(data.message || "I'm here. 💙");
    }
    scrollDown();
}

// ── Plain text bubble ──────────────────────────────────────────
function appendBotText(text, useMarkdown = false) {
    const wrapper = document.createElement('div');
    wrapper.className = 'msg msg-bot';
    const content = useMarkdown ? renderMd(esc(text)) : esc(text);
    wrapper.innerHTML = `
        <div class="bot-name">Serenity</div>
        <div class="bubble bubble-bot">${content}</div>`;
    messagesEl.appendChild(wrapper);
}

function appendUserBubble(text) {
    const wrapper = document.createElement('div');
    wrapper.className = 'msg msg-user';
    wrapper.innerHTML = `<div class="bubble bubble-user">${esc(text)}</div>`;
    messagesEl.appendChild(wrapper);
    scrollDown();
}

// ── Mood card ──────────────────────────────────────────────────
function renderMoodCard(data) {
    const { entry, follow_up, strategies, affirmation } = data;
    const stratsHTML = strategies.map(s => `
        <div class="strat-mini-item">
            <span>${s.emoji}</span>
            <div><strong>${esc(s.title)}</strong>${esc(s.desc)}</div>
        </div>`).join('');

    const wrapper = document.createElement('div');
    wrapper.className = 'msg msg-bot';
    wrapper.innerHTML = `
        <div class="bot-name">Serenity</div>
        <div class="mood-card">
            <div class="mood-card-top">
                <div class="mood-big-emoji">${entry.emoji}</div>
                <div class="mood-card-info">
                    <strong>${esc(entry.label)} — logged</strong>
                    <span>at ${esc(entry.time)}</span>
                </div>
            </div>
            <div class="mood-follow-up">${esc(follow_up)}</div>
            <div class="strat-mini-title">Two things that may help</div>
            <div class="strat-mini-list">${stratsHTML}</div>
            <div class="mood-affirmation">${esc(affirmation)}</div>
        </div>`;
    messagesEl.appendChild(wrapper);

    // Update sidebar log
    addLogEntry(entry);
    updateCounter(data.log_count);

    // Reset mood chips after delay
    setTimeout(() => {
        document.querySelectorAll('.mood-chip').forEach(c => c.classList.remove('active'));
    }, 2000);
}

// ── Strategies ─────────────────────────────────────────────────
function renderStrategies(strategies, moodInfo) {
    const cardsHTML = strategies.map(s => `
        <div class="strategy-card">
            <div class="strategy-title">${s.emoji} ${esc(s.title)}</div>
            <div class="strategy-desc">${esc(s.desc)}</div>
        </div>`).join('');

    const wrapper = document.createElement('div');
    wrapper.className = 'msg msg-bot';
    wrapper.innerHTML = `
        <div class="bot-name">Serenity</div>
        <div class="strategies-wrap">${cardsHTML}</div>`;
    messagesEl.appendChild(wrapper);
}

// ── Summary ────────────────────────────────────────────────────
function renderSummary(s) {
    const maxCount = Math.max(...Object.values(s.counts).map(v => v.count));
    const barsHTML = Object.entries(s.counts).map(([mood, v]) => `
        <div class="mood-bar-row">
            <div class="mood-bar-label">${v.info.emoji} ${esc(v.info.label)}</div>
            <div class="mood-bar-track">
                <div class="mood-bar-fill" style="width:${(v.count/maxCount)*100}%;background:${v.info.color}"></div>
            </div>
            <div class="mood-bar-count">${v.count}x</div>
        </div>`).join('');

    const avgLabel = s.avg_level >= 4 ? 'Positive' : s.avg_level >= 3 ? 'Neutral' : 'Challenging';

    const wrapper = document.createElement('div');
    wrapper.className = 'msg msg-bot';
    wrapper.innerHTML = `
        <div class="bot-name">Serenity</div>
        <div class="summary-card">
            <div class="summary-title">🌙 Today's Mood Journey</div>
            <div class="summary-dominant">
                <div class="summary-dominant-emoji">${s.dominant_info.emoji}</div>
                <div>
                    <strong style="color:var(--soft-white);font-size:16px">${esc(s.dominant_info.label)}</strong>
                    <div class="summary-stat">Most frequent mood</div>
                    <div class="summary-stat"><strong>${s.total}</strong> entries · Avg mood: <strong>${avgLabel}</strong></div>
                </div>
            </div>
            <div class="mood-bars">${barsHTML}</div>
        </div>`;
    messagesEl.appendChild(wrapper);
}

// ── Breathing ──────────────────────────────────────────────────
function renderBreathing() {
    const wrapper = document.createElement('div');
    wrapper.className = 'msg msg-bot';
    wrapper.innerHTML = `
        <div class="bot-name">Serenity</div>
        <div class="breathing-card">
            <div class="breath-phase" id="breathPhase">Ready</div>
            <div class="breath-counter" id="breathCounter">Press start to begin box breathing</div>
            <div class="breath-circle-wrap">
                <div class="breath-circle" id="breathCircle">🌬</div>
            </div>
            <button class="breath-start-btn" id="breathBtn" onclick="startBreathing(this)">Begin</button>
        </div>`;
    messagesEl.appendChild(wrapper);
}

function startBreathing(btn) {
    btn.disabled = true;
    btn.textContent = 'Breathing…';
    const phases = [
        { label: 'Inhale',    dur: 4000, cls: 'inhale', icon: '🫁' },
        { label: 'Hold',      dur: 4000, cls: 'hold',   icon: '⏸' },
        { label: 'Exhale',    dur: 4000, cls: 'exhale', icon: '🌬' },
        { label: 'Hold',      dur: 4000, cls: 'hold',   icon: '⏸' },
    ];
    let round = 0;
    const totalRounds = 4;

    function runPhase(phaseIdx) {
        if (round >= totalRounds) {
            document.getElementById('breathPhase').textContent = 'Done ✨';
            document.getElementById('breathCounter').textContent = 'Well done. Take a moment to notice how you feel.';
            document.getElementById('breathCircle').textContent = '✨';
            document.getElementById('breathCircle').className = 'breath-circle';
            btn.textContent = 'Complete';
            return;
        }
        const phase = phases[phaseIdx];
        const phaseEl = document.getElementById('breathPhase');
        const countEl = document.getElementById('breathCounter');
        const circleEl = document.getElementById('breathCircle');

        if (phaseEl) phaseEl.textContent = phase.label;
        if (countEl) countEl.textContent = `Round ${round + 1} of ${totalRounds}`;
        if (circleEl) {
            circleEl.textContent = phase.icon;
            circleEl.className = `breath-circle ${phase.cls}`;
        }

        let seconds = phase.dur / 1000;
        const tick = setInterval(() => {
            seconds--;
            if (countEl) countEl.textContent = `${seconds}s — Round ${round + 1} of ${totalRounds}`;
        }, 1000);

        setTimeout(() => {
            clearInterval(tick);
            const nextPhase = (phaseIdx + 1) % phases.length;
            if (nextPhase === 0) round++;
            runPhase(nextPhase);
        }, phase.dur);
    }

    runPhase(0);
}

// ── Affirmation ────────────────────────────────────────────────
function renderAffirmation(text) {
    const wrapper = document.createElement('div');
    wrapper.className = 'msg msg-bot';
    wrapper.innerHTML = `
        <div class="bot-name">Serenity</div>
        <div class="affirmation-bubble">${esc(text)}</div>`;
    messagesEl.appendChild(wrapper);
}

// ── Sidebar log update ─────────────────────────────────────────
function addLogEntry(entry) {
    const empty = logEntriesEl.querySelector('.empty-log');
    if (empty) empty.remove();

    const el = document.createElement('div');
    el.className = 'log-entry-mini';
    el.innerHTML = `
        <div class="log-dot" style="background:${entry.color}"></div>
        <div class="log-label">${entry.emoji} ${entry.label}</div>
        <div class="log-time">${entry.time}</div>`;
    logEntriesEl.appendChild(el);
    logEntriesEl.scrollTop = logEntriesEl.scrollHeight;
}

function updateCounter(count) {
    logCount = count;
    logCounterEl.textContent = `${count} entr${count === 1 ? 'y' : 'ies'} today`;
}

// ── Typing ─────────────────────────────────────────────────────
function showTyping() {
    const el = document.createElement('div');
    el.className = 'msg msg-bot';
    el.id = 'typing-msg';
    el.innerHTML = `
        <div class="bot-name">Serenity</div>
        <div class="typing-wrap">
            <div class="dot"></div>
            <div class="dot"></div>
            <div class="dot"></div>
        </div>`;
    messagesEl.appendChild(el);
    scrollDown();
}

function removeTyping() {
    const el = document.getElementById('typing-msg');
    if (el) el.remove();
}

// ── Helpers ────────────────────────────────────────────────────
function scrollDown() {
    messagesEl.scrollTop = messagesEl.scrollHeight;
}

function esc(str) {
    return String(str || '')
        .replace(/&/g,'&amp;').replace(/</g,'&lt;')
        .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function renderMd(html) {
    return html
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.+?)\*/g, '<em>$1</em>');
}
