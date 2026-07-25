
config_content = '''"""
Free Fire Tournament Bot - Configuration
"""
import os

# Bot Settings
BOT_TOKEN = os.getenv("BOT_TOKEN", "8558590216:AAG1IUG_dWV3xiEgtXdpm1_WniAF-uLAGOs")
WEB_SERVER_URL = os.getenv("WEB_SERVER_URL", "https://ybottt-143.onrender.com")

# Admin Settings
SUPER_ADMIN_ID = int(os.getenv("SUPER_ADMIN_ID", "8908999062"))  # Main Admin Telegram ID

# Unlock Settings
UNLOCK_DURATION_HOURS = 24
AD_WAIT_SECONDS = 10
CODE_LENGTH = 8

# Tournament Settings
MIN_LEVEL = 40
MAX_SQUAD_MEMBERS = 4
MAX_PLAYERS = 48

# File Paths
DATA_DIR = "data"
USERS_FILE = f"{DATA_DIR}/users.json"
TOURNAMENTS_FILE = f"{DATA_DIR}/tournaments.json"
ADMINS_FILE = f"{DATA_DIR}/admins.json"
UNLOCK_CODES_FILE = f"{DATA_DIR}/unlock_codes.json"
TASKS_FILE = f"{DATA_DIR}/tasks.json"

# Messages (Bengali)
MESSAGES = {
    "welcome": "🎮 *Free Fire Tournament Bot*\\n\\nস্বাগতম! 24 ঘন্টার অ্যাক্সেস পেতে নিচের বাটনে ক্লিক করুন।",
    "rules": """📜 *টুর্নামেন্ট রুলস:*

1️⃣ স্কোয়াডের ৪ জনের প্রথম নাম একই হতে হবে
2️⃣ প্রত্যেকের লেভেল কমপক্ষে 40 হতে হবে
3️⃣ সবাই একই গিল্ডের হতে হবে
4️⃣ কোনো চিট/হ্যাক/ঠাপাড়ি অ্যাপস ব্যবহার করা যাবে না
5️⃣ একজন হ্যাক করলে পুরো স্কোয়াড ব্যান হবে
6️⃣ পিওর প্লেয়ারদের জন্য টুর্নামেন্ট

⚠️ রুলস ভাঙলে সরাসরি ব্যান!""",
    "about": """ℹ️ *About Us*

🎮 Free Fire Tournament Bot
🤖 Bot Name: turbdtrad
📊 Auto Tournament Management
🔒 24H Unlock System
👮 Admin Panel Support

Developed with ❤️ for Bangladeshi Gamers""",
    "ad_wait": "⏳ অনুগ্রহ করে {seconds} সেকেন্ড অপেক্ষা করুন...",
    "unlock_success": "✅ আনলক সফল! আপনার কোড: `{code}`\\n\\nএই কোডটি বটে পাঠিয়ে দিন।",
    "already_unlocked": "✅ আপনার অ্যাকাউন্ট ইতিমধ্যে আনলক করা আছে!\\n⏳ মেয়াদ শেষ: {expires}",
    "unlock_expired": "❌ আপনার 24 ঘন্টার অ্যাক্সেস শেষ হয়ে গেছে। নতুন করে আনলক করুন।",
    "invalid_code": "❌ ভুল কোড! আবার চেষ্টা করুন।",
    "admin_only": "🚫 এই ফিচার শুধু এডমিনদের জন্য!",
    "super_admin_only": "🚫 এই ফিচার শুধু সুপার এডমিনের জন্য!",
    "tournament_created": "✅ টুর্নামেন্ট সফলভাবে তৈরি হয়েছে!\\n🆔 ID: `{tid}`",
    "tournament_deleted": "🗑️ টুর্নামেন্ট ডিলিট হয়ে গেছে!",
    "task_assigned": "📋 টাস্ক অ্যাসাইন করা হয়েছে!\\n🔗 লিংক: {link}\\n📝 {description}",
    "room_info": """🔐 *রুম তথ্য*

🆔 Room ID: `{room_id}`
🔑 Password: `{password}`

⚠️ এই তথ্য কাউকে শেয়ার করবেন না!""",
}
'''

with open('/mnt/agents/output/config.py', 'w', encoding='utf-8') as f:
    f.write(config_content)

print("✅ config.py created")
