
database_content = '''"""
Free Fire Tournament Bot - JSON Database Manager
Thread-safe, scalable JSON database handler
"""
import json
import os
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

class JSONDatabase:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.lock = threading.RLock()
        self._ensure_file()
    
    def _ensure_file(self):
        """Create file and directory if not exists"""
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        if not os.path.exists(self.filepath):
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
    
    def _load(self) -> Dict:
        """Load data from JSON file"""
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def _save(self, data: Dict):
        """Save data to JSON file atomically"""
        temp_file = self.filepath + '.tmp'
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(temp_file, self.filepath)
    
    def get(self, key: str, default=None) -> Any:
        with self.lock:
            data = self._load()
            return data.get(key, default)
    
    def set(self, key: str, value: Any):
        with self.lock:
            data = self._load()
            data[key] = value
            self._save(data)
    
    def delete(self, key: str) -> bool:
        with self.lock:
            data = self._load()
            if key in data:
                del data[key]
                self._save(data)
                return True
            return False
    
    def get_all(self) -> Dict:
        with self.lock:
            return self._load()
    
    def update(self, key: str, updates: Dict):
        with self.lock:
            data = self._load()
            if key not in data:
                data[key] = {}
            if isinstance(data[key], dict):
                data[key].update(updates)
            else:
                data[key] = updates
            self._save(data)
    
    def find(self, condition) -> List[Dict]:
        """Find all items matching condition"""
        with self.lock:
            data = self._load()
            return [v for v in data.values() if condition(v)]
    
    def keys(self) -> List[str]:
        with self.lock:
            return list(self._load().keys())


class UserDB(JSONDatabase):
    def __init__(self, filepath: str):
        super().__init__(filepath)
    
    def get_user(self, user_id: int) -> Dict:
        return self.get(str(user_id), {
            "user_id": user_id,
            "username": "",
            "first_name": "",
            "unlocked_until": 0,
            "is_banned": False,
            "joined_at": time.time(),
            "tasks_completed": [],
            "tournaments_joined": []
        })
    
    def update_user(self, user_id: int, updates: Dict):
        self.update(str(user_id), updates)
    
    def is_unlocked(self, user_id: int) -> bool:
        user = self.get_user(user_id)
        if user.get("is_banned", False):
            return False
        return time.time() < user.get("unlocked_until", 0)
    
    def unlock_user(self, user_id: int, hours: int = 24):
        unlock_time = time.time() + (hours * 3600)
        self.update_user(user_id, {"unlocked_until": unlock_time})
    
    def ban_user(self, user_id: int, reason: str = ""):
        self.update_user(user_id, {"is_banned": True, "ban_reason": reason})
    
    def unban_user(self, user_id: int):
        self.update_user(user_id, {"is_banned": False, "ban_reason": ""})
    
    def get_unlock_expiry(self, user_id: int) -> str:
        user = self.get_user(user_id)
        expiry = user.get("unlocked_until", 0)
        if expiry > time.time():
            dt = datetime.fromtimestamp(expiry)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        return "Expired"
    
    def get_stats(self) -> Dict:
        data = self.get_all()
        total = len(data)
        banned = sum(1 for u in data.values() if u.get("is_banned", False))
        unlocked = sum(1 for u in data.values() if self.is_unlocked(u.get("user_id", 0)))
        return {"total": total, "banned": banned, "unlocked": unlocked}


class TournamentDB(JSONDatabase):
    def __init__(self, filepath: str):
        super().__init__(filepath)
    
    def create_tournament(self, admin_id: int, name: str, ttype: str = "squad", 
                         max_players: int = 48, min_level: int = 40,
                         prize: str = "", start_time: str = "", 
                         room_id: str = "", room_pass: str = "") -> str:
        tid = f"T{int(time.time())}_{admin_id}"
        tournament = {
            "id": tid,
            "admin_id": admin_id,
            "name": name,
            "type": ttype,
            "max_players": max_players,
            "min_level": min_level,
            "prize": prize,
            "start_time": start_time,
            "room_id": room_id,
            "room_pass": room_pass,
            "teams": [],
            "status": "upcoming",  # upcoming, live, completed
            "created_at": time.time(),
            "tasks": [],
            "live_updates": []
        }
        self.set(tid, tournament)
        return tid
    
    def get_tournament(self, tid: str) -> Optional[Dict]:
        return self.get(tid)
    
    def get_admin_tournaments(self, admin_id: int) -> List[Dict]:
        return self.find(lambda t: t.get("admin_id") == admin_id)
    
    def delete_tournament(self, tid: str) -> bool:
        return self.delete(tid)
    
    def update_tournament(self, tid: str, updates: Dict):
        self.update(tid, updates)
    
    def add_team(self, tid: str, team_data: Dict):
        tour = self.get_tournament(tid)
        if tour:
            teams = tour.get("teams", [])
            teams.append(team_data)
            self.update(tid, {"teams": teams})
    
    def add_task(self, tid: str, task: Dict):
        tour = self.get_tournament(tid)
        if tour:
            tasks = tour.get("tasks", [])
            tasks.append(task)
            self.update(tid, {"tasks": tasks})
    
    def add_live_update(self, tid: str, update: str):
        tour = self.get_tournament(tid)
        if tour:
            updates = tour.get("live_updates", [])
            updates.append({"time": time.time(), "message": update})
            self.update(tid, {"live_updates": updates})
    
    def delete_old_tournaments(self, admin_id: int, keep_tid: str):
        """Delete all old tournaments of admin except keep_tid"""
        all_tours = self.get_admin_tournaments(admin_id)
        for tour in all_tours:
            if tour["id"] != keep_tid:
                self.delete(tour["id"])
    
    def get_all_tournaments(self) -> List[Dict]:
        return list(self.get_all().values())


class AdminDB(JSONDatabase):
    def __init__(self, filepath: str):
        super().__init__(filepath)
        self._init_super_admin()
    
    def _init_super_admin(self):
        from config import SUPER_ADMIN_ID
        if str(SUPER_ADMIN_ID) not in self.get_all():
            self.set(str(SUPER_ADMIN_ID), {
                "user_id": SUPER_ADMIN_ID,
                "role": "super",
                "added_at": time.time(),
                "added_by": SUPER_ADMIN_ID,
                "is_active": True
            })
    
    def is_admin(self, user_id: int) -> bool:
        admin = self.get(str(user_id))
        return admin is not None and admin.get("is_active", False)
    
    def is_super_admin(self, user_id: int) -> bool:
        admin = self.get(str(user_id))
        return admin is not None and admin.get("role") == "super" and admin.get("is_active", False)
    
    def is_sub_admin(self, user_id: int) -> bool:
        admin = self.get(str(user_id))
        return admin is not None and admin.get("role") == "sub" and admin.get("is_active", False)
    
    def add_admin(self, user_id: int, role: str = "sub", added_by: int = 0):
        self.set(str(user_id), {
            "user_id": user_id,
            "role": role,
            "added_at": time.time(),
            "added_by": added_by,
            "is_active": True
        })
    
    def remove_admin(self, user_id: int) -> bool:
        return self.delete(str(user_id))
    
    def block_admin(self, user_id: int):
        self.update(str(user_id), {"is_active": False})
    
    def unblock_admin(self, user_id: int):
        self.update(str(user_id), {"is_active": True})
    
    def get_all_admins(self) -> List[Dict]:
        return list(self.get_all().values())
    
    def get_sub_admins(self) -> List[Dict]:
        return self.find(lambda a: a.get("role") == "sub")


class UnlockCodeDB(JSONDatabase):
    def __init__(self, filepath: str):
        super().__init__(filepath)
    
    def create_code(self, user_id: int, code: str, expires_in: int = 3600) -> Dict:
        entry = {
            "user_id": user_id,
            "code": code,
            "created_at": time.time(),
            "expires_at": time.time() + expires_in,
            "used": False
        }
        self.set(code, entry)
        return entry
    
    def verify_code(self, code: str, user_id: int) -> bool:
        entry = self.get(code)
        if not entry:
            return False
        if entry.get("used", False):
            return False
        if entry.get("expires_at", 0) < time.time():
            return False
        if entry.get("user_id") != user_id:
            return False
        self.update(code, {"used": True})
        return True
    
    def cleanup_expired(self):
        """Remove expired codes"""
        data = self.get_all()
        now = time.time()
        expired = [k for k, v in data.items() if v.get("expires_at", 0) < now]
        for code in expired:
            self.delete(code)


class TaskDB(JSONDatabase):
    def __init__(self, filepath: str):
        super().__init__(filepath)
    
    def create_task(self, admin_id: int, tournament_id: str, link: str, 
                   description: str, reward_type: str = "room_info") -> str:
        task_id = f"TASK{int(time.time())}_{admin_id}"
        task = {
            "id": task_id,
            "admin_id": admin_id,
            "tournament_id": tournament_id,
            "link": link,
            "description": description,
            "reward_type": reward_type,
            "completed_by": [],
            "created_at": time.time(),
            "is_active": True
        }
        self.set(task_id, task)
        return task_id
    
    def complete_task(self, task_id: str, user_id: int) -> bool:
        task = self.get(task_id)
        if not task or not task.get("is_active", False):
            return False
        completed = task.get("completed_by", [])
        if user_id in completed:
            return False
        completed.append(user_id)
        self.update(task_id, {"completed_by": completed})
        return True
    
    def get_task(self, task_id: str) -> Optional[Dict]:
        return self.get(task_id)
    
    def get_tournament_tasks(self, tournament_id: str) -> List[Dict]:
        return self.find(lambda t: t.get("tournament_id") == tournament_id)
    
    def get_stats(self) -> Dict:
        data = self.get_all()
        total = len(data)
        completed = sum(len(t.get("completed_by", [])) for t in data.values())
        return {"total": total, "total_completions": completed}
'''

with open('/mnt/agents/output/database.py', 'w', encoding='utf-8') as f:
    f.write(database_content)

print("✅ database.py created")
