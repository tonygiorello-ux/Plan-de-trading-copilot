<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AVGT — Plan de Trading</title>
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;500;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
<style>
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --bg:        #07070e;
  --surface:   #0f0f1c;
  --border:    #1e1e35;
  --border2:   #2a2a48;
  --green:     #00e5a0;
  --red:       #ff3d5a;
  --gold:      #ffb830;
  --blue:      #4d9fff;
  --text:      #ddddf0;
  --muted:     #5a5a7a;
  --muted2:    #8888aa;
  --font-sans: 'Syne', sans-serif;
  --font-mono: 'JetBrains Mono', monospace;
}

html, body {
  background: var(--bg);
  color: var(--text);
  font-family: var(--font-sans);
  font-size: clamp(17px, 1.8vw, 22px);
  min-height: 100vh;
  line-height: 1.7;
}

.app {
  max-width: 1100px;
  margin: 0 auto;
  padding: 32px 28px 60px;
}

/* HEADER */
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 1px solid var(--border);
  flex-wrap: wrap;
  gap: 12px;
}
.logo { font-size: clamp(32px, 4vw, 46px); font-weight: 800; letter-spacing: -0.02em; color: var(--green); line-height: 1; }
.logo-sub { font-family: var(--font-mono); font-size: clamp(9px, 0.9vw, 11px); color: var(--muted); letter-spacing: 0.15em; margin-top: 6px; }
.header-clock { font-family: var(--font-mono); font-size: clamp(12px, 1.1vw, 15px); color: var(--muted2); letter-spacing: 0.06em; }
.header-clock span { color: var(--muted); margin-right: 8px; }

/* DISCIPLINE */
.discipline {
  background: rgba(255,61,90,0.06);
  border: 1px solid rgba(255,61,90,0.18);
  border-left: 3px solid var(--red);
  border-radius: 12px;
  padding: 14px 22px;
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 28px;
  flex-wrap: wrap;
}
.disc-tag { font-family: var(--font-mono); font-size: 11px; font-weight: 700; letter-spacing: 0.18em; color: var(--red); flex-shrink: 0; }
.disc-items { display: flex; gap: 22px; flex-wrap: wrap; align-items: center; }
.disc-item { font-size: clamp(14px, 1.4vw, 17px); color: #c0c0d8; display: flex; align-items: center; gap: 8px; }
.disc-sep { width: 1px; height: 26px; background: rgba(255,61,90,0.2); }

/* SECTION LABEL */
.section-label {
  font-family: var(--font-mono);
  font-size: 11px;
  letter-spacing: 0.2em;
  color: var(--muted);
  margin-bottom: 12px;
  padding-left: 2px;
}

/* SESSION CARDS */
.sessions-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
  margin-bottom: 32px;
}
@media (max-width: 640px) { .sessions-row { grid-template-columns: 1fr; } }

.sess-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 20px 22px;
  position: relative;
  overflow: hidden;
  transition: border-color 0.35s, background 0.35s;
}
.sess-card::after {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 16px;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.4s;
}
.sess-card.state-next { border-color: rgba(0,229,160,0.3); }
.sess-card.state-next::after { background: radial-gradient(ellipse at 50% -10%, rgba(0,229,160,0.07) 0%, transparent 65%); opacity: 1; }
.sess-card.state-live { border-color: rgba(255,184,48,0.45); background: #0f0f19; }
.sess-card.state-live::after { background: radial-gradient(ellipse at 50% -10%, rgba(255,184,48,0.1) 0%, transparent 65%); opacity: 1; }

.sess-card-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 14px;
}
.sess-name { font-family: var(--font-mono); font-size: clamp(22px, 2.6vw, 32px); font-weight: 700; color: var(--text); letter-spacing: 0.04em; line-height: 1; }
.sess-card.state-live .sess-name { color: var(--gold); }
.sess-card.state-next .sess-name { color: var(--green); }

.sess-badge {
  font-family: var(--font-mono);
  font-size: clamp(10px, 0.9vw, 12px);
  font-weight: 700;
  letter-spacing: 0.12em;
  padding: 4px 9px;
  border-radius: 100px;
  display: flex;
  align-items: center;
  gap: 5px;
  opacity: 0;
  transition: opacity 0.3s;
}
.sess-card.state-live .sess-badge { opacity: 1; background: rgba(255,184,48,0.12); color: var(--gold); border: 1px solid rgba(255,184,48,0.3); }
.sess-card.state-next .sess-badge { opacity: 1; background: rgba(0,229,160,0.08); color: var(--green); border: 1px solid rgba(0,229,160,0.2); }

