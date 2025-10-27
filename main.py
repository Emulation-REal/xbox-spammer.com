from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import aiohttp
import asyncio
import os
import json

# === EMBEDDED CSS (TABS + MODS UI — NEON RED PROFESSIONALISM) ===
INLINE_CSS = """
<style>
body { font-family: 'Courier New', monospace; background: black; color: #ef4444; overflow-x: hidden; margin: 0; padding: 0; }
#matrix { position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: -1; }
.container { max-width: 800px; margin: 0 auto; padding: 20px; }
h1 { font-size: 3em; text-align: center; margin-bottom: 20px; font-family: 'Orbitron', sans-serif; animation: glitch 2s infinite; position: relative; }
h1::before, h1::after { content: attr(data-text); position: absolute; top: 0; left: 0; width: 100%; height: 100%; }
h1::before { animation: glitch-1 0.5s infinite; clip-path: polygon(0 0, 100% 0, 100% 45%, 0 45%); }
h1::after { animation: glitch-2 0.5s infinite; clip-path: polygon(0 60%, 100% 60%, 100% 100%, 0 100%); }
@keyframes glitch { 0%, 100% { text-shadow: 2px 0 #ff0044, -2px 0 #00ffcc; } 50% { text-shadow: -2px 0 #ff0044, 2px 0 #00ffcc; } }
@keyframes glitch-1 { 0% { transform: translate(0); } 20% { transform: translate(-2px, 2px); } 40% { transform: translate(2px, -2px); } }
@keyframes glitch-2 { 0% { transform: translate(0); } 20% { transform: translate(2px, -2px); } 40% { transform: translate(-2px, 2px); } }

/* TAB NAVIGATION — PRO AF */
.tab-nav { display: flex; background: #111; border: 2px solid #ef4444; border-radius: 8px; overflow: hidden; margin-bottom: 20px; box-shadow: 0 0 20px rgba(239, 68, 68, 0.5); }
.tab-btn { flex: 1; padding: 15px; background: #222; border: none; color: #ef4444; font-weight: bold; cursor: pointer; transition: all 0.3s; }
.tab-btn.active { background: #990000; box-shadow: inset 0 0 10px #ff0000; }
.tab-btn:hover { background: #cc0000; color: white; }

/* TAB CONTENT */
.tab-content { display: none; background: #111; padding: 20px; border: 2px solid #ef4444; border-radius: 8px; box-shadow: 0 0 20px rgba(239, 68, 68, 0.5); margin-bottom: 20px; }
.tab-content.active { display: block; }
.party-form, .friend-form, .presence-form, .stats-form, .nuke-form { background: #111; padding: 20px; border: 2px solid #ff6600; border-radius: 8px; box-shadow: 0 0 20px rgba(255, 102, 0, 0.5); margin-top: 10px; }
input, button, input[type="range"], select { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ef4444; border-radius: 4px; background: #222; color: #ef4444; font-family: inherit; }
input[type="range"] { padding: 5px; }
#delay-value, #party-delay-value { display: block; text-align: center; color: #ff0000; font-weight: bold; }
input:focus { outline: none; border-color: #ff0000; box-shadow: 0 0 10px #ff0000; }
button { background: #990000; border: 2px solid #ff0000; cursor: pointer; font-weight: bold; transition: all 0.3s; }
button:hover { background: #cc0000; box-shadow: 0 0 15px #ff0000; }
button:disabled { background: #333; cursor: not-allowed; }
#progress { display: none; background: #111; padding: 15px; border: 1px solid #ef4444; border-radius: 4px; margin: 10px 0; }
#progress-bar { width: 100%; height: 20px; background: #333; border-radius: 10px; overflow: hidden; }
#progress-fill { height: 100%; background: linear-gradient(to right, #ef4444, #ff0000); transition: width 0.3s; width: 0%; }
#logs { background: #111; padding: 15px; border: 1px solid #ef4444; border-radius: 4px; height: 200px; overflow-y: auto; font-size: 12px; margin-top: 10px; }
.log-entry { margin: 2px 0; animation: fadeIn 0.3s; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(-5px); } to { opacity: 1; transform: translateY(0); } }
.footer { text-align: center; color: #888; font-size: 12px; margin-top: 20px; }
.preset-select { width: auto; margin: 10px 0; padding: 5px; }
</style>
"""

