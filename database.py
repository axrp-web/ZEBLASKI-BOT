import sqlite3
import os
from typing import Optional, Dict, Any, List

DB_PATH = os.path.join(os.path.dirname(__file__), "applications.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Gang Applications table (Recruitment)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        username TEXT NOT NULL,
        display_name TEXT,
        avatar_url TEXT,
        new_gang_name TEXT,
        current_level TEXT,
        ig_name TEXT,
        ph_number TEXT,
        ooc_name TEXT,
        ooc_age TEXT,
        experience TEXT,
        reason_for_change TEXT,
        status TEXT DEFAULT 'PENDING',
        mod_message_id INTEGER,
        mod_channel_id INTEGER,
        moderator_id INTEGER,
        moderator_name TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        reviewed_at TIMESTAMP
    )
    """)
    
    # 2. In-Game Name Registrations table (IGN System)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ign_registrations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        username TEXT NOT NULL,
        display_name TEXT,
        avatar_url TEXT,
        ooc_name TEXT,
        ig_name TEXT,
        server_name TEXT,
        current_level TEXT,
        status TEXT DEFAULT 'PENDING',
        mod_message_id INTEGER,
        mod_channel_id INTEGER,
        moderator_id INTEGER,
        moderator_name TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        reviewed_at TIMESTAMP
    )
    """)
    
    # 3. Guild settings table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS guild_settings (
        guild_id INTEGER PRIMARY KEY,
        mod_role_id INTEGER,
        review_channel_id INTEGER,
        results_channel_id INTEGER,
        member_role_id INTEGER,
        ign_review_channel_id INTEGER,
        ign_results_channel_id INTEGER
    )
    """)
    
    # Ensure newly added columns exist in case table was previously created
    for col in ["ign_review_channel_id", "ign_results_channel_id"]:
        try:
            cursor.execute(f"ALTER TABLE guild_settings ADD COLUMN {col} INTEGER")
        except sqlite3.OperationalError:
            pass  # column already exists
            
    conn.commit()
    conn.close()

# -------------------------------------------------------------
# GANG APPLICATIONS CRUD
# -------------------------------------------------------------

def create_application(data: Dict[str, Any]) -> int:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO applications (
        user_id, username, display_name, avatar_url,
        new_gang_name, current_level, ig_name, ph_number,
        ooc_name, ooc_age, experience, reason_for_change, status
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'PENDING')
    """, (
        data['user_id'], data['username'], data['display_name'], data.get('avatar_url'),
        data['new_gang_name'], data['current_level'], data['ig_name'], data['ph_number'],
        data['ooc_name'], data['ooc_age'], data['experience'], data['reason_for_change']
    ))
    app_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return app_id

def update_application_message(app_id: int, message_id: int, channel_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE applications
    SET mod_message_id = ?, mod_channel_id = ?
    WHERE id = ?
    """, (message_id, channel_id, app_id))
    conn.commit()
    conn.close()

def get_application(app_id: int) -> Optional[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM applications WHERE id = ?", (app_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def update_application_status(app_id: int, status: str, moderator_id: int, moderator_name: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE applications
    SET status = ?, moderator_id = ?, moderator_name = ?, reviewed_at = CURRENT_TIMESTAMP
    WHERE id = ?
    """, (status, moderator_id, moderator_name, app_id))
    conn.commit()
    conn.close()

def get_pending_applications() -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM applications WHERE status = 'PENDING'")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# -------------------------------------------------------------
# IGN REGISTRATIONS CRUD
# -------------------------------------------------------------

def create_ign_registration(data: Dict[str, Any]) -> int:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO ign_registrations (
        user_id, username, display_name, avatar_url,
        ooc_name, ig_name, server_name, current_level, status
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'PENDING')
    """, (
        data['user_id'], data['username'], data['display_name'], data.get('avatar_url'),
        data['ooc_name'], data['ig_name'], data['server_name'], data['current_level']
    ))
    reg_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return reg_id

def update_ign_registration_message(reg_id: int, message_id: int, channel_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE ign_registrations
    SET mod_message_id = ?, mod_channel_id = ?
    WHERE id = ?
    """, (message_id, channel_id, reg_id))
    conn.commit()
    conn.close()

def get_ign_registration(reg_id: int) -> Optional[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ign_registrations WHERE id = ?", (reg_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def update_ign_registration_status(reg_id: int, status: str, moderator_id: int, moderator_name: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE ign_registrations
    SET status = ?, moderator_id = ?, moderator_name = ?, reviewed_at = CURRENT_TIMESTAMP
    WHERE id = ?
    """, (status, moderator_id, moderator_name, reg_id))
    conn.commit()
    conn.close()

def get_pending_ign_registrations() -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ign_registrations WHERE status = 'PENDING'")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# -------------------------------------------------------------
# GUILD SETTINGS
# -------------------------------------------------------------

def get_guild_settings(guild_id: int) -> Dict[str, Any]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM guild_settings WHERE guild_id = ?", (guild_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return {
        'guild_id': guild_id,
        'mod_role_id': None,
        'review_channel_id': None,
        'results_channel_id': None,
        'member_role_id': None,
        'ign_review_channel_id': None,
        'ign_results_channel_id': None
    }

def update_guild_setting(guild_id: int, key: str, value: Any):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO guild_settings (guild_id) VALUES (?)", (guild_id,))
    cursor.execute(f"UPDATE guild_settings SET {key} = ? WHERE guild_id = ?", (value, guild_id))
    conn.commit()
    conn.close()
