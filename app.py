import streamlit as st
from datetime import datetime, time
import pytz
from streamlit_autorefresh import st_autorefresh

PARIS = pytz.timezone("Europe/Paris")
st_autorefresh(interval=1000, key="timer_refresh")

# ══════════════════════════════════════════════
# SESSIONS
# ══════════════════════════════════════════════
SESSIONS = [
    ("EU",  time(9, 45),  time(11, 15)),
    ("US1", time(15, 45), time(17, 15)),
    ("US2", time(19, 30), time(21,  0)),
]

def get_active_session():
    now = datetime.now(PARIS)
    for name, s, e in SESSIONS:
        if s <= now.time() <= e:
            return name, s, e
    return None, None, None

session_name, start, end = get_active_session()

# ══════════════════════════════════════════════
# STATE
# ══════════════════════════════════════════════
defaults = {
    "step": 0,
    "direction": None,
    "validated": {},
    "session_log": [],
    "entry_time": None,
    "trade_active": False,
    "summary_shown": False,
    # nouvelle logique : entrée possible après step 2
    "can_enter": False,
    # Variables pour le suivi SL/TP
    "sl_respected": False,
    "tp_reached": False,
    # Historique des trades avec détails
    "trade_history": [],
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ══════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════
def validate(sk, rk):
    if sk not in st.session_state.validated:
        st.session_state.validated[sk] = set()
    st.session_state.validated[sk].add(rk)

def is_ok(sk, rk):
    return rk in st.session_state.validated.get(sk, set())

def all_ok(sk, keys):
    return all(is_ok(sk, k) for k in keys)

def log_event(etype, detail=""):
    st.session_state.session_log.append({
        "time": datetime.now(PARIS).strftime("%H:%M:%S"),
        "type": etype,
        "detail": detail,
        "session": session_name or "—",
    })

def record_trade_entry():
    """Enregistre l'entrée en position avec les règles validées"""
    trade_data = {
        "entry_time": datetime.now(PARIS).strftime("%H:%M:%S"),
        "direction": st.session_state.direction,
        "validated_rules": st.session_state.validated.copy(),
        "session": session_name or "—",
        "date": datetime.now(PARIS).strftime("%Y-%m-%d"),
        "sl_respected": None,
        "tp_reached": None,
        "exit_time": None,
        "result": None,
        # Deux conditions de trading
        "bonnes_conditions": is_ok("s1", "bonnes_conditions"),
        "annonces": is_ok("s1", "annonces")
    }
    st.session_state.trade_history.append(trade_data)

def record_trade_exit(is_win, sl_respected, tp_reached):
    """Enregistre la sortie de position"""
    if st.session_state.trade_history:
        last_trade = st.session_state.trade_history[-1]
        last_trade["exit_time"] = datetime.now(PARIS).strftime("%H:%M:%S")
        last_trade["result"] = "GAGNANT" if is_win else "PERDANT"
        last_trade["sl_respected"] = sl_respected
        last_trade["tp_reached"] = tp_reached

def get_tp_zone():
    if session_name is None:
        return None, None, None, 0
    now = datetime.now(PARIS)
    def dt(t): return PARIS.localize(datetime.combine(now.date(), t))
    zones = {
        "EU":  [time(9,45),  time(10,15), time(10,30), time(11,15)],
        "US1": [time(15,45), time(16,15), time(16,30), time(17,15)],
        "US2": [time(19,30), time(20,0),  time(20,15), time(21,0)],
    }
    g, o, r, se = [dt(t) for t in zones[session_name]]
    if   g <= now < o:  return "M15",   "#3BFFA0", o,  max(0, int((o  - now).total_seconds()))
    elif o <= now < r:  return "M5–M1", "#FFB800", r,  max(0, int((r  - now).total_seconds()))
    elif r <= now < se: return "M1",    "#FF5F5F", se, max(0, int((se - now).total_seconds()))
    return None, None, None, 0

# ══════════════════════════════════════════════
# CSS — Dark Neon Lisible
# fond #141820, cartes #1C2230, accents cyan/vert
# ══════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@700;800&family=Inter:wght@400;500;600&display=swap');

:root {
    --bg:       #141820;
    --surface:  #1C2230;
    --surface2: #232B3E;
    --border:   #2E3A50;
    --border-glow: #3BFFA055;
    --cyan:     #3BFFA0;
    --cyan-dim: #3BFFA033;
    --orange:   #FFB800;
    --orange-dim:#FFB80022;
    --red:      #FF5F5F;
    --red-dim:  #FF5F5F22;
    --text:     #E8EDF5;
    --text-dim: #8895AA;
    --text-faint:#4A5568;
}

/* ── BASE FULL WIDTH ── */
[data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
}
[data-testid="stHeader"]  { background: transparent !important; }
[data-testid="stSidebar"] { background: #111620 !important; border-right: 1px solid var(--border) !important; }
[data-testid="block-container"],
.main .block-container {
    padding: 1.4rem 2rem !important;
    max-width: 100% !important;
    width: 100% !important;
}
[data-testid="stMarkdown"] p { font-family:'Inter',sans-serif !important; color:var(--text) !important; font-size:15px !important; }

/* ── TYPOGRAPHY ── */
.t-mono   { font-family:'DM Mono',monospace; }
.t-display{ font-family:'Syne',sans-serif; }
.t-body   { font-family:'Inter',sans-serif; }

/* ── DIVIDER ── */
.divider {
    height:1px;
    background: linear-gradient(90deg, transparent, var(--border), transparent);
    margin: 18px 0; border:none;
}
.divider-glow {
    height:1px;
    background: linear-gradient(90deg, transparent, var(--cyan), transparent);
    margin: 20px 0; border:none;
    box-shadow: 0 0 8px var(--cyan);
}

/* ── CARDS ── */
.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 18px 22px;
    margin-bottom: 12px;
}
.card-glow {
    background: var(--surface);
    border: 1px solid var(--cyan-dim);
    border-top: 2px solid var(--cyan);
    border-radius: 10px;
    padding: 18px 22px;
    margin-bottom: 12px;
    box-shadow: 0 4px 24px rgba(59,255,160,0.06);
}

/* ── HUD ── */
.hud-eyebrow {
    font-family:'DM Mono',monospace;
    font-size:11px; letter-spacing:0.22em;
    color:var(--cyan); text-transform:uppercase;
    margin:0 0 4px 0;
}
.hud-title {
    font-family:'Syne',sans-serif;
    font-size:28px; font-weight:800;
    color:var(--text); margin:0;
    letter-spacing:-0.01em;
}
.live-clock {
    font-family:'DM Mono',monospace;
    font-size:30px; font-weight:500;
    color:var(--text); letter-spacing:0.06em;
    text-align:right;
}
.live-date {
    font-family:'DM Mono',monospace;
    font-size:11px; color:var(--text-faint);
    letter-spacing:0.15em; text-align:right; margin-bottom:4px;
}

/* ── SESSION PILLS ── */
.sess-pill {
    border-radius:8px; padding:12px 16px;
    border:1px solid var(--border);
    background:var(--surface2);
}
.sess-pill.live {
    border-color: var(--cyan-dim);
    background: rgba(59,255,160,0.05);
    box-shadow: 0 0 16px rgba(59,255,160,0.08);
}
.sess-status {
    font-family:'DM Mono',monospace; font-size:10px;
    letter-spacing:0.2em; text-transform:uppercase; margin-bottom:4px;
}
.sess-name {
    font-family:'Syne',sans-serif; font-size:18px; font-weight:800;
    margin:2px 0;
}
.sess-time {
    font-family:'DM Mono',monospace; font-size:11px; color:var(--text-faint);
}

/* ── TIMERS ── */
.timer-label {
    font-family:'DM Mono',monospace; font-size:10px;
    color:var(--text-faint); letter-spacing:0.22em;
    text-transform:uppercase; margin-bottom:8px;
}
.timer-big {
    font-family:'DM Mono',monospace; font-size:42px; font-weight:500;
    color:var(--cyan); letter-spacing:0.04em; line-height:1;
    text-shadow: 0 0 20px rgba(59,255,160,0.4);
}
.timer-big.warn  { color:var(--orange) !important; text-shadow:0 0 20px rgba(255,184,0,0.4) !important; }
.timer-big.danger{ color:var(--red)    !important; text-shadow:0 0 20px rgba(255,95,95,0.4)  !important; }
.progress-track {
    height:4px; background:var(--border);
    border-radius:2px; margin:12px 0 6px; overflow:hidden;
}

/* ── STEP HEADER ── */
.step-hdr {
    display:flex; align-items:center; gap:14px;
    margin-bottom:16px;
}
.step-num-badge {
    font-family:'DM Mono',monospace; font-size:11px; font-weight:500;
    color:var(--cyan); background:var(--cyan-dim);
    border:1px solid var(--cyan-dim); border-radius:6px;
    padding:4px 10px; letter-spacing:0.1em; white-space:nowrap;
}
.step-hdr-title {
    font-family:'Syne',sans-serif; font-size:20px; font-weight:800;
    color:var(--text); letter-spacing:-0.01em;
}

/* ── RULE CARDS ── */
.rule {
    border-radius:8px; padding:14px 18px; margin:8px 0;
    font-family:'Inter',sans-serif; font-size:15px;
    font-weight:500; line-height:1.55; position:relative;
}
.rule.cyan   { background:rgba(59,255,160,0.06); border:1px solid rgba(59,255,160,0.2); border-left:3px solid var(--cyan);   color:#C8F7E5; }
.rule.orange { background:rgba(255,184,0,0.06);  border:1px solid rgba(255,184,0,0.2);  border-left:3px solid var(--orange); color:#FFF0C0; }
.rule.red    { background:rgba(255,95,95,0.06);  border:1px solid rgba(255,95,95,0.2);  border-left:3px solid var(--red);    color:#FFD5D5; }
.rule.done   { opacity:0.45; }
.rule-icon   { display:inline-block; margin-right:10px; font-size:13px; }
.rule-ok-badge {
    font-family:'DM Mono',monospace; font-size:10px;
    letter-spacing:0.15em; margin: 2px 0 10px 0;
    padding-left:6px;
}

/* ── DIRECTION BADGE ── */
.dir-badge {
    font-family:'Syne',sans-serif; font-size:15px; font-weight:800;
    letter-spacing:0.08em; padding:7px 18px; border-radius:8px;
    display:inline-block;
}
.dir-achat { background:rgba(59,255,160,0.1); border:1px solid rgba(59,255,160,0.3); color:var(--cyan); }
.dir-vente { background:rgba(255,95,95,0.1);  border:1px solid rgba(255,95,95,0.3);  color:var(--red);  }

/* ── PROGRESS DOTS ── */
.dots-row { display:flex; gap:6px; margin:4px 0; }
.dot { height:4px; flex:1; border-radius:2px; background:var(--border); }
.dot.done   { background:var(--cyan); box-shadow:0 0 6px rgba(59,255,160,0.5); }
.dot.active { background:rgba(59,255,160,0.5); }

/* ── LOCK WARNING ── */
.lock-warn {
    background:rgba(255,184,0,0.06); border:1px solid rgba(255,184,0,0.25);
    border-radius:8px; padding:10px 16px; margin:10px 0;
    font-family:'DM Mono',monospace; font-size:11px;
    color:var(--orange); letter-spacing:0.12em; text-align:center;
}

/* ── ENTER POSITION BANNER ── */
.enter-banner {
    background: linear-gradient(135deg, rgba(59,255,160,0.08), rgba(59,255,160,0.03));
    border:1px solid rgba(59,255,160,0.3);
    border-radius:10px; padding:20px; text-align:center; margin:12px 0;
}
.enter-title {
    font-family:'Syne',sans-serif; font-size:16px; font-weight:800;
    color:var(--cyan); letter-spacing:0.05em;
}
.enter-sub {
    font-family:'DM Mono',monospace; font-size:11px;
    color:var(--text-faint); letter-spacing:0.14em; margin-top:6px;
}

/* ── POSITION DASHBOARD ── */
.pos-header {
    background: linear-gradient(135deg, rgba(59,255,160,0.07), rgba(59,255,160,0.02));
    border:1px solid rgba(59,255,160,0.25);
    border-radius:12px; padding:22px 26px; margin-bottom:16px;
    animation: glow-pulse 3s ease-in-out infinite;
}
@keyframes glow-pulse {
    0%,100% { box-shadow: 0 0 0 rgba(59,255,160,0); }
    50%      { box-shadow: 0 0 24px rgba(59,255,160,0.1); }
}
.pos-live-tag {
    display:inline-flex; align-items:center; gap:6px;
    font-family:'DM Mono',monospace; font-size:11px;
    color:var(--cyan); letter-spacing:0.2em;
    background:rgba(59,255,160,0.1); border:1px solid rgba(59,255,160,0.25);
    border-radius:20px; padding:4px 12px; margin-bottom:12px;
}
.pos-live-dot {
    width:7px; height:7px; background:var(--cyan);
    border-radius:50%; animation:blink 1.2s ease-in-out infinite;
}
@keyframes blink { 0%,100%{opacity:1;} 50%{opacity:0.2;} }
.pos-direction {
    font-family:'Syne',sans-serif; font-size:32px; font-weight:800;
    letter-spacing:0.05em; margin:4px 0;
}
.pos-entry {
    font-family:'DM Mono',monospace; font-size:13px;
    color:var(--text-dim); letter-spacing:0.1em;
}

/* ── RECAP CARD ── */
.recap-card {
    background:var(--surface2); border:1px solid var(--border);
    border-radius:8px; padding:14px 18px; margin-bottom:8px;
}
.recap-label {
    font-family:'DM Mono',monospace; font-size:10px;
    color:var(--text-faint); letter-spacing:0.2em;
    text-transform:uppercase; margin-bottom:8px;
}
.recap-rule {
    font-family:'Inter',sans-serif; font-size:14px;
    color:var(--text); line-height:1.5; padding:6px 0;
    border-bottom:1px solid var(--border); display:flex; gap:10px;
    align-items:flex-start;
}
.recap-rule:last-child { border-bottom:none; }
.recap-check { color:var(--cyan); font-size:12px; margin-top:2px; flex-shrink:0; }

/* ── INFO BLOCS POSITION ── */
.info-bloc {
    background:var(--surface2); border:1px solid var(--border);
    border-radius:12px; padding:24px 28px;
    height: 100%;
    transition: box-shadow 0.2s;
}
.info-bloc:hover {
    box-shadow: 0 4px 24px rgba(0,0,0,0.25);
}
.info-bloc-icon {
    font-size: 28px;
    margin-bottom: 12px;
    display: block;
}
.info-bloc-label {
    font-family:'DM Mono',monospace; font-size:11px;
    letter-spacing:0.25em; text-transform:uppercase;
    margin-bottom:14px; padding-bottom:10px;
    border-bottom:1px solid var(--border);
}
.info-bloc-title {
    font-family:'Syne',sans-serif; font-size:16px; font-weight:800;
    color:var(--text); margin-bottom:10px; letter-spacing:0.01em;
}
.info-bloc-content {
    font-family:'Inter',sans-serif; font-size:15px; font-weight:500;
    color:var(--text); line-height:1.7;
}
.info-bloc-content strong {
    font-weight:700; color:var(--text);
}
.info-bloc-rule {
    display:flex; align-items:flex-start; gap:10px;
    padding: 8px 0; border-bottom:1px solid var(--border);
    font-family:'Inter',sans-serif; font-size:14px; color:var(--text-dim); line-height:1.55;
}
.info-bloc-rule:last-child { border-bottom:none; }
.info-bloc-rule-icon { flex-shrink:0; font-size:15px; margin-top:1px; }
.info-bloc-timer {
    font-family:'DM Mono',monospace; font-size:38px; font-weight:500;
    letter-spacing:0.06em; line-height:1; margin:10px 0 4px;
}
.info-bloc-timer-label {
    font-family:'DM Mono',monospace; font-size:11px;
    color:var(--text-faint); letter-spacing:0.18em; text-transform:uppercase;
}

/* ── EXIT BUTTONS ── */
.exit-section {
    margin-top:6px;
}

/* ── SUMMARY STATS ── */
.stat-box {
    background:var(--surface2); border:1px solid var(--border);
    border-radius:10px; padding:18px; text-align:center;
}
.stat-num { font-family:'Syne',sans-serif; font-size:36px; font-weight:800; line-height:1; }
.stat-lbl { font-family:'DM Mono',monospace; font-size:10px; color:var(--text-faint); letter-spacing:0.2em; margin-top:6px; text-transform:uppercase; }

/* ── STREAMLIT BUTTON OVERRIDES ── */
div[data-testid="stButton"] > button {
    font-family:'Inter',sans-serif !important;
    font-size:14px !important; font-weight:600 !important;
    border-radius:8px !important;
    background:var(--surface2) !important;
    color:var(--text) !important;
    border:1px solid var(--border) !important;
    transition:all 0.18s ease !important;
    padding:0.5rem 1rem !important;
}
div[data-testid="stButton"] > button:hover {
    background:var(--surface) !important;
    border-color:var(--cyan-dim) !important;
    color:var(--cyan) !important;
    box-shadow:0 0 12px rgba(59,255,160,0.15) !important;
    transform:translateY(-1px) !important;
}
div[data-testid="stButton"] > button:disabled {
    background:#1a1f2b !important;
    color:var(--text-faint) !important;
    border-color:var(--border) !important;
    transform:none !important; box-shadow:none !important;
    cursor:not-allowed !important;
}

/* ── CHECKBOXES EN BLANC ── */
div[data-testid="stCheckbox"] label {
    color: var(--text) !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
}
div[data-testid="stCheckbox"] label span[data-baseweb="checkbox"] {
    background-color: var(--surface2) !important;
    border-color: var(--border) !important;
}
div[data-testid="stCheckbox"] label span[data-baseweb="checkbox"]:hover {
    border-color: var(--cyan-dim) !important;
}
div[data-testid="stCheckbox"] input[type="checkbox"]:checked + span[data-baseweb="checkbox"] {
    background-color: var(--cyan) !important;
    border-color: var(--cyan) !important;
}
/* Forcer le texte en blanc pour toutes les checkboxes */
div[data-testid="stCheckbox"] label > span:first-child {
    color: var(--text) !important;
}
/* CSS plus spécifique pour forcer le texte en blanc */
div[data-testid="stCheckbox"] label {
    color: #E8EDF5 !important;
}
div[data-testid="stCheckbox"] label span {
    color: #E8EDF5 !important;
}
/* CSS pour le texte spécifique des checkboxes */
div[data-testid="stCheckbox"] label .stText {
    color: #E8EDF5 !important;
}
/* CSS le plus puissant pour forcer le blanc */
div[data-testid="stCheckbox"] label > div {
    color: #E8EDF5 !important;
}
div[data-testid="stCheckbox"] label p {
    color: #E8EDF5 !important;
}
div[data-testid="stCheckbox"] label div {
    color: #E8EDF5 !important;
}

.stProgress > div > div { background:var(--cyan) !important; }
[data-testid="stProgress"] { background:var(--border) !important; border-radius:4px !important; }
</style>
""", unsafe_allow_html=True)

# ════════# ════════════════════════════════════════
# EXPORT CSV
# ════════════════════════════════════════
def convert_to_csv(trades):
    """Convertir les trades en format CSV"""
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # En-tête
    writer.writerow([
        'Date', 'Session', 'Direction', 'Entrée', 'Sortie', 
        'Résultat', 'Bonnes Conditions', 'Annonces Vérifiées',
        'Règles Discipline', 'Règles Timing', 
        'SL Respecté', 'TP Atteint'
    ])
    
    # Données
    for trade in trades:
        discipline_rules = len(trade.get('validated_rules', {}).get('s1', [])) if 'validated_rules' in trade else 0
        timing_rules = len(trade.get('validated_rules', {}).get('s2', [])) if 'validated_rules' in trade else 0
        
        writer.writerow([
            trade.get('date', ''),
            trade.get('session', ''),
            trade.get('direction', ''),
            trade.get('entry_time', ''),
            trade.get('exit_time', ''),
            trade.get('result', ''),
            '✅' if trade.get('bonnes_conditions') else '❌',
            '✅' if trade.get('annonces') else '❌',
            f"{discipline_rules}/2",
            f"{timing_rules}/3",
            '✅' if trade.get('sl_respected') else '❌',
            '✅' if trade.get('tp_reached') else '❌'
        ])
    
    return output.getvalue()

# ══════════════════════════════════════
# HUD HEADER
# ══════════════════════════════════════════════
now_str  = datetime.now(PARIS).strftime("%H:%M:%S")
date_str = datetime.now(PARIS).strftime("%d %b %Y").upper()

c_title, c_clock = st.columns([3, 1])
with c_title:
    st.markdown('<p class="hud-eyebrow">◈ Copilot de Trading</p>', unsafe_allow_html=True)
    st.markdown('<p class="hud-title">Plan de Trading</p>', unsafe_allow_html=True)
with c_clock:
    st.markdown(f'<p class="live-date">{date_str}</p><p class="live-clock">{now_str}</p>', unsafe_allow_html=True)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# SESSION STATUS
# ══════════════════════════════════════════════
now_time = datetime.now(PARIS).time()
cols_sess = st.columns(3)
for col, (sname, ss, se) in zip(cols_sess, SESSIONS):
    with col:
        active = ss <= now_time <= se
        cls    = "sess-pill live" if active else "sess-pill"
        s_col  = "var(--cyan)"   if active else "var(--text-faint)"
        n_col  = "var(--cyan)"   if active else "var(--text-dim)"
        status = "● LIVE"        if active else "○ Offline"
        st.markdown(f"""
        <div class="{cls}">
            <div class="sess-status" style="color:{s_col};">{status}</div>
            <div class="sess-name"   style="color:{n_col};">Session {sname}</div>
            <div class="sess-time">{ss.strftime('%H:%M')} → {se.strftime('%H:%M')}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# TIMERS
# ══════════════════════════════════════════════
c_sess, c_tp = st.columns(2)

with c_sess:
    if session_name is not None:
        now_dt   = datetime.now(PARIS)
        end_dt   = PARIS.localize(datetime.combine(now_dt.date(), end))
        start_dt = PARIS.localize(datetime.combine(now_dt.date(), start))
        rem      = max(0, int((end_dt - now_dt).total_seconds()))
        total    = int((end_dt - start_dt).total_seconds())
        pct      = (1 - rem / total) * 100 if total > 0 else 0
        h_r, m_r, s_r = rem // 3600, (rem % 3600) // 60, rem % 60
        t_cls    = "danger" if rem < 600 else ("warn" if rem < 1200 else "")
        fill_c   = "var(--red)" if rem < 600 else ("var(--orange)" if rem < 1200 else "var(--cyan)")
        st.markdown(f"""
        <div class="card">
            <div class="timer-label">⏱ Décompte Session · {session_name}</div>
            <div class="timer-big {t_cls}">{h_r:02d}:{m_r:02d}:{s_r:02d}</div>
            <div class="progress-track">
                <div style="width:{pct:.1f}%;height:100%;background:{fill_c};border-radius:2px;transition:width 1s linear;"></div>
            </div>
            <div style="font-family:'DM Mono',monospace;font-size:10px;color:var(--text-faint);letter-spacing:0.15em;">{pct:.0f}% ÉCOULÉ</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="card">
            <div class="timer-label">⏱ Décompte Session</div>
            <div style="font-family:'Syne',sans-serif;font-size:18px;font-weight:800;color:var(--text-faint);margin-top:8px;">Hors session</div>
            <div style="font-family:'DM Mono',monospace;font-size:11px;color:var(--text-faint);margin-top:6px;letter-spacing:0.12em;">En attente d'ouverture</div>
        </div>
        """, unsafe_allow_html=True)

with c_tp:
    tp_name, tp_color, tp_end_dt, tp_rem = get_tp_zone()
    if tp_name:
        m_tp, s_tp = tp_rem // 60, tp_rem % 60
        durations  = {"M15": 1800, "M5–M1": 900, "M1": 2700}
        zone_tot   = durations.get(tp_name, 1800)
        zone_pct   = max(0, min(100, (1 - tp_rem / zone_tot) * 100))
        st.markdown(f"""
        <div class="card" style="border-left:3px solid {tp_color};">
            <div class="timer-label" style="color:{tp_color}aa;">🎯 Zone TP Active</div>
            <div style="font-family:'Syne',sans-serif;font-size:20px;font-weight:800;color:{tp_color};margin:6px 0;text-shadow:0 0 12px {tp_color}66;">
                Boll {tp_name}
            </div>
            <div class="progress-track">
                <div style="width:{zone_pct:.1f}%;height:100%;background:{tp_color};border-radius:2px;box-shadow:0 0 6px {tp_color}88;transition:width 1s linear;"></div>
            </div>
            <div style="display:flex;justify-content:space-between;align-items:center;">
                <div style="font-family:'DM Mono',monospace;font-size:10px;color:var(--text-faint);letter-spacing:0.15em;">TEMPS RESTANT</div>
                <div style="font-family:'DM Mono',monospace;font-size:26px;font-weight:500;color:{tp_color};text-shadow:0 0 10px {tp_color}66;">{m_tp:02d}:{s_tp:02d}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="card">
            <div class="timer-label">🎯 Zone TP</div>
            <div style="font-family:'Syne',sans-serif;font-size:16px;font-weight:800;color:var(--text-faint);margin-top:8px;">En attente de zone</div>
            <div style="font-family:'DM Mono',monospace;font-size:11px;color:var(--text-faint);margin-top:6px;letter-spacing:0.12em;">Hors plage TP active</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div class='divider-glow'></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# STEP 0 — DIRECTION
# ══════════════════════════════════════════════════════════════
if st.session_state.step == 0:

    # ── RAPPORT DE SESSION ───────────────────────────────
    if st.session_state.summary_shown:
        st.markdown("""
        <div class="step-hdr">
            <div class="step-num-badge">Fin de session</div>
            <div class="step-hdr-title">Rapport de Performance</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Calcul des statistiques
        trades = st.session_state.trade_history
        total_trades = len(trades)
        
        if total_trades > 0:
            winning_trades = len([t for t in trades if t["result"] == "GAGNANT"])
            losing_trades = len([t for t in trades if t["result"] == "PERDANT"])
            win_rate = int((winning_trades / total_trades * 100))
            
            # Calcul des pourcentages de respect des règles
            sl_respected_count = len([t for t in trades if t["sl_respected"] == True])
            tp_reached_count = len([t for t in trades if t["tp_reached"] == True])
            sl_respect_rate = int((sl_respected_count / total_trades * 100)) if total_trades > 0 else 0
            tp_reach_rate = int((tp_reached_count / total_trades * 100)) if total_trades > 0 else 0
            
            # Calcul du pourcentage total de respect des règles
            total_rules_respected = 0
            total_rules_possible = 0
            
            for trade in trades:
                # Règles d'entrée validées
                entry_rules = 0
                if "s1" in trade["validated_rules"]:
                    entry_rules += len(trade["validated_rules"]["s1"])
                if "s2" in trade["validated_rules"]:
                    entry_rules += len(trade["validated_rules"]["s2"])
                total_rules_respected += entry_rules
                
                # Conditions de trading (2 conditions)
                if trade.get("bonnes_conditions"):
                    total_rules_respected += 1
                if trade.get("annonces"):
                    total_rules_respected += 1
                
                # Règles de sortie (SL/TP)
                if trade["sl_respected"]:
                    total_rules_respected += 1
                if trade["tp_reached"]:
                    total_rules_respected += 1
                
                total_rules_possible += entry_rules + 4  # +2 conditions + 2 pour SL et TP
            
            overall_respect_rate = int((total_rules_respected / total_rules_possible * 100)) if total_rules_possible > 0 else 0
            
            # Affichage des statistiques
            s1, s2, s3, s4 = st.columns(4)
            with s1:
                st.markdown(f'<div class="stat-box"><div class="stat-num" style="color:var(--text);">{total_trades}</div><div class="stat-lbl" style="color:var(--text);">Trades</div></div>', unsafe_allow_html=True)
            with s2:
                st.markdown(f'<div class="stat-box"><div class="stat-num" style="color:var(--cyan);">{tp_reach_rate}%</div><div class="stat-lbl" style="color:var(--text);">TP Respect</div></div>', unsafe_allow_html=True)
            with s3:
                st.markdown(f'<div class="stat-box"><div class="stat-num" style="color:var(--red);">{sl_respect_rate}%</div><div class="stat-lbl" style="color:var(--text);">SL Respect</div></div>', unsafe_allow_html=True)
            with s4:
                st.markdown(f'<div class="stat-box"><div class="stat-num" style="color:var(--orange);">{overall_respect_rate}%</div><div class="stat-lbl" style="color:var(--text);">Règles Respect</div></div>', unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Filtres par date avec calendrier visuel
            unique_dates = sorted(list(set(trade["date"] for trade in trades)))
            
            # Convertir les dates en objets datetime pour le calendrier
            date_objects = []
            for date_str in unique_dates:
                try:
                    date_objects.append(datetime.strptime(date_str, "%Y-%m-%d").date())
                except:
                    continue
            
            # Calendrier visuel pour sélectionner une date
            selected_date_obj = st.date_input(
                "📅 Sélectionner une date:",
                value=None,
                min_value=min(date_objects) if date_objects else None,
                max_value=max(date_objects) if date_objects else None,
                key="date_calendar"
            )
            
            # Déterminer la date sélectionnée
            if selected_date_obj:
                selected_date = selected_date_obj.strftime("%Y-%m-%d")
                filtered_trades = [trade for trade in trades if trade["date"] == selected_date]
            else:
                selected_date = None
                filtered_trades = trades
            
            st.markdown("---")
            
            # Boutons d'action au-dessus du bouton Nouvelle session
            col_export, col_reset = st.columns(2)
            
            with col_export:
                # Préparer le CSV une seule fois pour éviter les problèmes
                csv_data = convert_to_csv(trades)
                st.download_button(
                    label="📥 Exporter les données",
                    data=csv_data,
                    file_name=f"trading_export_{datetime.now(PARIS).strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col_reset:
                if st.button("🗑️ Réinitialiser les données", use_container_width=True, key="reset_all_data"):
                    if st.session_state.trade_history:
                        st.session_state.trade_history = []
                        st.session_state.session_log = []
                        st.success("✅ Toutes les données ont été réinitialisées avec succès!")
                        st.rerun()
                    else:
                        st.info("ℹ️ Aucune donnée à réinitialiser")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Affichage des trades filtrés
            if selected_date:
                st.markdown(f'<div style="font-family:\'DM Mono\',monospace;font-size:10px;color:var(--text-faint);letter-spacing:0.22em;margin-bottom:10px;">▸ HISTORIQUE DES TRADES - {selected_date}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div style="font-family:\'DM Mono\',monospace;font-size:10px;color:var(--text-faint);letter-spacing:0.22em;margin-bottom:10px;">▸ HISTORIQUE DES TRADES</div>', unsafe_allow_html=True)
            
            for trade in filtered_trades:
                # Couleur selon résultat
                result_color = "var(--cyan)" if trade["result"] == "GAGNANT" else "var(--red)"
                result_icon = "✓" if trade["result"] == "GAGNANT" else "✗"
                
                # Règles validées
                rules_text = []
                
                # Compter uniquement les règles de discipline (r1, r2) dans s1
                discipline_count = 0
                if "s1" in trade["validated_rules"]:
                    discipline_rules = ["r1", "r2"]  # règles de discipline uniquement
                    discipline_count = len([r for r in discipline_rules if r in trade["validated_rules"]["s1"]])
                    rules_text.append(f"Discipline: {discipline_count}/2")
                
                # Compter les règles de timing dans s2
                # if "s2" in trade["validated_rules"]:
                #     rules_text.append(f"Timing: {len(trade['validated_rules']['s2'])}/3")
                
                # SL/TP
                sl_text = "✅" if trade["sl_respected"] else "❌"
                tp_text = "✅" if trade["tp_reached"] else "❌"
                
                st.markdown(f"""
                <div style="background:var(--surface2); border:1px solid var(--border); border-radius:8px; padding:12px; margin-bottom:8px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                        <div style="color:var(--text); font-family:'Syne',sans-serif; font-size:16px; font-weight:700;">
                            {trade['direction']} | {trade['entry_time']} → {trade['exit_time']}
                        </div>
                        <div style="color:{result_color}; font-family:'DM Mono',monospace; font-size:14px; font-weight:500;">
                            {result_icon} {trade['result']}
                        </div>
                    </div>
                    <div style="font-family:'DM Mono',monospace;font-size:11px;color:var(--text-dim);">
                        <div>📅 {trade['date']} | 📍 Session {trade['session']}</div>
                        <div>📋 Règles: {' | '.join(rules_text)}</div>
                        <div>🛡️ SL: {sl_text} | 🎯 TP: {tp_text}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
        if st.button("↺  Nouvelle session", use_container_width=True):
            # Ne réinitialiser que les données de session courante, PAS l'historique
            st.session_state.session_log = []
            st.session_state.validated = {}
            st.session_state.trade_active = False
            st.session_state.summary_shown = False
            st.session_state.can_enter = False
            st.session_state.entry_time = None
            st.session_state.direction = None
            st.session_state.step = 0
            # NE PAS effacer trade_history pour conserver l'historique
            st.rerun()

    # ── CHOIX DIRECTION ───────────────────────────────────
    else:
        if session_name is not None:
            st.markdown('<div style="font-family:\'DM Mono\',monospace;font-size:11px;color:var(--text-faint);letter-spacing:0.2em;text-align:center;margin-bottom:20px;">SÉLECTIONNER LA DIRECTION</div>', unsafe_allow_html=True)
            st.markdown("""
            <style>
            div[data-testid="stButton"] > button { height:100px !important; font-size:18px !important; font-weight:700 !important; }
            </style>""", unsafe_allow_html=True)
            ca, cv = st.columns(2)
            with ca:
                if st.button("▲  ACHAT", use_container_width=True, key="btn_achat"):
                    st.session_state.direction = "ACHAT"
                    st.session_state.step = 1
                    st.session_state.validated = {}
                    st.session_state.can_enter = False
                    log_event("DIRECTION", "ACHAT")
                    st.rerun()
            with cv:
                if st.button("▼  VENTE", use_container_width=True, key="btn_vente"):
                    st.session_state.direction = "VENTE"
                    st.session_state.step = 1
                    st.session_state.validated = {}
                    st.session_state.can_enter = False
                    log_event("DIRECTION", "VENTE")
                    st.rerun()
            
            if st.session_state.session_log:
                st.markdown("<br>", unsafe_allow_html=True)
            
            # Bouton d'accès au rapport de session en fin de page
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("📊 Rapport de session", use_container_width=True, key="report_from_new_session"):
                st.session_state.summary_shown = True
                st.rerun()
        else:
            st.markdown("""
            <div style="background:rgba(255,95,95,0.05);border:1px solid rgba(255,95,95,0.2);border-radius:10px;padding:32px;text-align:center;">
                <div style="font-family:'Syne',sans-serif;font-size:18px;font-weight:800;color:var(--red);">Hors session</div>
                <div style="font-family:'DM Mono',monospace;font-size:11px;color:var(--text-faint);margin-top:10px;letter-spacing:0.12em;">
                    EU 09:45–11:15 · US1 15:45–17:15 · US2 19:30–21:00
                </div>
            </div>
            """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# STEP 1 — CONDITIONS DE TRADING (uniquement si direction choisie)
# ══════════════════════════════════════════════════════════════
if st.session_state.step == 1 and st.session_state.direction is not None:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div style="font-family:\'DM Mono\',monospace;font-size:11px;color:var(--text-faint);letter-spacing:0.2em;text-align:center;margin-bottom:20px;">🔍 CONDITIONS DE TRADING</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="card-glow">
        <div style="font-family:\'Syne\',sans-serif;font-size:16px;font-weight:800;color:var(--cyan);margin-bottom:16px;text-align:center;">
            Vérification pré-trade
        </div>
    """, unsafe_allow_html=True)
    
    # Utiliser le même format que les règles de discipline
    def rule_card_conditions(text, color, sk, rk):
        done = is_ok(sk, rk)
        icon_c = {"cyan": "var(--cyan)", "orange": "var(--orange)", "red": "var(--red)"}[color]
        bg_c = {"cyan": "rgba(59,255,160,0.06)", "orange": "rgba(255,184,0,0.06)", "red": "rgba(255,95,95,0.06)"}[color]
        border_c = {"cyan": "rgba(59,255,160,0.2)", "orange": "rgba(255,184,0,0.2)", "red": "rgba(255,95,95,0.2)"}[color]
        text_c = {"cyan": "#C8F7E5", "orange": "#FFF0C0", "red": "#FFD5D5"}[color]
        
        st.markdown(f"""
        <div class="rule {color} {('done' if done else '')}" style="background:{bg_c};border:1px solid {border_c};border-left:3px solid {icon_c};color:{text_c};">
            <span class="rule-icon">📋</span>
            {text}
        </div>
        """, unsafe_allow_html=True)
        
        if not done:
            if st.button("✓  J'ai vérifié", key=f"v_{sk}_{rk}", use_container_width=True):
                validate(sk, rk)
                st.rerun()
        else:
            st.markdown(f'<div class="rule-ok-badge" style="color:{icon_c}88;">Confirmé ✓</div>', unsafe_allow_html=True)

    sk = "s1"
    
    # Condition 1: Bonnes conditions
    rule_card_conditions("Suis-je dans de bonnes conditions pour trader ? (concentration, état d'esprit, forme physique...)", "cyan", sk, "bonnes_conditions")
    
    # Condition 2: Annonces
    rule_card_conditions("Ai-je vérifié les annonces économiques importantes ?", "orange", sk, "annonces")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Bouton pour continuer vers les règles de discipline
    conditions_all_ok = all_ok(sk, ["bonnes_conditions", "annonces"])
    
    if conditions_all_ok:
        st.markdown('<div class="enter-banner">', unsafe_allow_html=True)
        st.markdown('<div class="enter-title">✅ Conditions remplies</div>', unsafe_allow_html=True)
        st.markdown('<div class="enter-sub">Tu peux passer aux règles de discipline</div>', unsafe_allow_html=True)
        
        if st.button("→ Continuer vers les règles", use_container_width=True, key="continue_to_rules"):
            st.session_state.step = 2
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="lock-warn">
            ⚠ Valide toutes les conditions pour continuer
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# STEPS 2+ (normal) ou DASHBOARD POSITION (trade_active)
# ══════════════════════════════════════════════════════════════
if st.session_state.step >= 2 or st.session_state.trade_active:
    direction = st.session_state.direction
    step      = st.session_state.step

    # ──────────────────────────────────────────────────────
    # MODE POSITION ACTIVE → Version avec cartes SL/TP
    # ──────────────────────────────────────────────────────
    if st.session_state.trade_active:

        # Header simple dans une carte
        dir_col = "🟢" if direction == "ACHAT" else "🔴"
        dir_sym = "▲" if direction == "ACHAT" else "▼"
        
        st.markdown(f"""
        <div class="pos-header">
            <div class="pos-live-tag">
                <div class="pos-live-dot"></div>
                <span>POSITION ACTIVE</span>
            </div>
            <div class="pos-direction" style="color:{"var(--cyan)" if direction == "ACHAT" else "var(--red)"};">
                {dir_col} {dir_sym} {direction}
            </div>
            <div class="pos-entry">
                Entrée : {st.session_state.entry_time}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("---")
        
        # Cartes SL et TP côte à côte - Style session avec police plus grande
        tp_name, tp_color, tp_end_dt, tp_rem = get_tp_zone()
        
        col_sl, col_tp = st.columns(2, gap="large")
        
        with col_sl:
            # Récupérer l'état de la checkbox SL
            sl_respected = st.session_state.get("sl_respect_trade", False)
            sl_status = "✅ VALIDÉ" if sl_respected else "⏳ EN ATTENTE"
            sl_status_color = "var(--cyan)" if sl_respected else "var(--orange)"
            
            if direction == "ACHAT":
                sl_condition = "Bleue foncée + gold croisent EN-DESSOUS de la rouge"
            else:
                sl_condition = "Bleue claire + gold croisent AU-DESSUS de la rouge"
            
            st.markdown(f"""
            <div class="sess-pill" style="border-left:4px solid var(--red); border-color:var(--red); background:rgba(255,95,95,0.05);">
                <div class="sess-status" style="color:var(--red);">🛡️ STOP-LOSS</div>
                <div class="sess-name" style="color:var(--red);">Signal de sortie perdante</div>
                <div style="background:rgba(255,255,255,0.1); border-radius:6px; padding:8px; margin:8px 0; text-align:center;">
                    <div style="font-family:'DM Mono',monospace;font-size:12px;color:{sl_status_color};font-weight:600;letter-spacing:0.1em;">
                        {sl_status}
                    </div>
                </div>
                <div style="font-family:'DM Mono',monospace;font-size:14px;color:var(--text);margin:8px 0;">
                    <strong style="color:var(--red);">⚠ SIGNAL</strong><br>
                    {sl_condition}
                </div>
                <div style="font-family:'DM Mono',monospace;font-size:14px;color:var(--text);margin:8px 0;">
                    <strong style="color:var(--orange);">⏱ PROCÉDURE</strong><br>
                    <span style="color:var(--red);font-weight:bold;">①</span> Signal SL détecté<br>
                    <span style="color:var(--orange);font-weight:bold;">②</span> Attendre la bougie suivante (+1 min)<br>
                    <span style="color:var(--cyan);font-weight:bold;">③</span> À +2 min : reprise du sens → on reste<br>
                    &nbsp;&nbsp;&nbsp;Pas de reprise → on sort
                </div>
                <div style="font-family:'DM Mono',monospace;font-size:13px;color:var(--orange);margin-top:8px;">
                    ⚠ SL SE RÈGLE TOUJOURS<br>
                    Sur la plus petite unité de temps
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Checkbox SL sous la carte
            st.checkbox("✅ Stop-Loss respecté", key="sl_respect_trade")
        
        with col_tp:
            # Récupérer l'état de la checkbox TP
            tp_reached = st.session_state.get("tp_reach_trade", False)
            tp_status = "✅ VALIDÉ" if tp_reached else "⏳ EN ATTENTE"
            tp_status_color = "var(--cyan)" if tp_reached else "var(--orange)"
            
            tp_description = "Quand les prix vont rencontrer les prochains points de friction (bol m1-m5)"
            
            st.markdown(f"""
            <div class="sess-pill" style="border-left:4px solid var(--cyan); border-color:var(--cyan); background:rgba(59,255,160,0.05);">
                <div class="sess-status" style="color:var(--cyan);">🎯 TP</div>
                <div class="sess-name" style="color:var(--cyan);">Objectif de sortie gagnante</div>
                <div style="background:rgba(255,255,255,0.1); border-radius:6px; padding:8px; margin:8px 0; text-align:center;">
                    <div style="font-family:'DM Mono',monospace;font-size:12px;color:{tp_status_color};font-weight:600;letter-spacing:0.1em;">
                        {tp_status}
                    </div>
                </div>
                <div style="font-family:'DM Mono',monospace;font-size:14px;color:var(--text);margin:8px 0;">
                    {tp_description}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Checkbox TP sous la carte
            st.checkbox("🎯 Take Profit atteint", key="tp_reach_trade")
            
            # Timer TP sous la carte TP
            if tp_name:
                m_tp, s_tp = tp_rem // 60, tp_rem % 60
                durations = {"M15": 1800, "M5–M1": 900, "M1": 2700}
                zone_tot = durations.get(tp_name, 1800)
                zone_pct = max(0, min(100, (1 - tp_rem / zone_tot) * 100))
                
                st.markdown(f"""
                <div style="margin: 8px 0; padding: 12px; background: rgba(255,255,255,0.05); 
                            border-radius: 8px; border: 1px solid rgba(59,255,160,0.2);">
                    <div style="color: rgba(59,255,160,0.7); font-family: 'DM Mono', monospace; font-size: 10px; 
                               letter-spacing: 0.15em; margin-bottom: 4px;">ZONE TP ACTIVE</div>
                    <div style="font-family: 'Syne', sans-serif; font-size: 16px; font-weight: 800; 
                               color: #3BFFA0; margin-bottom: 6px;">Boll {tp_name}</div>
                    <div style="background: rgba(255,255,255,0.1); height: 4px; border-radius: 2px; margin-bottom: 6px;">
                        <div style="width: {zone_pct:.1f}%; height: 100%; background: #3BFFA0; 
                                    border-radius: 2px; transition: width 1s linear;"></div>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="color: #8895AA; font-family: 'DM Mono', monospace; font-size: 10px; 
                                   letter-spacing: 0.15em;">TEMPS RESTANT</div>
                        <div style="color: #3BFFA0; font-family: 'DM Mono', monospace; font-size: 20px; 
                                   font-weight: 500;">{m_tp:02d}:{s_tp:02d}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="margin: 8px 0; padding: 12px; background: rgba(255,255,255,0.05); 
                            border-radius: 8px; border: 1px solid rgba(255,184,0,0.2);">
                    <div style="color: #8895AA; font-family: 'DM Mono', monospace; font-size: 10px; 
                               letter-spacing: 0.15em; margin-bottom: 4px;">ZONE TP</div>
                    <div style="color: #8895AA; font-family: 'Syne', sans-serif; font-size: 16px; 
                               font-weight: 700; margin-bottom: 6px;">En attente de zone</div>
                    <div style="color: #8895AA; font-family: 'DM Mono', monospace; font-size: 11px;">
                        Hors plage TP active
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        st.write("---")
        
        # Boutons de sortie
        st.write("**CLÔTURER LA POSITION**")
        
        st.write("---")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Sortie Gagnante", use_container_width=True, key="exit_win"):
                sl_respected = st.session_state.get("sl_respect_trade", False)
                tp_reached = st.session_state.get("tp_reach_trade", False)
                record_trade_exit(True, sl_respected, tp_reached)
                log_event("SORTI_GAGNANT", f"{direction} | {st.session_state.entry_time} → {datetime.now(PARIS).strftime('%H:%M:%S')}")
                st.session_state.trade_active = False
                st.session_state.step = 0
                st.session_state.direction = None
                st.session_state.validated = {}
                st.session_state.entry_time = None
                st.session_state.can_enter = False
                st.rerun()
        with col2:
            if st.button("❌ Sortie Perdante", use_container_width=True, key="exit_loss"):
                sl_respected = st.session_state.get("sl_respect_trade", False)
                tp_reached = st.session_state.get("tp_reach_trade", False)
                record_trade_exit(False, sl_respected, tp_reached)
                log_event("SORTI_PERDANT", f"{direction} | {st.session_state.entry_time} → {datetime.now(PARIS).strftime('%H:%M:%S')}")
                st.session_state.trade_active = False
                st.session_state.step = 0
                st.session_state.direction = None
                st.session_state.validated = {}
                st.session_state.entry_time = None
                st.session_state.can_enter = False
                st.rerun()

    # ──────────────────────────────────────────────────────
    # MODE GUIDAGE — Steps 1 & 2 (avant entrée)
    # ──────────────────────────────────────────────────────
    else:
        # Badge direction + dots
        badge_cls = "dir-achat" if direction == "ACHAT" else "dir-vente"
        badge_sym = "▲ ACHAT"  if direction == "ACHAT" else "▼ VENTE"

        cb, cpd = st.columns([2, 3])
        # ── Helper rule card ──────────────────────────────
        def rule_card(text, color, sk, rk):
            done = is_ok(sk, rk)
            cls  = "done" if done else ""
            icon_c = {"cyan":"var(--cyan)","orange":"var(--orange)","red":"var(--red)"}.get(color,"var(--cyan)")
            icon   = "✓" if done else "·"
            st.markdown(f"""
            <div class="rule {color} {cls}">
                <span class="rule-icon" style="color:{icon_c};">[{icon}]</span>{text}
            </div>
            """, unsafe_allow_html=True)
            if not done:
                if st.button("✓  J'ai vérifié", key=f"v_{sk}_{rk}", use_container_width=True):
                    validate(sk, rk)
                    st.rerun()
            else:
                st.markdown(f'<div class="rule-ok-badge" style="color:{icon_c}88;">Confirmé ✓</div>', unsafe_allow_html=True)

        can_next = False

        # ── STEP 2 ─────────────────────────────────────────
        if step == 2:
            st.markdown("""
            <div class="step-hdr">
                <div class="step-num-badge">Étape 02 / 03</div>
                <div class="step-hdr-title">Discipline</div>
            </div>
            """, unsafe_allow_html=True)
            sk = "s1"
            rule_card("Entrée trop tardive → réduit le gain et augmente potentiellement la perte.", "orange", sk, "r1")
            rule_card("Ne pas respecter le Stop-Loss fixé → INTERDIT.", "red", sk, "r2")
            can_next = all_ok(sk, ["r1", "r2"])
            
            # ── BANNER PROGRESSION VERS ÉTAPE 3 ─────────────────────
            if can_next:
                st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
                st.markdown("""
                <div class="enter-banner">
                    <div class="enter-title">✅ Discipline validée</div>
                    <div class="enter-sub">RÈGLES DE DISCIPLINE VÉRIFIÉES · PASSONS AU TIMING</div>
                </div>
                """, unsafe_allow_html=True)
                
                col_next, col_back = st.columns([2, 1])
                with col_next:
                    if st.button("→ Continuer", use_container_width=True, key="continue_to_timing"):
                        st.session_state.step = 3
                        st.rerun()
                with col_back:
                    if st.button("← Retour", use_container_width=True, key="back_from_discipline"):
                        st.session_state.step = 0
                        st.session_state.direction = None
                        st.session_state.validated = {}
                        st.rerun()

        # ── STEP 3 ─────────────────────────────────────────
        elif step == 3:
            st.markdown("""
            <div class="step-hdr">
                <div class="step-num-badge">Étape 03 / 03</div>
                <div class="step-hdr-title">Quand est-ce que je rentre ?</div>
            </div>
            """, unsafe_allow_html=True)
            sk = "s2"
            rule_card("Entrer au début d'un chandelier M1 quand les 3 temporalités sont sur le même signal.", "orange", sk, "r1")
            if direction == "ACHAT":
                rule_card("ACHAT : Bleue foncée + marron passent AU-DESSUS de la rouge sur 3 unités de temps consécutives.", "cyan", sk, "r2")
            else:
                rule_card("VENTE : Bleue claire + marron passent EN-DESSOUS de la rouge sur 3 unités de temps consécutives.", "red", sk, "r2")
            rule_card("ACCÉLÉRATION : Les deux vidyas se collent → signal d'accélération.", "orange", sk, "r3")
            can_next = all_ok(sk, ["r1", "r2"])

        # ── BANNER ENTRÉE EN POSITION ─────────────────────
        if can_next and step == 3:
            st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
            st.markdown("""
            <div class="enter-banner">
                <div class="enter-title">◈ Toutes les conditions sont réunies</div>
                <div class="enter-sub">CONDITIONS D'ENTRÉE VÉRIFIÉES · PRÊT À OUVRIR LA POSITION</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🚀  VALIDER ET ENTRER EN POSITION", use_container_width=True):
                st.session_state.trade_active = True
                st.session_state.can_enter = True
                st.session_state.entry_time = datetime.now(PARIS).strftime("%H:%M:%S")
                record_trade_entry()  # Enregistrer l'entrée avec les règles validées
                log_event("TRADE_ENTRÉ", f"{direction} | Entrée {st.session_state.entry_time}")
                st.rerun()

        # ── NAVIGATION ────────────────────────────────────
        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
        if not can_next:
            st.markdown('<div class="lock-warn">⚠ Confirme toutes les règles pour continuer</div>', unsafe_allow_html=True)

        n_back, n_mid, n_fwd = st.columns([1, 2, 1])
        with n_back:
            if step > 1:
                if st.button("◀  Retour", use_container_width=True):
                    st.session_state.step -= 1
                    st.rerun()
        with n_fwd:
            if step < 2:
                if st.button("Suivant  ▶", disabled=not can_next, use_container_width=True):
                    st.session_state.step += 1
                    st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("✕  Abandonner", use_container_width=True):
            log_event("DISCIPLINE", "Trade abandonné")
            st.session_state.step = 0
            st.session_state.direction = None
            st.session_state.validated = {}
            st.session_state.can_enter = False
            st.rerun()