# === EMBEDDED MATRIX JS (INLINE — SAME OL' RAIN) ===
INLINE_MATRIX_JS = """
<script>
const canvas = document.createElement('canvas');
canvas.id = 'matrix';
document.body.appendChild(canvas);
const ctx = canvas.getContext('2d');
function resize() { canvas.width = window.innerWidth; canvas.height = window.innerHeight; }
resize(); window.addEventListener('resize', resize);
const matrix = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789@#$%^&*()*&^%+-/~{[|`]}';
const fontSize = 14; let columns = canvas.width / fontSize;
const drops = Array(Math.floor(columns)).fill(1);
function draw() {
  ctx.fillStyle = 'rgba(0, 0, 0, 0.05)'; ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = '#ef4444'; ctx.font = fontSize + 'px monospace';
  for (let i = 0; i < drops.length; i++) {
    const text = matrix[Math.floor(Math.random() * matrix.length)];
    ctx.fillText(text, i * fontSize, drops[i] * fontSize);
    if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) drops[i] = 0;
    drops[i]++;
  }
}
setInterval(draw, 50);

// KONAMI EGG — TYPE UP UP DOWN DOWN LEFT RIGHT LEFT RIGHT B A
let konami = [38,38,40,40,37,39,37,39,66,65];
let kIndex = 0;
document.addEventListener('keydown', (e) => {
  if (e.keyCode === konami[kIndex]) kIndex++;
  else kIndex = 0;
  if (kIndex === konami.length) { alert('NUKE MODE UNLOCKED! (jk, spam harder)'); kIndex = 0; }
});
</script>
"""

# === EMBEDDED APP JS (TABS + MULTI-MOD SWITCHER + PRESETS) ===
INLINE_APP_JS = """
<script>
let running = false; let pollInterval; let currentMode = 'message';
const tabs = document.querySelectorAll('.tab-btn');
const contents = document.querySelectorAll('.tab-content');
const messageForm = document.querySelector('#message-form');
const partyForm = document.querySelector('#party-form');
const friendForm = document.querySelector('#friend-form');
const presenceForm = document.querySelector('#presence-form');
const statsForm = document.querySelector('#stats-form');
const nukeForm = document.querySelector('#nuke-form');
const startBtn = document.querySelector('#start-btn');
const stopBtn = document.querySelector('#stop-btn');
const progressDiv = document.getElementById('progress');
const progressFill = document.getElementById('progress-fill');
const logsDiv = document.getElementById('logs');
const delaySlider = document.querySelector('#delay-slider');
const delayValue = document.getElementById('delay-value');
const authKeyInput = document.querySelector('input[name="auth_key"]');

// TAB SWITCHER
tabs.forEach(tab => {
  tab.addEventListener('click', () => {
    tabs.forEach(t => t.classList.remove('active'));
    contents.forEach(c => c.classList.remove('active'));
    tab.classList.add('active');
    document.getElementById(tab.dataset.tab).classList.add('active');
    currentMode = tab.dataset.tab;
  });
});

// SLIDER UPDATES
delaySlider.addEventListener('input', (e) => { delayValue.textContent = e.target.value + 's'; });

// PRESET MESSAGES
const presetSelect = document.querySelector('#preset-select');
presetSelect.addEventListener('change', (e) => {
  const presets = { 'roast': 'Your K/D is ass, noob!', 'troll': 'Join my carry party? LOL', 'ez': 'GG EZ, uninstall plz' };
  document.querySelector('input[name="message"]').value = presets[e.target.value] || '';
});

// FORM SUBMITS (MULTI-MODE)
[messageForm, partyForm, friendForm, presenceForm, statsForm, nukeForm].forEach(form => {
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (!authKeyInput.value) { alert('API Key? You forgetting your dick too?'); return; }
    running = true;
    startBtn.disabled = true;
    startBtn.textContent = 'NUKING...';
    stopBtn.style.display = 'block';
    addLog(`🚀 ${currentMode.toUpperCase()} MODE ACTIVATED`);
    const formData = new FormData(form);
    formData.append('mode', currentMode);
    const res = await fetch('/start', { method: 'POST', body: formData });
    const data = await res.json();
    if (data.error) { alert(data.error); resetUI(); return; }
    pollStatus();
  });
});

stopBtn.addEventListener('click', async () => {
  await fetch('/stop', { method: 'POST' });
  running = false;
  resetUI();
});

function resetUI() {
  running = false;
  startBtn.disabled = false;
  startBtn.textContent = 'START NUKE';
  stopBtn.style.display = 'none';
  progressDiv.style.display = 'none';
  if (pollInterval) clearInterval(pollInterval);
}

function pollStatus() {
  pollInterval = setInterval(async () => {
    if (!running) { clearInterval(pollInterval); return; }
    const res = await fetch('/status');
    const data = await res.json();
    document.getElementById('progress-text').textContent = data.progress > 0 ? Math.round(data.progress) + '%' : '∞';
    progressFill.style.width = data.progress + '%';
    document.getElementById('cooldown').textContent = data.cooldown;
    if (data.cooldown > 0) document.getElementById('cooldown-row').style.display = 'block';
    else document.getElementById('cooldown-row').style.display = 'none';
    logsDiv.innerHTML = data.logs.slice(-20).map(log => `<div class="log-entry">${log}</div>`).join('');
    if (!data.active) resetUI();
  }, 1000);
}

function addLog(msg) { 
  logsDiv.innerHTML += `<div class="log-entry">${msg}</div>`; 
  logsDiv.scrollTop = logsDiv.scrollHeight; 
  progressDiv.style.display = 'block';
}

// DEFAULT TAB
document.querySelector('[data-tab="message"]').click();
</script>
"""

