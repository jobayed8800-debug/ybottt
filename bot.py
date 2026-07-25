
bot_content = '''"""
Free Fire Tournament Bot - Main Entry Point
Complete Telegram Bot with Admin Panel, Tournament Management, and Unlock System
"""
import logging
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from config import BOT_TOKEN
from user_handlers import (
    start_cmd, unlock_cmd, enter_code_cmd, process_code,
    show_tournaments, view_tournament, do_task, complete_task,
    show_room_info, show_rules, show_about, main_menu, admin_check
)
from admin_handlers import (
    admin_panel, super_admin_panel, add_sub_admin, remove_sub_admin,
    block_admin, unblock_admin, list_all_admins, user_statistics,
    ban_user_cmd, unban_user_cmd, create_tournament_cmd, my_tournaments_cmd,
    delete_tournament_cmd, assign_task_cmd, set_room_info_cmd,
    live_update_cmd, admin_stats_cmd
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
WAITING_FOR_CODE = 1

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors caused by updates"""
    logger.error(f"Update {update} caused error {context.error}")
    
    # Notify user
    if update and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "⚠️ একটি এরর হয়েছে! অনুগ্রহ করে আবার চেষ্টা করুন।"
            )
        except:
            pass

def main():
    """Start the bot"""
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("❌ BOT_TOKEN not set! Please set your bot token in config.py or environment variable.")
        sys.exit(1)
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # ==================== USER HANDLERS ====================
    
    # Start command
    application.add_handler(CommandHandler("start", start_cmd))
    
    # Unlock conversation handler
    unlock_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(enter_code_cmd, pattern="^enter_code$")
        ],
        states={
            WAITING_FOR_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_code)]
        },
        fallbacks=[CommandHandler("cancel", lambda u, c: u.message.reply_text("Cancelled"))]
    )
    application.add_handler(unlock_conv)
    
    # Callback queries
    application.add_handler(CallbackQueryHandler(unlock_cmd, pattern="^unlock$"))
    application.add_handler(CallbackQueryHandler(show_tournaments, pattern="^tournaments$"))
    application.add_handler(CallbackQueryHandler(show_rules, pattern="^rules$"))
    application.add_handler(CallbackQueryHandler(show_about, pattern="^about$"))
    application.add_handler(CallbackQueryHandler(main_menu, pattern="^main_menu$"))
    application.add_handler(CallbackQueryHandler(admin_check, pattern="^admin_check$"))
    application.add_handler(CallbackQueryHandler(view_tournament, pattern="^view_tour_"))
    application.add_handler(CallbackQueryHandler(do_task, pattern="^do_task_"))
    application.add_handler(CallbackQueryHandler(complete_task, pattern="^complete_task_"))
    application.add_handler(CallbackQueryHandler(show_room_info, pattern="^room_info_"))
    
    # ==================== ADMIN HANDLERS ====================
    
    # Super Admin Commands
    application.add_handler(CommandHandler("superadmin", super_admin_panel))
    application.add_handler(CommandHandler("addadmin", add_sub_admin))
    application.add_handler(CommandHandler("removeadmin", remove_sub_admin))
    application.add_handler(CommandHandler("blockadmin", block_admin))
    application.add_handler(CommandHandler("unblockadmin", unblock_admin))
    application.add_handler(CommandHandler("listadmins", list_all_admins))
    application.add_handler(CommandHandler("userstats", user_statistics))
    application.add_handler(CommandHandler("banuser", ban_user_cmd))
    application.add_handler(CommandHandler("unbanuser", unban_user_cmd))
    
    # Sub Admin Commands
    application.add_handler(CommandHandler("admin", admin_panel))
    application.add_handler(CommandHandler("createtour", create_tournament_cmd))
    application.add_handler(CommandHandler("mytours", my_tournaments_cmd))
    application.add_handler(CommandHandler("deltour", delete_tournament_cmd))
    application.add_handler(CommandHandler("assigntask", assign_task_cmd))
    application.add_handler(CommandHandler("setroom", set_room_info_cmd))
    application.add_handler(CommandHandler("live", live_update_cmd))
    application.add_handler(CommandHandler("adminstats", admin_stats_cmd))
    
    # ==================== ERROR HANDLER ====================
    application.add_error_handler(error_handler)
    
    # Start bot
    logger.info("🚀 Starting Free Fire Tournament Bot...")
    logger.info("✅ Bot is running! Press Ctrl+C to stop.")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
'''

with open('/mnt/agents/output/bot.py', 'w', encoding='utf-8') as f:
    f.write(bot_content)

print("✅ bot.py created")
