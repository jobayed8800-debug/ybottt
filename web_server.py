
web_server_content = r'''"""
Free Fire Tournament Bot - Flask Web Server
Handles Ad Pages, Unlock Codes, and API Endpoints
"""
from flask import Flask, request, jsonify, render_template_string
import threading
import time
import random
from database import UnlockCodeDB, UserDB, TournamentDB, TaskDB
from utils import generate_unlock_code
from config import (
    UNLOCK_CODES_FILE, USERS_FILE, TOURNAMENTS_FILE, TASKS_FILE,
    AD_WAIT_SECONDS, CODE_LENGTH, WEB_SERVER_URL, UNLOCK_DURATION_HOURS, PORT
)

app = Flask(__name__)

# Initialize databases
code_db = UnlockCodeDB(UNLOCK_CODES_FILE)
user_db = UserDB(USERS_FILE)
tour_db = TournamentDB(TOURNAMENTS_FILE)
task_db = TaskDB(TASKS_FILE)

# In-memory store for active ad sessions (for high concurrency)
ad_sessions = {}
session_lock = threading.Lock()

AD_PAGE_HTML = """
<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Advertisement - Free Fire Tournament</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #fff;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            background: rgba(255,255,255,0.05);
            border-radius: 20px;
            padding: 40px;
            max-width: 500px;
            width: 100%;
            text-align: center;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
        }
        .logo { font-size: 3em; margin-bottom: 10px; }
        h1 { color: #e94560; margin-bottom: 20px; font-size: 1.5em; }
        .ad-box {
            background: #0f3460;
            border-radius: 15px;
            padding: 30px;
            margin: 20px 0;
            min-height: 200px;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 2px dashed #e94560;
        }
        .ad-text { font-size: 1.2em; color: #aaa; }
        .timer {
            font-size: 2em;
            color: #e94560;
            margin: 20px 0;
            font-weight: bold;
        }
        .btn {
            background: #e94560;
            color: white;
            border: none;
            padding: 15px 40px;
            font-size: 1.1em;
            border-radius: 50px;
            cursor: pointer;
            transition: all 0.3s;
            display: none;
            width: 100%;
        }
        .btn:hover { background: #ff6b6b; transform: scale(1.05); }
        .btn.show { display: inline-block; }
        .code-box {
            background: #16213e;
            border-radius: 10px;
            padding: 20px;
            margin-top: 20px;
            display: none;
            border: 2px solid #0f3460;
        }
        .code-box.show { display: block; }
        .code { font-size: 2em; color: #00ff88; letter-spacing: 5px; font-family: monospace; }
        .instructions { margin-top: 15px; color: #aaa; font-size: 0.9em; }
        .progress-bar {
            width: 100%;
            height: 8px;
            background: #0f3460;
            border-radius: 4px;
            margin: 15px 0;
            overflow: hidden;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #e94560, #ff6b6b);
            width: 0%;
            transition: width 1s linear;
        }
        .user-info { font-size: 0.8em; color: #666; margin-top: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🎮</div>
        <h1>Free Fire Tournament</h1>
        <p>24 ঘন্টার অ্যাক্সেস পেতে নিচের অ্যাড দেখুন</p>
        
        <div class="ad-box">
            <span class="ad-text">📢 Advertisement Space<br><br>আপনার বিজ্ঞাপন এখানে</span>
        </div>
        
        <div class="progress-bar">
            <div class="progress-fill" id="progress"></div>
        </div>
        
        <div class="timer" id="timer">{{ wait_seconds }}s</div>
        
        <button class="btn" id="unlockBtn" onclick="generateCode()">
            🔓 Unlock Now
        </button>
        
        <div class="code-box" id="codeBox">
            <p>আপনার কনফার্মেশন কোড:</p>
            <div class="code" id="code"></div>
            <p class="instructions">এই কোডটি কপি করে বটে পাঠিয়ে দিন</p>
        </div>
        
        <div class="user-info">User: {{ user_id }} | Session: {{ token }}</div>
    </div>

    <script>
        let timeLeft = {{ wait_seconds }};
        const timerEl = document.getElementById('timer');
        const btnEl = document.getElementById('unlockBtn');
        const progressEl = document.getElementById('progress');
        const codeBox = document.getElementById('codeBox');
        const codeEl = document.getElementById('code');
        
        const totalTime = timeLeft;
        
        const interval = setInterval(() => {
            timeLeft--;
            timerEl.textContent = timeLeft + 's';
            const progress = ((totalTime - timeLeft) / totalTime) * 100;
            progressEl.style.width = progress + '%';
            
            if (timeLeft <= 0) {
                clearInterval(interval);
                timerEl.textContent = '✅ Ready!';
                btnEl.classList.add('show');
                progressEl.style.width = '100%';
            }
        }, 1000);
        
        async function generateCode() {
            btnEl.disabled = true;
            btnEl.textContent = '⏳ Generating...';
            
            try {
                const response = await fetch('/api/generate-code', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        user_id: {{ user_id }},
                        token: '{{ token }}'
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    codeEl.textContent = data.code;
                    codeBox.classList.add('show');
                    btnEl.textContent = '✅ Code Generated';
                    timerEl.style.display = 'none';
                } else {
                    alert('Error: ' + data.message);
                    btnEl.disabled = false;
                    btnEl.textContent = '🔓 Try Again';
                }
            } catch (err) {
                alert('Network error! Please try again.');
                btnEl.disabled = false;
                btnEl.textContent = '🔓 Unlock Now';
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return jsonify({
        "status": "running",
        "service": "Free Fire Tournament Bot API",
        "version": "1.0.0"
    })

@app.route('/ad')
def ad_page():
    """Serve unique ad page for each user"""
    user_id = request.args.get('user', '0')
    token = request.args.get('token', '')
    
    try:
        user_id = int(user_id)
    except:
        user_id = 0
    
    # Store session
    with session_lock:
        ad_sessions[token] = {
            "user_id": user_id,
            "token": token,
            "created_at": time.time(),
            "used": False
        }
    
    return render_template_string(
        AD_PAGE_HTML,
        user_id=user_id,
        token=token,
        wait_seconds=AD_WAIT_SECONDS
    )

@app.route('/api/generate-code', methods=['POST'])
def generate_code():
    """Generate unique unlock code for user"""
    data = request.get_json()
    user_id = data.get('user_id', 0)
    token = data.get('token', '')
    
    try:
        user_id = int(user_id)
    except:
        return jsonify({"success": False, "message": "Invalid user ID"})
    
    # Verify session
    with session_lock:
        session = ad_sessions.get(token)
        if not session:
            return jsonify({"success": False, "message": "Invalid session"})
        if session.get("used"):
            return jsonify({"success": False, "message": "Session already used"})
        if session.get("user_id") != user_id:
            return jsonify({"success": False, "message": "User mismatch"})
        
        ad_sessions[token]["used"] = True
    
    # Generate unique code
    code = generate_unlock_code(CODE_LENGTH)
    while code_db.get(code):
        code = generate_unlock_code(CODE_LENGTH)
    
    # Store code
    code_db.create_code(user_id, code)
    
    return jsonify({
        "success": True,
        "code": code,
        "message": "Code generated successfully"
    })

@app.route('/api/verify-code', methods=['POST'])
def verify_code():
    """Verify unlock code"""
    data = request.get_json()
    user_id = data.get('user_id', 0)
    code = data.get('code', '')
    
    try:
        user_id = int(user_id)
    except:
        return jsonify({"success": False, "message": "Invalid user ID"})
    
    if code_db.verify_code(code, user_id):
        # Unlock user
        user_db.unlock_user(user_id, UNLOCK_DURATION_HOURS)
        return jsonify({
            "success": True,
            "message": "User unlocked successfully",
            "expires_in": f"{UNLOCK_DURATION_HOURS} hours"
        })
    
    return jsonify({"success": False, "message": "Invalid or expired code"})

@app.route('/api/user/status/<int:user_id>')
def user_status(user_id):
    """Check user unlock status"""
    is_unlocked = user_db.is_unlocked(user_id)
    expiry = user_db.get_unlock_expiry(user_id)
    
    return jsonify({
        "user_id": user_id,
        "unlocked": is_unlocked,
        "expires_at": expiry
    })

@app.route('/api/tournaments')
def get_tournaments():
    """Get all active tournaments"""
    tournaments = tour_db.get_all_tournaments()
    active = [t for t in tournaments if t.get("status") in ["upcoming", "live"]]
    return jsonify({"tournaments": active})

@app.route('/api/tournament/<tid>')
def get_tournament(tid):
    """Get tournament details"""
    tour = tour_db.get_tournament(tid)
    if tour:
        # Remove sensitive info for public API
        public_tour = {
            "id": tour["id"],
            "name": tour["name"],
            "type": tour["type"],
            "max_players": tour["max_players"],
            "min_level": tour["min_level"],
            "prize": tour["prize"],
            "start_time": tour["start_time"],
            "status": tour["status"],
            "teams_count": len(tour.get("teams", []))
        }
        return jsonify(public_tour)
    return jsonify({"error": "Tournament not found"}), 404

@app.route('/api/stats')
def get_stats():
    """Get bot statistics"""
    user_stats = user_db.get_stats()
    task_stats = task_db.get_stats()
    
    return jsonify({
        "users": user_stats,
        "tasks": task_stats,
        "server_time": time.time()
    })

# Cleanup expired codes periodically
@app.route('/api/cleanup', methods=['POST'])
def cleanup():
    code_db.cleanup_expired()
    return jsonify({"success": True, "message": "Cleanup completed"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=False, threaded=True)
'''

# Write as raw bytes to avoid any encoding issues
with open('/mnt/agents/output/web_server.py', 'wb') as f:
    f.write(web_server_content.encode('utf-8'))

# Verify - check last 10 lines
with open('/mnt/agents/output/web_server.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    print("Total lines:", len(lines))
    print("\nLast 10 lines:")
    for line in lines[-10:]:
        print(line, end='')