# === FULL HTML (TABS + 6 MOD PANELS + PRESETS) ===
FULL_HTML = f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>XBOX SPAMMER PRO v3.0</title>
  <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@900&display=swap" rel="stylesheet">
  {INLINE_CSS}
</head>
<body>
  {INLINE_MATRIX_JS}
  <div class="container">
    <h1 data-text="XBOX SPAMMER PRO v3.0">XBOX SPAMMER PRO v3.0</h1>
    
    <!-- TAB NAV -->
    <div class="tab-nav">
      <button class="tab-btn active" data-tab="message">💬 Message Spam</button>
      <button class="tab-btn" data-tab="party">🪅 Party Invite</button>
      <button class="tab-btn" data-tab="friend">👥 Friend Request</button>
      <button class="tab-btn" data-tab="presence">👁️ Presence Poll</button>
      <button class="tab-btn" data-tab="stats">📊 Stats Viewer</button>
      <button class="tab-btn" data-tab="nuke">💣 Nuke Mode</button>
    </div>
    
    <!-- MESSAGE TAB -->
    <div id="message" class="tab-content active">
      <form id="message-form">
        <input type="password" name="auth_key" placeholder="🔑 xbl.io API Key" required>
        <input type="text" name="gamertag" placeholder="🎮 Target Gamertag" required>
        <select id="preset-select" class="preset-select">
          <option value="">Custom Message</option>
          <option value="roast">Roast Kit</option>
          <option value="troll">Troll Pack</option>
          <option value="ez">EZ Mode</option>
        </select>
        <input type="text" name="message" placeholder="💬 Spam Text" value="GG EZ">
        <label>Delay: <input type="range" id="delay-slider" name="delay" min="0.5" max="5" step="0.1" value="1.3"></label>
        <span id="delay-value">1.3s</span>
        <input type="number" name="amount" placeholder="🔢 Amount (0=∞)" min="0" value="50">
        <button type="submit" id="start-btn">🚀 NUKE 'EM</button>
      </form>
    </div>
    
    <!-- PARTY TAB -->
    <div id="party" class="tab-content">
      <form id="party-form" class="party-form">
        <input type="password" name="auth_key" placeholder="🔑 API Key (reuse)">
        <input type="text" name="gamertag" placeholder="🎮 Target">
        <label>Invite Delay: <input type="range" name="party_delay" min="0.5" max="5" step="0.1" value="2.0"></label>
        <span id="party-delay-value">2.0s</span>
        <input type="number" name="party_amount" placeholder="🔢 Invites (0=∞)" min="0" value="10">
        <button type="submit">🎉 RAID PARTY</button>
      </form>
    </div>
    
    <!-- FRIEND TAB -->
    <div id="friend" class="tab-content">
      <form id="friend-form" class="friend-form">
        <input type="password" name="auth_key" placeholder="🔑 API Key">
        <input type="text" name="gamertag" placeholder="🎮 Target to Friend-Bomb">
        <label>Request Delay: <input type="range" name="friend_delay" min="1" max="10" step="0.5" value="3"></label>
        <input type="number" name="friend_amount" placeholder="🔢 Requests (0=∞)" min="0" value="20">
        <button type="submit">👥 FRIEND FLOOD</button>
      </form>
    </div>
    
    <!-- PRESENCE TAB -->
    <div id="presence" class="tab-content">
      <form id="presence-form" class="presence-form">
        <input type="password" name="auth_key" placeholder="🔑 API Key">
        <input type="text" name="gamertag" placeholder="🎮 Stalk Target">
        <input type="number" name="poll_interval" placeholder="Poll every Xs" value="30" min="10">
        <button type="submit">👁️ LIVE STALK MODE</button>
      </form>
    </div>
    
    <!-- STATS TAB -->
    <div id="stats" class="tab-content">
      <form id="stats-form" class="stats-form">
        <input type="password" name="auth_key" placeholder="🔑 API Key">
        <input type="text" name="gamertag" placeholder="🎮 Pull Stats">
        <button type="submit">📊 FETCH K/D ROAST</button>
      </form>
    </div>
    
    <!-- NUKE TAB -->
    <div id="nuke" class="tab-content">
      <form id="nuke-form" class="nuke-form">
        <input type="password" name="auth_key" placeholder="🔑 API Key">
        <input type="text" name="gamertag" placeholder="🎮 TOTAL NUKE TARGET">
        <input type="number" name="nuke_duration" placeholder="Nuke for Xs" value="60" min="30">
        <button type="submit">💣 FULL NUKE (ALL MODS)</button>
      </form>
    </div>
    
    <button type="button" id="stop-btn" style="display: none; width: 100%; margin: 10px 0;">🛑 ABORT MISSION</button>
    
    <div id="progress">
      <div style="display: flex; justify-content: space-between; margin-bottom: 10px; font-size: 14px;">
        <span>NUKE Progress</span>
        <span id="progress-text">0%</span>
      </div>
      <div id="progress-bar"><div id="progress-fill"></div></div>
      <p id="cooldown-row" style="text-align: center; margin-top: 10px; font-size: 12px; display: none;">
        ⏰ Cooldown: <span id="cooldown">0</span>s
      </p>
    </div>
    <div id="logs"></div>
    <p class="footer">⚡ xbl.io Powered | Konami Code for Easter Eggs | Don't Cry When Banned</p>
  </div>
  {INLINE_APP_JS}