.pulse { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; display: inline-block; }
.state-live .pulse { background: var(--gold); animation: blink 0.8s ease-in-out infinite; }
.state-next .pulse { background: var(--green); animation: blink 1.4s ease-in-out infinite; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.1} }

.sess-hours { font-family: var(--font-mono); font-size: clamp(14px, 1.4vw, 18px); color: var(--muted2); letter-spacing: 0.03em; margin-bottom: 3px; }
.sess-market { font-size: clamp(11px, 1vw, 13px); color: var(--muted); font-family: var(--font-mono); letter-spacing: 0.06em; }

.sess-timer { margin-top: 16px; padding-top: 14px; border-top: 1px solid var(--border); display: none; }
.sess-card.state-live .sess-timer,
.sess-card.state-next .sess-timer { display: block; }

.sess-timer-label { font-family: var(--font-mono); font-size: clamp(10px, 0.9vw, 12px); letter-spacing: 0.14em; margin-bottom: 4px; }
.state-live .sess-timer-label { color: var(--gold); }
.state-next .sess-timer-label { color: var(--green); }

.sess-timer-value { font-family: var(--font-mono); font-size: clamp(36px, 4vw, 52px); font-weight: 700; line-height: 1; letter-spacing: 0.04em; }
.state-live .sess-timer-value { color: var(--gold); }
.state-next .sess-timer-value { color: var(--green); }

/* RULES */
.rules-stack { display: flex; flex-direction: column; gap: 14px; }

.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 28px 32px;
  position: relative;
  overflow: hidden;
  transition: border-color 0.2s;
}
.card:hover { border-color: var(--border2); }
.card-accent { position: absolute; top: 0; left: 0; right: 0; height: 2px; border-radius: 16px 16px 0 0; }

.card-header { display: flex; align-items: baseline; gap: 14px; margin-bottom: 22px; }
.card-eyebrow { font-family: var(--font-mono); font-size: clamp(10px, 0.9vw, 12px); letter-spacing: 0.14em; color: var(--muted); flex-shrink: 0; }
.card-title { font-size: clamp(22px, 2.3vw, 30px); font-weight: 800; letter-spacing: -0.01em; }
.card-title.green { color: var(--green); }
.card-title.red   { color: var(--red); }
.card-title.gold  { color: var(--gold); }

