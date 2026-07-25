
utils_content = '''"""
Free Fire Tournament Bot - Utility Functions
"""
import random
import string
import time
from datetime import datetime
from typing import Optional

def generate_unlock_code(length: int = 8) -> str:
    """Generate random alphanumeric code"""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=length))

def generate_unique_link(base_url: str, user_id: int) -> str:
    """Generate unique ad link for each user"""
    timestamp = int(time.time())
    token = f"{user_id}_{timestamp}_{random.randint(1000, 9999)}"
    return f"{base_url}/ad?user={user_id}&token={token}"

def format_time_remaining(until_timestamp: float) -> str:
    """Format remaining time"""
    remaining = until_timestamp - time.time()
    if remaining <= 0:
        return "Expired"
    hours = int(remaining // 3600)
    minutes = int((remaining % 3600) // 60)
    return f"{hours}h {minutes}m"

def format_timestamp(ts: float) -> str:
    """Format timestamp to readable string"""
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")

def escape_markdown(text: str) -> str:
    """Escape markdown special characters"""
    chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in chars:
        text = text.replace(char, f"\\\\{char}")
    return text

def validate_squad_rules(team: dict) -> tuple:
    """
    Validate squad against tournament rules
    Returns: (is_valid, error_message)
    """
    members = team.get("members", [])
    
    if len(members) != 4:
        return False, "স্কোয়াডে ঠিক ৪ জন থাকতে হবে!"
    
    # Check first names are same
    first_names = [m.get("first_name", "").strip().split()[0].lower() for m in members if m.get("first_name")]
    if len(set(first_names)) != 1:
        return False, "সবার প্রথম নাম একই হতে হবে!"
    
    # Check level >= 40
    for member in members:
        if member.get("level", 0) < 40:
            return False, f"{member.get('name')} এর লেভেল 40 এর কম!"
    
    # Check same guild
    guilds = [m.get("guild", "").lower() for m in members]
    if len(set(guilds)) != 1:
        return False, "সবাই একই গিল্ডের হতে হবে!"
    
    return True, "✅ স্কোয়াড ভ্যালিড!"

def create_keyboard(buttons: list, per_row: int = 2) -> list:
    """Create inline keyboard layout"""
    keyboard = []
    for i in range(0, len(buttons), per_row):
        keyboard.append(buttons[i:i+per_row])
    return keyboard
'''

with open('/mnt/agents/output/utils.py', 'w', encoding='utf-8') as f:
    f.write(utils_content)

print("✅ utils.py created")