</body>
</html>
"""

# === AUTO-CREATE ===
os.makedirs("static", exist_ok=True)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# === GLOBAL STATE ===
spammer_task = None
spammer_active = False
log_messages = []
progress = 0
cooldown = 0
current_mode = 'message'

# === API FUNCTIONS (EXPANDED FOR MODS) ===
async def convert_gamertag_to_xuid(session, gamertag, auth_key):
    url = f"https://xbl.io/api/v2/search/{gamertag}"
    headers = {"x-authorization": auth_key, "accept": "*/*", "Content-Type": "application/json"}
    async with session.get(url, headers=headers) as resp:
        if resp.status != 200:
            raise Exception(f"Search failed: {resp.status}")
        data = await resp.json()
        return data["people"][0]["xuid"]

async def api_call(session, method, url, payload=None, auth_key=None, is_json=True):
    headers = {"x-authorization": auth_key, "accept": "*/*", "Content-Type": "application/json"}
    if method == 'GET':
        async with session.get(url, headers=headers) as resp:
            return await handle_response(resp, is_json)
    else:
        async with session.post(url, json=payload, headers=headers) as resp:
            return await handle_response(resp, is_json)

async def handle_response(resp, is_json):
    if resp.status == 429:
        return {"limitType": "rate_limit"}
    content_type = resp.headers.get("content-type", "")
    if "application/json" in content_type and is_json:
        return await resp.json()
    else:
        text = await resp.text()
        raise Exception(f"Non-JSON: {resp.status} - {text[:100]}...")

# === MOD-SPECIFIC CALLS ===
async def send_message(session, xuid, message, auth_key):
    url = "https://xbl.io/api/v2/conversations"
    payload = {"message": message, "xuid": xuid}
    return await api_call(session, 'POST', url, payload, auth_key)

async def send_party_invite(session, xuid, auth_key):
    url = "https://xbl.io/api/v2/sessions/invite"  # Plausible; mod if 404
    payload = {"xuid": xuid}
    return await api_call(session, 'POST', url, payload, auth_key)

async def send_friend_request(session, xuid, auth_key):
    url = "https://xbl.io/api/v2/friends/add"
    payload = {"xuid": xuid}
    return await api_call(session, 'POST', url, payload, auth_key)

async def get_presence(session, xuid, auth_key):
    url = f"https://xbl.io/api/v2/presence/{xuid}"
    return await api_call(session, 'GET', url, auth_key=auth_key)

async def get_stats(session, xuid, auth_key):
    url = f"https://xbl.io/api/v2/player/stats/{xuid}"
    return await api_call(session, 'GET', url, auth_key=auth_key)

# === SPAM WORKER (MOD-AGNOSTIC + BACKOFF) ===
async def spam_worker(gamertag: str, message: str, amount: int, auth_key: str, delay: float, mode: str):
    global spammer_active, log_messages, progress, cooldown, current_mode
    current_mode = mode
    async with aiohttp.ClientSession() as session:
        try:
            log_messages.append(f"🔍 Resolving {gamertag}...")
            xuid = await convert_gamertag_to_xuid(session, gamertag, auth_key)
            log_messages.append(f"✅ XUID Locked: {xuid}")

            sent = 0
            target = amount if amount > 0 else float('inf')
            backoff = 1  # Exponential backoff multiplier

            while sent < target and spammer_active:
                try:
                    result = await run_mod_call(session, xuid, message, auth_key, mode)
                    sent += 1
                    progress = min((sent / target) * 100, 100) if target != float('inf') else 0
                    log_messages.append(f"✅ #{sent} {mode} fired: {message[:20] if mode == 'message' else 'BOOM'}")
                    
                    if "limitType" in result:
                        cooldown_time = 60 * backoff  # 60s, 120s, etc.
                        log_messages.append(f"⚠️ Rate bitch-slap! Backoff {cooldown_time}s (x{backoff})")
                        for sec in range(cooldown_time, 0, -1):
                            if not spammer_active: break
                            cooldown = sec
                            await asyncio.sleep(1)
                        cooldown = 0
                        backoff = min(backoff * 2, 10)  # Cap at 10x
                        continue

                    await asyncio.sleep(delay)
                    backoff = 1  # Reset on success
                except Exception as e:
                    log_messages.append(f"💥 Mod fail: {str(e)[:50]}")
                    await asyncio.sleep(delay * 2)

            log_messages.append(f"🎉 {mode.upper()} MISSION COMPLETE!" if sent >= target else "🛑 ABORTED — PUSSY MODE")
        except Exception as e:
            log_messages.append(f"💥 FATAL: {str(e)}")
        finally:
            spammer_active = False
            progress = 0
            backoff = 1

async def run_mod_call(session, xuid, message, auth_key, mode):
    if mode == 'message':
        return await send_message(session, xuid, message, auth_key)
    elif mode == 'party':
        return await send_party_invite(session, xuid, auth_key)
    elif mode == 'friend':
        return await send_friend_request(session, xuid, auth_key)
    elif mode == 'presence':
        return await get_presence(session, xuid, auth_key)  # Poll, not spam
    elif mode == 'stats':
        return await get_stats(session, xuid, auth_key)
    elif mode == 'nuke':
        # Chain all — message + party + friend in loop
        await asyncio.gather(
            send_message(session, xuid, message, auth_key),
            send_party_invite(session, xuid, auth_key),
            send_friend_request(session, xuid, auth_key)
        )
        return {"success": True}
    raise Exception(f"Unknown mod: {mode}")

# === ROUTES (MODE-AWARE) ===
@app.get("/", response_class=HTMLResponse)
async def index():
    return HTMLResponse(FULL_HTML)

@app.post("/start")
async def start_spam(
    auth_key: str = Form(...),
    gamertag: str = Form(...),
    message: str = Form("GG EZ"),
    amount: int = Form(50),
    delay: float = Form(1.3),
    mode: str = Form('message'),
    party_amount: int = Form(10),
    party_delay: float = Form(2.0),
    friend_amount: int = Form(20),
    friend_delay: float = Form(3.0),
    nuke_duration: int = Form(60)
):
    global spammer_task, spammer_active, log_messages
    if spammer_active:
        return {"error": "One nuke at a time, cowboy!"}

    final_amount = amount if mode in ['message', 'nuke'] else (party_amount if mode == 'party' else friend_amount)
    final_delay = delay if mode in ['message', 'nuke'] else (party_delay if mode == 'party' else friend_delay)

    spammer_active = True
    log_messages = [f"🚀 {mode.upper()} NUKE INITIATED ON {gamertag}"]
    progress = 0
    spammer_task = asyncio.create_task(spam_worker(gamertag, message, final_amount, auth_key, final_delay, mode))
    return {"status": "nuking"}

@app.post("/stop")
async def stop_spam():
    global spammer_active
    spammer_active = False
    return {"status": "aborted"}

@app.get("/status")
async def get_status():
    return {
        "active": spammer_active,
        "progress": progress,
        "cooldown": cooldown,
        "logs": log_messages[-20:],
        "mode": current_mode
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