.rules-body { display: flex; flex-direction: column; gap: 16px; }
.rule { display: flex; align-items: flex-start; gap: 14px; font-size: clamp(16px, 1.6vw, 19px); line-height: 1.65; color: #a8a8c8; }

.dot { width: 9px; height: 9px; border-radius: 50%; margin-top: 8px; flex-shrink: 0; }
.dot-green   { background: var(--green); box-shadow: 0 0 6px rgba(0,229,160,0.5); }
.dot-red     { background: var(--red);   box-shadow: 0 0 6px rgba(255,61,90,0.5); }
.dot-gold    { background: var(--gold);  box-shadow: 0 0 6px rgba(255,184,48,0.5); }
.dot-blue    { background: var(--blue); }
.dot-neutral { background: var(--muted); }

hl { color: var(--text); font-weight: 700; }

.badge { display: inline-flex; align-items: center; font-family: var(--font-mono); font-size: clamp(12px, 1.1vw, 14px); font-weight: 700; padding: 3px 10px; border-radius: 5px; letter-spacing: 0.04em; vertical-align: middle; }
.badge-buy  { background: rgba(0,229,160,0.1);  color: var(--green); border: 1px solid rgba(0,229,160,0.25); }
.badge-sell { background: rgba(255,61,90,0.1);  color: var(--red);   border: 1px solid rgba(255,61,90,0.25); }
.badge-accel{ background: rgba(255,184,48,0.1); color: var(--gold);  border: 1px solid rgba(255,184,48,0.25); }

.tf-row { display: flex; align-items: center; gap: 10px; padding-top: 18px; margin-top: 18px; border-top: 1px solid var(--border); flex-wrap: wrap; }
.tf-pill { font-family: var(--font-mono); font-size: clamp(13px, 1.3vw, 16px); font-weight: 700; padding: 7px 18px; border-radius: 8px; border: 1px solid; }
.tf-m1  { color: #b197fc; border-color: rgba(177,151,252,0.35); background: rgba(177,151,252,0.08); }
.tf-m5  { color: var(--blue); border-color: rgba(77,159,255,0.35); background: rgba(77,159,255,0.08); }
.tf-m15 { color: var(--green); border-color: rgba(0,229,160,0.35); background: rgba(0,229,160,0.08); }
.tf-plus { color: var(--muted2); font-family: var(--font-mono); font-size: clamp(16px, 1.5vw, 20px); }
.tf-caption { font-size: clamp(13px, 1.3vw, 16px); color: var(--muted2); margin-left: 4px; }

.sl-protocol { margin-top: 0; border: 1px solid rgba(255,184,48,0.2); border-radius: 0 0 8px 8px; overflow: hidden; }
.sl-row { display: flex; align-items: center; padding: 13px 18px; gap: 16px; border-bottom: 1px solid rgba(255,184,48,0.12); font-size: clamp(14px, 1.4vw, 17px); color: #9090b0; }
.sl-row:last-child { border-bottom: none; }
.sl-t { font-family: var(--font-mono); font-size: clamp(12px, 1.1vw, 14px); font-weight: 700; color: var(--gold); min-width: 58px; flex-shrink: 0; }
.sl-or { font-family: var(--font-mono); font-size: clamp(12px, 1.1vw, 14px); color: var(--muted); padding: 0 6px; }

.rebond-block { margin-top: 20px; }
.rebond-header {
  display: flex;
  align-items: center;
  gap: 9px;
  font-family: var(--font-mono);
  font-size: clamp(11px, 1vw, 13px);
  font-weight: 700;
  letter-spacing: 0.1em;
  color: var(--gold);
  background: rgba(255,184,48,0.08);
  border: 1px solid rgba(255,184,48,0.25);
  border-bottom: none;
  border-radius: 8px 8px 0 0;
  padding: 10px 18px;
  text-transform: uppercase;
}
.rebond-icon { font-size: clamp(13px, 1.2vw, 15px); }

.friction-label { display: inline-block; font-family: var(--font-mono); font-size: clamp(12px, 1.1vw, 14px); font-weight: 700; color: var(--gold); letter-spacing: 0.08em; padding: 5px 14px; background: rgba(255,184,48,0.08); border-radius: 6px; border: 1px solid rgba(255,184,48,0.2); margin-top: 8px; }

/* FOREXFACTORY CARD */
.ff-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 16px 22px;
  margin-bottom: 14px;
  text-decoration: none;
  transition: border-color 0.25s, background 0.25s;
  cursor: pointer;
  flex-wrap: wrap;
}
.ff-card:hover {
  border-color: rgba(77,159,255,0.4);
  background: rgba(77,159,255,0.04);
}
.ff-left { display: flex; align-items: center; gap: 14px; }
.ff-icon { font-size: clamp(20px, 2vw, 24px); line-height: 1; flex-shrink: 0; }
.ff-title { font-size: clamp(15px, 1.5vw, 18px); font-weight: 700; color: var(--text); margin-bottom: 2px; }
.ff-sub { font-family: var(--font-mono); font-size: clamp(10px, 1vw, 12px); color: var(--muted2); letter-spacing: 0.04em; }
.ff-right { display: flex; align-items: center; gap: 8px; flex-shrink: 0; }
.ff-url { font-family: var(--font-mono); font-size: clamp(11px, 1vw, 13px); color: var(--blue); letter-spacing: 0.04em; }
.ff-arrow { width: 18px; height: 18px; color: var(--blue); flex-shrink: 0; }

/* FOOTER */
.footer { display: flex; align-items: center; justify-content: space-between; margin-top: 24px; padding-top: 16px; border-top: 1px solid var(--border); gap: 10px; flex-wrap: wrap; }
.footer-ts { font-family: var(--font-mono); font-size: clamp(11px, 1vw, 13px); color: var(--muted); letter-spacing: 0.06em; }
.live-dot { width: 5px; height: 5px; border-radius: 50%; background: var(--green); display: inline-block; margin-right: 7px; animation: blink 2s ease-in-out infinite; }
</style>
</head>
<body>
<div class="app">

  <div class="header">
    <div>
      <div class="logo">AVGT</div>
    </div>
    <div class="header-clock"><span>PARIS</span><span id="hdr-clock">--:--:--</span></div>
  </div>

  <div class="section-label">Sessions actives</div>
  <div class="sessions-row">

    <div class="sess-card" id="card-EU">
      <div class="sess-card-top">
        <div class="sess-name">EU</div>
        <div class="sess-badge"><span class="pulse"></span><span class="badge-txt">EN COURS</span></div>
      </div>
      <div class="sess-hours">09h45 – 11h15</div>
      <div class="sess-market">Heure de Paris</div>
      <div class="sess-timer">
        <div class="sess-timer-label" id="lbl-EU">FIN DANS</div>
        <div class="sess-timer-value" id="tmr-EU">--:--</div>
      </div>
    </div>

    <div class="sess-card" id="card-US1">
      <div class="sess-card-top">
        <div class="sess-name">US1</div>
        <div class="sess-badge"><span class="pulse"></span><span class="badge-txt">EN COURS</span></div>
      </div>
      <div class="sess-hours">15h45 – 17h15</div>
      <div class="sess-market">Heure de Paris</div>
      <div class="sess-timer">
        <div class="sess-timer-label" id="lbl-US1">FIN DANS</div>
        <div class="sess-timer-value" id="tmr-US1">--:--</div>
      </div>
    </div>

    <div class="sess-card" id="card-US2">
      <div class="sess-card-top">
        <div class="sess-name">US2</div>
        <div class="sess-badge"><span class="pulse"></span><span class="badge-txt">EN COURS</span></div>
      </div>
      <div class="sess-hours">19h30 – 21h00</div>
      <div class="sess-market">Heure de Paris</div>
      <div class="sess-timer">
        <div class="sess-timer-label" id="lbl-US2">FIN DANS</div>
        <div class="sess-timer-value" id="tmr-US2">--:--</div>
      </div>
    </div>

  </div>

  <a href="https://www.forexfactory.com/" target="_blank" class="ff-card">
    <div class="ff-left">
      <div class="ff-icon">📅</div>
      <div>
        <div class="ff-title">Annonces économiques</div>
        <div class="ff-sub">Vérifier le calendrier avant chaque session</div>
      </div>
    </div>
    <div class="ff-right">
      <span class="ff-url">forexfactory.com</span>
      <svg class="ff-arrow" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M3 8h10M9 4l4 4-4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
    </div>
  </a>

  <div class="discipline">
    <div class="disc-tag">DISCIPLINE</div>
    <div class="disc-items">
      <div class="disc-item">🛡&nbsp; Entrée trop tardive → gain réduit, risque augmenté</div>
      <div class="disc-sep"></div>
      <div class="disc-item">⛔&nbsp; <b style="color:var(--red)">Ne pas respecter le Stop-Loss → INTERDIT</b></div>
    </div>
  </div>

  <div class="section-label">Règles de trading</div>
  <div class="rules-stack">

    <div class="card">
      <div class="card-accent" style="background:var(--green)"></div>
      <div class="card-header">
        <div class="card-title green">⚡ Quand entrer ?</div>
      </div>
      <div class="rules-body">
        <div class="rule"><div class="dot dot-blue"></div><div>Entrée sur <hl>clôture M1</hl> quand les 3 temporalités sont alignées (toutes buy ou toutes sell)</div></div>
        <div class="rule"><div class="dot dot-green"></div><div><span class="badge badge-buy">BUY</span>&nbsp; Bleue foncée + Marron passent <hl>au-dessus</hl> de la Rouge sur 3 TF consécutifs</div></div>
        <div class="rule"><div class="dot dot-red"></div><div><span class="badge badge-sell">SELL</span>&nbsp; Bleue claire + Marron passent <hl>en-dessous</hl> de la Rouge sur 3 TF consécutifs</div></div>
        <div class="rule"><div class="dot dot-gold"></div><div><span class="badge badge-accel">ACCÉL</span>&nbsp; VIDYAs collées = signal d'accélération</div></div>
      </div>
      <div class="tf-row">
        <div class="tf-pill tf-m1">M1</div><span class="tf-plus">+</span>
        <div class="tf-pill tf-m5">M5</div><span class="tf-plus">+</span>
        <div class="tf-pill tf-m15">M15</div>
        <span class="tf-caption">→ 3 TF alignés requis</span>
      </div>
    </div>

    <div class="card">
      <div class="card-accent" style="background:var(--red)"></div>
      <div class="card-header">
        <div class="card-title red">🛑 Stop-Loss</div>
      </div>
      <div class="rules-body">
        <div class="rule"><div class="dot dot-neutral"></div><div>SL réglé sur la <hl>plus petite TF</hl> de la trinité sélectionnée</div></div>
        <div class="rule"><div class="dot dot-green"></div><div><span class="badge badge-buy">BUY</span>&nbsp; Bleue foncée + Gold croisent <hl>en-dessous</hl> de la Rouge → SL</div></div>
        <div class="rule"><div class="dot dot-red"></div><div><span class="badge badge-sell">SELL</span>&nbsp; Bleue claire + Gold croisent <hl>au-dessus</hl> de la Rouge → SL</div></div>
      </div>
      <div class="rebond-block">
        <div class="rebond-header">
          <span class="rebond-icon">⚠</span>
          Rebond mécanique
        </div>
        <div class="sl-protocol">
          <div class="sl-row"><span class="sl-t">+0 min</span><span>Croisement dans le mauvais sens</span></div>
          <div class="sl-row"><span class="sl-t">+1 min</span><span>Attendre la clôture de la bougie suivante</span></div>
          <div class="sl-row"><span class="sl-t">+2 min</span><span>Reprise du sens → on reste <span class="sl-or">|</span> Sinon → on sort</span></div>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="card-accent" style="background:var(--green)"></div>
      <div class="card-header">
        <div class="card-title green">🎯 Take-Profit</div>
      </div>
      <div class="rules-body">
        <div class="rule"><div class="dot dot-green"></div><div>TP quand les prix atteignent les prochains <hl>points de friction</hl></div></div>
      </div>
      <div><span class="friction-label" style="color:var(--green);background:rgba(0,229,160,0.08);border-color:rgba(0,229,160,0.2)">POINTS DE FRICTION</span></div>
    </div>

  </div>

  <div class="footer">
    <div class="footer-ts"><span class="live-dot"></span><span id="footer-time">--:--:--</span>&nbsp;·&nbsp; Heure Paris</div>

  </div>

</div>
<script>
const PARIS_TZ = 'Europe/Paris';
const SESSIONS = [
  { id: 'EU',  start: [9,45],  end: [11,15] },
  { id: 'US1', start: [15,45], end: [17,15] },
  { id: 'US2', start: [19,30], end: [21,0]  },
];

function nowParis() {
  const s = new Date().toLocaleString('en-US', {
    timeZone: PARIS_TZ, hour12: false,
    hour: '2-digit', minute: '2-digit', second: '2-digit'
  });
  const [h, m, sec] = s.split(':').map(Number);
  return { t: h*3600 + m*60 + sec, hms: s };
}

function fmt(s) {
  if (s == null || s < 0) return '--:--';
  const h = Math.floor(s/3600), m = Math.floor((s%3600)/60), sec = s%60;
  if (h > 0) return `${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}:${String(sec).padStart(2,'0')}`;
  return `${String(m).padStart(2,'0')}:${String(sec).padStart(2,'0')}`;
}

function tick() {
  const { t, hms } = nowParis();
  document.getElementById('hdr-clock').textContent = hms;
  document.getElementById('footer-time').textContent = hms;

  let liveId = null, nextId = null;
  for (const s of SESSIONS) {
    const st = s.start[0]*3600 + s.start[1]*60;
    const en = s.end[0]*3600   + s.end[1]*60;
    if (t >= st && t <= en) { liveId = s.id; break; }
  }
  if (!liveId) {
    for (const s of SESSIONS) {
      if (t < s.start[0]*3600 + s.start[1]*60) { nextId = s.id; break; }
    }
  }

  for (const s of SESSIONS) {
    const card  = document.getElementById('card-' + s.id);
    const lbl   = document.getElementById('lbl-' + s.id);
    const tmr   = document.getElementById('tmr-' + s.id);
    const badge = card.querySelector('.badge-txt');
    const st = s.start[0]*3600 + s.start[1]*60;
    const en = s.end[0]*3600   + s.end[1]*60;

    if (s.id === liveId) {
      card.className = 'sess-card state-live';
      badge.textContent = 'EN COURS';
      lbl.textContent = 'FIN DANS';
      tmr.textContent = fmt(en - t);
    } else if (s.id === nextId) {
      card.className = 'sess-card state-next';
      badge.textContent = 'PROCHAINE';
      lbl.textContent = 'DÉBUT DANS';
      tmr.textContent = fmt(st - t);
    } else {
      card.className = 'sess-card';
      tmr.textContent = '--:--';
    }
  }
}

tick();
setInterval(tick, 1000);
</script>
</body>
</html>
