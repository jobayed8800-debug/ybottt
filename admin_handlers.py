
admin_handlers_content = '''"""
Free Fire Tournament Bot - Admin Handlers
Super Admin & Sub Admin Command Handlers
"""
import time
from typing import Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import MESSAGES, SUPER_ADMIN_ID
from database import AdminDB, UserDB, TournamentDB, TaskDB
from utils import escape_markdown, create_keyboard

# Initialize databases
admin_db = AdminDB("data/admins.json")
user_db = UserDB("data/users.json")
tour_db = TournamentDB("data/tournaments.json")
task_db = TaskDB("data/tasks.json")

# ==================== PERMISSION CHECKS ====================

def is_super_admin(user_id: int) -> bool:
    return user_id == SUPER_ADMIN_ID or admin_db.is_super_admin(user_id)

def is_sub_admin(user_id: int) -> bool:
    return admin_db.is_sub_admin(user_id)

def is_any_admin(user_id: int) -> bool:
    return admin_db.is_admin(user_id)

# ==================== SUPER ADMIN COMMANDS ====================

async def super_admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Super Admin Control Panel"""
    user_id = update.effective_user.id
    
    if not is_super_admin(user_id):
        await update.message.reply_text(MESSAGES["super_admin_only"])
        return
    
    keyboard = create_keyboard([
        InlineKeyboardButton("➕ Add Sub Admin", callback_data="sa_add_admin"),
        InlineKeyboardButton("➖ Remove Sub Admin", callback_data="sa_remove_admin"),
        InlineKeyboardButton("🚫 Block Sub Admin", callback_data="sa_block_admin"),
        InlineKeyboardButton("✅ Unblock Sub Admin", callback_data="sa_unblock_admin"),
        InlineKeyboardButton("📊 View All Admins", callback_data="sa_list_admins"),
        InlineKeyboardButton("📈 User Stats", callback_data="sa_user_stats"),
        InlineKeyboardButton("🗑️ Delete Any Tournament", callback_data="sa_del_tour"),
        InlineKeyboardButton("🔨 Ban User", callback_data="sa_ban_user"),
        InlineKeyboardButton("🔓 Unban User", callback_data="sa_unban_user"),
        InlineKeyboardButton("📋 All Tasks Stats", callback_data="sa_task_stats"),
        InlineKeyboardButton("🏠 Back to Menu", callback_data="main_menu"),
    ], per_row=2)
    
    await update.message.reply_text(
        "👑 *Super Admin Panel*\\n\\nসুপার এডমিন কন্ট্রোল প্যানেলে স্বাগতম!",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="MarkdownV2"
    )

async def add_sub_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add a new sub admin (Super Admin only)"""
    user_id = update.effective_user.id
    
    if not is_super_admin(user_id):
        await update.message.reply_text(MESSAGES["super_admin_only"])
        return
    
    if not context.args or len(context.args) < 1:
        await update.message.reply_text(
            "⚠️ Usage: `/addadmin <telegram_user_id>`\\n\\nউদাহরণ: `/addadmin 123456789`",
            parse_mode="MarkdownV2"
        )
        return
    
    try:
        new_admin_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ ভুল User ID! সংখ্যা দিন।")
        return
    
    if admin_db.is_admin(new_admin_id):
        await update.message.reply_text("⚠️ এই ইউজার ইতিমধ্যে এডমিন!")
        return
    
    admin_db.add_admin(new_admin_id, role="sub", added_by=user_id)
    
    await update.message.reply_text(
        f"✅ *নতুন Sub Admin যোগ করা হয়েছে!*\\n\\n🆔 User ID: `{new_admin_id}`\\n👤 Role: Sub Admin",
        parse_mode="MarkdownV2"
    )
    
    # Notify new admin
    try:
        await context.bot.send_message(
            chat_id=new_admin_id,
            text="🎉 *অভিনন্দন!*\\n\\nআপনাকে Sub Admin হিসেবে নিয়োগ করা হয়েছে!\\n\\nএডমিন প্যানেল অ্যাক্সেস করতে `/admin` টাইপ করুন।",
            parse_mode="MarkdownV2"
        )
    except Exception as e:
        await update.message.reply_text(f"⚠️ নতুন এডমিনকে নোটিফাই করা যায়নি: {str(e)}")

async def remove_sub_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove a sub admin"""
    user_id = update.effective_user.id
    
    if not is_super_admin(user_id):
        await update.message.reply_text(MESSAGES["super_admin_only"])
        return
    
    if not context.args:
        await update.message.reply_text("⚠️ Usage: `/removeadmin <user_id>`")
        return
    
    try:
        target_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ ভুল User ID!")
        return
    
    if target_id == SUPER_ADMIN_ID:
        await update.message.reply_text("🚫 মেইন এডমিনকে রিমুভ করা যাবে না!")
        return
    
    if admin_db.remove_admin(target_id):
        await update.message.reply_text(f"✅ এডমিন `{target_id}` রিমুভ করা হয়েছে!", parse_mode="MarkdownV2")
    else:
        await update.message.reply_text("❌ এডমিন পাওয়া যায়নি!")

async def block_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Block a sub admin"""
    user_id = update.effective_user.id
    
    if not is_super_admin(user_id):
        await update.message.reply_text(MESSAGES["super_admin_only"])
        return
    
    if not context.args:
        await update.message.reply_text("⚠️ Usage: `/blockadmin <user_id>`")
        return
    
    try:
        target_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ ভুল User ID!")
        return
    
    if target_id == SUPER_ADMIN_ID:
        await update.message.reply_text("🚫 নিজেকে ব্লক করা যাবে না!")
        return
    
    admin_db.block_admin(target_id)
    await update.message.reply_text(f"🚫 এডমিন `{target_id}` ব্লক করা হয়েছে!", parse_mode="MarkdownV2")

async def unblock_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Unblock a sub admin"""
    user_id = update.effective_user.id
    
    if not is_super_admin(user_id):
        await update.message.reply_text(MESSAGES["super_admin_only"])
        return
    
    if not context.args:
        await update.message.reply_text("⚠️ Usage: `/unblockadmin <user_id>`")
        return
    
    try:
        target_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ ভুল User ID!")
        return
    
    admin_db.unblock_admin(target_id)
    await update.message.reply_text(f"✅ এডমিন `{target_id}` আনব্লক করা হয়েছে!", parse_mode="MarkdownV2")

async def list_all_admins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all admins (Super Admin only)"""
    user_id = update.effective_user.id
    
    if not is_super_admin(user_id):
        await update.message.reply_text(MESSAGES["super_admin_only"])
        return
    
    admins = admin_db.get_all_admins()
    
    if not admins:
        await update.message.reply_text("📭 কোনো এডমিন নেই!")
        return
    
    text = "👥 *সকল এডমিন তালিকা:*\\n\\n"
    for admin in admins:
        role = "👑 Super" if admin.get("role") == "super" else "👤 Sub"
        status = "✅ Active" if admin.get("is_active", False) else "🚫 Blocked"
        added = time.strftime("%Y-%m-%d", time.localtime(admin.get("added_at", 0)))
        text += f"🆔 `{admin['user_id']}`\\n{role} | {status}\\n📅 Added: {added}\\n\\n"
    
    await update.message.reply_text(text, parse_mode="MarkdownV2")

async def user_statistics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user statistics (Super Admin)"""
    user_id = update.effective_user.id
    
    if not is_super_admin(user_id):
        await update.message.reply_text(MESSAGES["super_admin_only"])
        return
    
    stats = user_db.get_stats()
    
    text = f"""📊 *ইউজার স্ট্যাটিস্টিক্স:*

👥 মোট ইউজার: `{stats['total']}`
🔒 ব্যান্ড: `{stats['banned']}`
🔓 আনলকড: `{stats['unlocked']}`
📅 আপডেট: `{time.strftime('%Y-%m-%d %H:%M')}`"""
    
    await update.message.reply_text(text, parse_mode="MarkdownV2")

async def ban_user_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ban a user (Super Admin)"""
    user_id = update.effective_user.id
    
    if not is_super_admin(user_id):
        await update.message.reply_text(MESSAGES["super_admin_only"])
        return
    
    if not context.args:
        await update.message.reply_text("⚠️ Usage: `/banuser <user_id> [reason]`")
        return
    
    try:
        target_id = int(context.args[0])
        reason = " ".join(context.args[1:]) if len(context.args) > 1 else "No reason"
    except ValueError:
        await update.message.reply_text("❌ ভুল User ID!")
        return
    
    user_db.ban_user(target_id, reason)
    await update.message.reply_text(f"🔨 ইউজার `{target_id}` ব্যান করা হয়েছে!\\n📝 কারণ: {reason}", parse_mode="MarkdownV2")

async def unban_user_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Unban a user (Super Admin)"""
    user_id = update.effective_user.id
    
    if not is_super_admin(user_id):
        await update.message.reply_text(MESSAGES["super_admin_only"])
        return
    
    if not context.args:
        await update.message.reply_text("⚠️ Usage: `/unbanuser <user_id>`")
        return
    
    try:
        target_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ ভুল User ID!")
        return
    
    user_db.unban_user(target_id)
    await update.message.reply_text(f"🔓 ইউজার `{target_id}` আনব্যান করা হয়েছে!", parse_mode="MarkdownV2")

# ==================== SUB ADMIN COMMANDS ====================

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sub Admin Panel"""
    user_id = update.effective_user.id
    
    if not is_any_admin(user_id):
        await update.message.reply_text(MESSAGES["admin_only"])
        return
    
    # Super admin gets super panel
    if is_super_admin(user_id):
        await super_admin_panel(update, context)
        return
    
    keyboard = create_keyboard([
        InlineKeyboardButton("➕ Create Tournament", callback_data="ad_create_tour"),
        InlineKeyboardButton("📝 My Tournaments", callback_data="ad_my_tours"),
        InlineKeyboardButton("🗑️ Delete Tournament", callback_data="ad_del_tour"),
        InlineKeyboardButton("📋 Assign Task", callback_data="ad_assign_task"),
        InlineKeyboardButton("🔐 Set Room Info", callback_data="ad_room_info"),
        InlineKeyboardButton("📢 Live Update", callback_data="ad_live_update"),
        InlineKeyboardButton("📊 My Stats", callback_data="ad_my_stats"),
        InlineKeyboardButton("🏠 Back to Menu", callback_data="main_menu"),
    ], per_row=2)
    
    await update.message.reply_text(
        "👮 *Admin Panel*\\n\\nসাব এডমিন কন্ট্রোল প্যানেলে স্বাগতম!",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="MarkdownV2"
    )

async def create_tournament_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Create new tournament (Sub Admin)"""
    user_id = update.effective_user.id
    
    if not is_sub_admin(user_id) and not is_super_admin(user_id):
        await update.message.reply_text(MESSAGES["admin_only"])
        return
    
    if len(context.args) < 1:
        await update.message.reply_text(
            "⚠️ Usage: `/createtour <name> [type] [max_players] [min_level] [prize] [start_time]`\\n\\n"
            "উদাহরণ: `/createtour Night Cup squad 48 40 1000TK 2024-01-15 20:00`"
        )
        return
    
    name = context.args[0]
    ttype = context.args[1] if len(context.args) > 1 else "squad"
    max_players = int(context.args[2]) if len(context.args) > 2 else 48
    min_level = int(context.args[3]) if len(context.args) > 3 else 40
    prize = context.args[4] if len(context.args) > 4 else ""
    start_time = " ".join(context.args[5:]) if len(context.args) > 5 else ""
    
    # Delete old tournaments when creating new one
    tour_db.delete_old_tournaments(user_id, "")
    
    tid = tour_db.create_tournament(
        admin_id=user_id,
        name=name,
        ttype=ttype,
        max_players=max_players,
        min_level=min_level,
        prize=prize,
        start_time=start_time
    )
    
    await update.message.reply_text(
        MESSAGES["tournament_created"].format(tid=tid) + f"\\n\\n🏆 নাম: {escape_markdown(name)}",
        parse_mode="MarkdownV2"
    )

async def my_tournaments_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show admin's tournaments"""
    user_id = update.effective_user.id
    
    if not is_any_admin(user_id):
        await update.message.reply_text(MESSAGES["admin_only"])
        return
    
    tournaments = tour_db.get_admin_tournaments(user_id)
    
    if not tournaments:
        await update.message.reply_text("📭 আপনার কোনো টুর্নামেন্ট নেই!")
        return
    
    text = "🎮 *আপনার টুর্নামেন্টগুলো:*\\n\\n"
    for tour in tournaments:
        status_emoji = "🟢" if tour.get("status") == "live" else "🟡" if tour.get("status") == "upcoming" else "🔴"
        text += f"{status_emoji} *{escape_markdown(tour['name'])}*\\n"
        text += f"🆔 `{tour['id']}`\\n"
        text += f"👥 Teams: {len(tour.get('teams', []))}/{tour.get('max_players', 48)}\\n"
        text += f"💰 Prize: {escape_markdown(tour.get('prize', 'N/A'))}\\n"
        text += f"⏰ Start: {escape_markdown(tour.get('start_time', 'TBA'))}\\n\\n"
    
    await update.message.reply_text(text, parse_mode="MarkdownV2")

async def delete_tournament_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Delete a tournament"""
    user_id = update.effective_user.id
    
    if not is_any_admin(user_id):
        await update.message.reply_text(MESSAGES["admin_only"])
        return
    
    if not context.args:
        await update.message.reply_text("⚠️ Usage: `/deltour <tournament_id>`")
        return
    
    tid = context.args[0]
    tour = tour_db.get_tournament(tid)
    
    if not tour:
        await update.message.reply_text("❌ টুর্নামেন্ট পাওয়া যায়নি!")
        return
    
    # Only super admin or the creator can delete
    if tour.get("admin_id") != user_id and not is_super_admin(user_id):
        await update.message.reply_text("🚫 আপনি এই টুর্নামেন্ট ডিলিট করতে পারবেন না!")
        return
    
    tour_db.delete_tournament(tid)
    await update.message.reply_text(MESSAGES["tournament_deleted"])

async def assign_task_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Assign task for room ID/password"""
    user_id = update.effective_user.id
    
    if not is_any_admin(user_id):
        await update.message.reply_text(MESSAGES["admin_only"])
        return
    
    if len(context.args) < 3:
        await update.message.reply_text(
            "⚠️ Usage: `/assigntask <tournament_id> <link> <description>`\\n\\n"
            "উদাহরণ: `/assigntask T123 https://example.com 'Visit this site and take screenshot'`"
        )
        return
    
    tid = context.args[0]
    link = context.args[1]
    description = " ".join(context.args[2:])
    
    tour = tour_db.get_tournament(tid)
    if not tour:
        await update.message.reply_text("❌ টুর্নামেন্ট পাওয়া যায়নি!")
        return
    
    if tour.get("admin_id") != user_id and not is_super_admin(user_id):
        await update.message.reply_text("🚫 অন্যের টুর্নামেন্টে টাস্ক দিতে পারবেন না!")
        return
    
    task_id = task_db.create_task(user_id, tid, link, description)
    
    await update.message.reply_text(
        MESSAGES["task_assigned"].format(link=link, description=description),
        parse_mode="MarkdownV2"
    )

async def set_room_info_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set room ID and password"""
    user_id = update.effective_user.id
    
    if not is_any_admin(user_id):
        await update.message.reply_text(MESSAGES["admin_only"])
        return
    
    if len(context.args) < 3:
        await update.message.reply_text(
            "⚠️ Usage: `/setroom <tournament_id> <room_id> <password>`"
        )
        return
    
    tid = context.args[0]
    room_id = context.args[1]
    room_pass = context.args[2]
    
    tour = tour_db.get_tournament(tid)
    if not tour:
        await update.message.reply_text("❌ টুর্নামেন্ট পাওয়া যায়নি!")
        return
    
    if tour.get("admin_id") != user_id and not is_super_admin(user_id):
        await update.message.reply_text("🚫 অন্যের টুর্নামেন্ট এডিট করতে পারবেন না!")
        return
    
    tour_db.update_tournament(tid, {
        "room_id": room_id,
        "room_pass": room_pass
    })
    
    await update.message.reply_text(
        f"✅ রুম তথ্য আপডেট হয়েছে!\\n\\n🆔 Room ID: `{room_id}`\\n🔑 Password: `{room_pass}`",
        parse_mode="MarkdownV2"
    )

async def live_update_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add live update to tournament"""
    user_id = update.effective_user.id
    
    if not is_any_admin(user_id):
        await update.message.reply_text(MESSAGES["admin_only"])
        return
    
    if len(context.args) < 2:
        await update.message.reply_text(
            "⚠️ Usage: `/live <tournament_id> <message>`"
        )
        return
    
    tid = context.args[0]
    message = " ".join(context.args[1:])
    
    tour = tour_db.get_tournament(tid)
    if not tour:
        await update.message.reply_text("❌ টুর্নামেন্ট পাওয়া যায়নি!")
        return
    
    if tour.get("admin_id") != user_id and not is_super_admin(user_id):
        await update.message.reply_text("🚫 অন্যের টুর্নামেন্টে আপডেট দিতে পারবেন না!")
        return
    
    tour_db.add_live_update(tid, message)
    
    await update.message.reply_text(f"📢 লাইভ আপডেট পোস্ট করা হয়েছে!\\n\\n📝 {message}")

async def admin_stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show admin statistics"""
    user_id = update.effective_user.id
    
    if not is_any_admin(user_id):
        await update.message.reply_text(MESSAGES["admin_only"])
        return
    
    my_tours = tour_db.get_admin_tournaments(user_id)
    total_teams = sum(len(t.get("teams", [])) for t in my_tours)
    
    text = f"""📊 *আপনার স্ট্যাটিস্টিক্স:*

🎮 টুর্নামেন্ট: {len(my_tours)}
👥 মোট টিম: {total_teams}
📅 আপডেট: {time.strftime('%Y-%m-%d %H:%M')}"""
    
    await update.message.reply_text(text, parse_mode="MarkdownV2")
'''

with open('/mnt/agents/output/admin_handlers.py', 'w', encoding='utf-8') as f:
    f.write(admin_handlers_content)

print("✅ admin_handlers.py created")
