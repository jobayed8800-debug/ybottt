
user_handlers_content = '''"""
Free Fire Tournament Bot - User Handlers
Handles user interactions, unlock system, tournament viewing
"""
import time
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationTypes
from config import MESSAGES, WEB_SERVER_URL, UNLOCK_DURATION_HOURS
from database import UserDB, TournamentDB, TaskDB, UnlockCodeDB
from utils import generate_unique_link, escape_markdown, create_keyboard

# Initialize databases
user_db = UserDB("data/users.json")
tour_db = TournamentDB("data/tournaments.json")
task_db = TaskDB("data/tasks.json")
code_db = UnlockCodeDB("data/unlock_codes.json")

# Conversation states
WAITING_FOR_CODE = 1

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command - Welcome user"""
    user = update.effective_user
    user_id = user.id
    
    # Register user if new
    existing = user_db.get_user(user_id)
    if not existing.get("username"):
        user_db.update_user(user_id, {
            "username": user.username or "",
            "first_name": user.first_name or "",
            "last_name": user.last_name or ""
        })
    
    # Check if banned
    if existing.get("is_banned", False):
        await update.message.reply_text(
            "🚫 *আপনার অ্যাকাউন্ট ব্যান করা হয়েছে!*\\n\\n"
            f"📝 কারণ: {escape_markdown(existing.get('ban_reason', 'Unknown'))}",
            parse_mode="MarkdownV2"
        )
        return
    
    keyboard = create_keyboard([
        InlineKeyboardButton("🔓 Unlock 24H", callback_data="unlock"),
        InlineKeyboardButton("🎮 Tournaments", callback_data="tournaments"),
        InlineKeyboardButton("📜 Rules", callback_data="rules"),
        InlineKeyboardButton("ℹ️ About", callback_data="about"),
        InlineKeyboardButton("👮 Admin Panel", callback_data="admin_check"),
    ], per_row=2)
    
    await update.message.reply_text(
        MESSAGES["welcome"],
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="MarkdownV2"
    )

async def unlock_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle unlock request"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    # Check if already unlocked
    if user_db.is_unlocked(user_id):
        expiry = user_db.get_unlock_expiry(user_id)
        keyboard = [[InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]]
        await query.edit_message_text(
            MESSAGES["already_unlocked"].format(expires=expiry),
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="MarkdownV2"
        )
        return
    
    # Generate unique ad link
    ad_link = generate_unique_link(WEB_SERVER_URL, user_id)
    
    keyboard = create_keyboard([
        InlineKeyboardButton("📺 Watch Ad", url=ad_link),
        InlineKeyboardButton("🔑 Enter Code", callback_data="enter_code"),
        InlineKeyboardButton("🏠 Back", callback_data="main_menu"),
    ], per_row=2)
    
    await query.edit_message_text(
        "🔓 *24 ঘন্টার অ্যাক্সেস পেতে:*\\n\\n"
        "1️⃣ নিচের \"Watch Ad\" বাটনে ক্লিক করুন\\n"
        "2️⃣ 10 সেকেন্ড অপেক্ষা করুন\\n"
        "3️⃣ Unlock বাটনে ক্লিক করে কোড নিন\\n"
        "4️⃣ \"Enter Code\" এ ক্লিক করে কোড দিন\\n\\n"
        f"🔗 আপনার ইউনিক লিংক:\\n`{ad_link}`",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="MarkdownV2"
    )

async def enter_code_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ask user to enter unlock code"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "🔑 *আনলক কোড দিন:*\\n\\n"
        "আপনার কোডটি টাইপ করুন (যেমন: ABC12345)\\n\\n"
        "⏳ কোড ১ ঘন্টার জন্য ভ্যালিড।",
        parse_mode="MarkdownV2"
    )
    
    return WAITING_FOR_CODE

async def process_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process unlock code"""
    user_id = update.effective_user.id
    code = update.message.text.strip().upper()
    
    # Verify code via API
    try:
        response = requests.post(
            f"{WEB_SERVER_URL}/api/verify-code",
            json={"user_id": user_id, "code": code},
            timeout=10
        )
        result = response.json()
        
        if result.get("success"):
            keyboard = [[InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]]
            await update.message.reply_text(
                f"✅ *অভিনন্দন!*\\n\\n"
                f"আপনার অ্যাকাউন্ট {UNLOCK_DURATION_HOURS} ঘন্টার জন্য আনলক করা হয়েছে!\\n"
                f"⏳ মেয়াদ: {result.get('expires_in', '24 hours')}",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="MarkdownV2"
            )
        else:
            keyboard = [
                [InlineKeyboardButton("🔄 Try Again", callback_data="enter_code")],
                [InlineKeyboardButton("📺 Watch Ad Again", callback_data="unlock")]
            ]
            await update.message.reply_text(
                f"❌ *ভুল কোড!*\\n\\n{result.get('message', 'Invalid code')}",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="MarkdownV2"
            )
    except Exception as e:
        await update.message.reply_text(
            f"⚠️ *সার্ভার এরর!*\\n\\nঅনুগ্রহ করে পরে আবার চেষ্টা করুন।\\nError: {str(e)}",
            parse_mode="MarkdownV2"
        )
    
    return ConversationHandler.END

async def show_tournaments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show active tournaments"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    # Check unlock status
    if not user_db.is_unlocked(user_id):
        keyboard = [
            [InlineKeyboardButton("🔓 Unlock Now", callback_data="unlock")],
            [InlineKeyboardButton("🏠 Back", callback_data="main_menu")]
        ]
        await query.edit_message_text(
            "🔒 *টুর্নামেন্ট দেখতে হলে আগে আনলক করুন!*\\n\\n"
            "24 ঘন্টার অ্যাক্সেস পেতে Unlock Now বাটনে ক্লিক করুন।",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="MarkdownV2"
        )
        return
    
    tournaments = tour_db.get_all_tournaments()
    active = [t for t in tournaments if t.get("status") in ["upcoming", "live"]]
    
    if not active:
        keyboard = [[InlineKeyboardButton("🏠 Back", callback_data="main_menu")]]
        await query.edit_message_text(
            "📭 *কোনো সক্রিয় টুর্নামেন্ট নেই!*\\n\\nপরে আবার চেষ্টা করুন।",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="MarkdownV2"
        )
        return
    
    # Show tournament list with buttons
    keyboard = []
    text = "🎮 *সক্রিয় টুর্নামেন্টগুলো:*\\n\\n"
    
    for tour in active:
        status_emoji = "🟢 LIVE" if tour.get("status") == "live" else "🟡 Upcoming"
        text += f"{status_emoji} *{escape_markdown(tour['name'])}*\\n"
        text += f"💰 Prize: {escape_markdown(tour.get('prize', 'N/A'))}\\n"
        text += f"⏰ Start: {escape_markdown(tour.get('start_time', 'TBA'))}\\n\\n"
        keyboard.append([InlineKeyboardButton(
            f"👁️ View {tour['name'][:20]}", 
            callback_data=f"view_tour_{tour['id']}"
        )])
    
    keyboard.append([InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")])
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="MarkdownV2"
    )

async def view_tournament(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View specific tournament details"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    tid = query.data.replace("view_tour_", "")
    
    tour = tour_db.get_tournament(tid)
    if not tour:
        await query.edit_message_text("❌ টুর্নামেন্ট পাওয়া যায়নি!")
        return
    
    # Check tasks for this tournament
    tasks = task_db.get_tournament_tasks(tid)
    has_tasks = len(tasks) > 0
    
    text = f"""🎮 *{escape_markdown(tour['name'])}*

🆔 ID: `{tour['id']}`
📋 Type: {tour.get('type', 'squad').upper()}
👥 Max Players: {tour.get('max_players', 48)}
📊 Min Level: {tour.get('min_level', 40)}
💰 Prize: {escape_markdown(tour.get('prize', 'N/A'))}
⏰ Start: {escape_markdown(tour.get('start_time', 'TBA'))}
📡 Status: {tour.get('status', 'unknown').upper()}

👥 Teams Joined: {len(tour.get('teams', []))}"""
    
    keyboard = []
    
    if has_tasks:
        for task in tasks:
            keyboard.append([InlineKeyboardButton(
                f"📋 Task: {task['description'][:25]}",
                callback_data=f"do_task_{task['id']}"
            )])
    
    # Show room info if no tasks or tasks completed
    if not has_tasks or user_id in tasks[0].get("completed_by", []) if tasks else True:
        if tour.get("room_id"):
            keyboard.append([InlineKeyboardButton(
                "🔐 Get Room Info", callback_data=f"room_info_{tid}"
            )])
    
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="tournaments")])
    keyboard.append([InlineKeyboardButton("🏠 Menu", callback_data="main_menu")])
    
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="MarkdownV2"
    )

async def do_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show task details and link"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    task_id = query.data.replace("do_task_", "")
    
    task = task_db.get_task(task_id)
    if not task:
        await query.edit_message_text("❌ টাস্ক পাওয়া যায়নি!")
        return
    
    # Check if already completed
    if user_id in task.get("completed_by", []):
        await query.edit_message_text(
            "✅ আপনি ইতিমধ্যে এই টাস্ক কমপ্লিট করেছেন!\\n\\n"
            "রুম তথ্য দেখতে টুর্নামেন্টে ফিরে যান।",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Back", callback_data=f"view_tour_{task['tournament_id']}")
            ]])
        )
        return
    
    keyboard = [
        [InlineKeyboardButton("🔗 Open Task Link", url=task['link'])],
        [InlineKeyboardButton("✅ Complete Task", callback_data=f"complete_task_{task_id}")],
        [InlineKeyboardButton("🔙 Back", callback_data=f"view_tour_{task['tournament_id']}")]
    ]
    
    await query.edit_message_text(
        f"📋 *টাস্ক:*\\n\\n"
        f"📝 {escape_markdown(task['description'])}\\n\\n"
        f"🔗 লিংক: {escape_markdown(task['link'])}\\n\\n"
        f"✅ টাস্ক কমপ্লিট করার পর Complete Task বাটনে ক্লিক করুন।",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="MarkdownV2"
    )

async def complete_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mark task as completed"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    task_id = query.data.replace("complete_task_", "")
    
    if task_db.complete_task(task_id, user_id):
        task = task_db.get_task(task_id)
        keyboard = [
            [InlineKeyboardButton("🔐 Get Room Info", callback_data=f"room_info_{task['tournament_id']}")],
            [InlineKeyboardButton("🔙 Back", callback_data=f"view_tour_{task['tournament_id']}")]
        ]
        await query.edit_message_text(
            "✅ *টাস্ক সফলভাবে কমপ্লিট হয়েছে!*\\n\\n"
            "এখন আপনি রুম তথ্য পেতে পারেন।",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="MarkdownV2"
        )
    else:
        await query.edit_message_text("⚠️ টাস্ক কমপ্লিট করা যায়নি!")

async def show_room_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show room ID and password"""
    query = update.callback_query
    await query.answer()
    
    tid = query.data.replace("room_info_", "")
    tour = tour_db.get_tournament(tid)
    
    if not tour:
        await query.edit_message_text("❌ টুর্নামেন্ট পাওয়া যায়নি!")
        return
    
    room_id = tour.get("room_id", "")
    room_pass = tour.get("room_pass", "")
    
    if not room_id:
        await query.edit_message_text(
            "⏳ *রুম তথ্য এখনো সেট করা হয়নি!*\\n\\n"
            "এডমিন রুম তথ্য আপডেট করার পর আবার চেষ্টা করুন।",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Back", callback_data=f"view_tour_{tid}")
            ]])
        )
        return
    
    keyboard = [
        [InlineKeyboardButton("📋 Copy Room ID", callback_data=f"copy_{room_id}")],
        [InlineKeyboardButton("🔙 Back", callback_data=f"view_tour_{tid}")]
    ]
    
    await query.edit_message_text(
        MESSAGES["room_info"].format(room_id=room_id, password=room_pass),
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="MarkdownV2"
    )

async def show_rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show tournament rules"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [[InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]]
    
    await query.edit_message_text(
        MESSAGES["rules"],
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="MarkdownV2"
    )

async def show_about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show about page"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [[InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]]
    
    await query.edit_message_text(
        MESSAGES["about"],
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="MarkdownV2"
    )

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Return to main menu"""
    query = update.callback_query
    await query.answer()
    
    keyboard = create_keyboard([
        InlineKeyboardButton("🔓 Unlock 24H", callback_data="unlock"),
        InlineKeyboardButton("🎮 Tournaments", callback_data="tournaments"),
        InlineKeyboardButton("📜 Rules", callback_data="rules"),
        InlineKeyboardButton("ℹ️ About", callback_data="about"),
        InlineKeyboardButton("👮 Admin Panel", callback_data="admin_check"),
    ], per_row=2)
    
    await query.edit_message_text(
        MESSAGES["welcome"],
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="MarkdownV2"
    )

async def admin_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check if user is admin and show appropriate panel"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    from admin_handlers import is_any_admin, is_super_admin
    
    if is_super_admin(user_id):
        from admin_handlers import super_admin_panel
        # Create fake update for super_admin_panel
        class FakeUpdate:
            def __init__(self, msg):
                self.message = msg
                self.effective_user = type('obj', (object,), {'id': user_id})()
        fake = FakeUpdate(query.message)
        await super_admin_panel(fake, context)
    elif is_any_admin(user_id):
        from admin_handlers import admin_panel
        class FakeUpdate:
            def __init__(self, msg):
                self.message = msg
                self.effective_user = type('obj', (object,), {'id': user_id})()
        fake = FakeUpdate(query.message)
        await admin_panel(fake, context)
    else:
        keyboard = [[InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]]
        await query.edit_message_text(
            "🚫 *আপনার এডমিন অ্যাক্সেস নেই!*\\n\\n"
            "শুধুমাত্র অনুমোদিত এডমিনরা প্যানেল অ্যাক্সেস করতে পারবেন।",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="MarkdownV2"
        )
'''

with open('/mnt/agents/output/user_handlers.py', 'w', encoding='utf-8') as f:
    f.write(user_handlers_content)

print("✅ user_handlers.py created")
