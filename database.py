"""
Database Module - Lab Management & Analytics System
Supports SQLite (default) and PostgreSQL (cloud-ready via DATABASE_URL)
"""

import json
import os
import shutil
import sqlite3
import uuid
from datetime import datetime

DATABASE_PATH = "lab_management.db"
_FORCE_SQLITE_FALLBACK = False

PERFORMA_TABLES = {
    "data_retrieval_reports",
    "lab_activity",
    "special_checking_in_lab",
    "daily_checking_report",
    "monthly_site_checking_report",
    "ami_mdi_tcps",
    "audit_record",
    "court_cases",
    "log_book_record",
    "ta_da_record",
}


def _get_database_url():
    url = os.getenv("DATABASE_URL")
    if url:
        return url

    try:
        import streamlit as st

        if "DATABASE_URL" in st.secrets:
            return st.secrets["DATABASE_URL"]
    except Exception:
        pass

    return None


def _is_postgres():
    global _FORCE_SQLITE_FALLBACK
    if _FORCE_SQLITE_FALLBACK:
        return False
    url = _get_database_url()
    return bool(url and url.startswith(("postgres://", "postgresql://")))


def _db_kind():
    return "postgres" if _is_postgres() else "sqlite"


def _convert_placeholders(query):
    if _is_postgres():
        return query.replace("?", "%s")
    return query


def _safe_table_name(table_name):
    if table_name not in PERFORMA_TABLES:
        raise ValueError(f"Invalid table name: {table_name}")
    return table_name


def get_connection():
    """Get database connection."""
    global _FORCE_SQLITE_FALLBACK

    if _is_postgres():
        try:
            import psycopg2

            return psycopg2.connect(_get_database_url())
        except Exception as exc:
            _FORCE_SQLITE_FALLBACK = True
            print(f"[database] PostgreSQL unavailable, falling back to SQLite. Reason: {exc}")

    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def _to_dict_rows(rows, columns=None):
    if not rows:
        return []

    if _is_postgres():
        if columns is None:
            return []
        return [dict(zip(columns, row)) for row in rows]

    return [dict(row) for row in rows]


def _execute(query, params=None, fetch=None):
    params = params or []
    conn = get_connection()
    cur = conn.cursor()

    try:
        sql = _convert_placeholders(query)
        cur.execute(sql, params)

        if fetch == "one":
            row = cur.fetchone()
            if row is None:
                result = None
            elif _is_postgres():
                columns = [d[0] for d in cur.description]
                result = dict(zip(columns, row))
            else:
                result = dict(row)
            conn.commit()
            return result

        if fetch == "all":
            rows = cur.fetchall()
            columns = [d[0] for d in cur.description] if _is_postgres() else None
            result = _to_dict_rows(rows, columns)
            conn.commit()
            return result

        if fetch == "scalar":
            row = cur.fetchone()
            conn.commit()
            return row[0] if row else None

        if fetch == "lastrowid":
            last_id = cur.lastrowid if not _is_postgres() else None
            conn.commit()
            return last_id

        conn.commit()
        return None
    finally:
        cur.close()
        conn.close()


def init_database():
    """Initialize all database tables."""
    user_pk = "SERIAL PRIMARY KEY" if _is_postgres() else "INTEGER PRIMARY KEY AUTOINCREMENT"
    id_pk = "SERIAL PRIMARY KEY" if _is_postgres() else "INTEGER PRIMARY KEY AUTOINCREMENT"

    _execute(
        f'''
        CREATE TABLE IF NOT EXISTS users (
            user_id {user_pk},
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin', 'staff')),
            full_name TEXT NOT NULL,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        '''
    )

    _execute(
        '''
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            logout_time TIMESTAMP,
            is_active INTEGER DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
        '''
    )

    _execute(
        f'''
        CREATE TABLE IF NOT EXISTS activity_logs (
            log_id {id_pk},
            username TEXT NOT NULL,
            role TEXT NOT NULL,
            session_id TEXT NOT NULL,
            performa_name TEXT NOT NULL,
            action_type TEXT NOT NULL CHECK(action_type IN ('Add', 'Edit', 'Delete', 'Print', 'Unlock')),
            reference_no TEXT,
            record_id INTEGER,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            details TEXT
        )
        '''
    )

    _execute(
        f'''
        CREATE TABLE IF NOT EXISTS theme_settings (
            setting_id {id_pk},
            background_color TEXT DEFAULT '#0E1117',
            sidebar_color TEXT DEFAULT '#262730',
            text_color TEXT DEFAULT '#FAFAFA',
            card_color TEXT DEFAULT '#1E1E1E',
            primary_color TEXT DEFAULT '#FF4B4B',
            updated_by TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        '''
    )

    for performa in PERFORMA_TABLES:
        _execute(
            f'''
            CREATE TABLE IF NOT EXISTS {performa} (
                id {id_pk},
                s_no INTEGER,
                sub_division TEXT,
                reference_no TEXT NOT NULL,
                name TEXT,
                tariff TEXT,
                load TEXT,
                meter_no TEXT,
                make TEXT,
                mco_no TEXT,
                mco_date DATE,
                bill_reading REAL DEFAULT 0,
                meter_reading REAL DEFAULT 0,
                difference REAL DEFAULT 0,
                status TEXT DEFAULT 'Active',
                remarks TEXT,
                entry_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by TEXT,
                is_locked INTEGER DEFAULT 0,
                locked_at TIMESTAMP,
                last_edited_by TEXT,
                last_edited_at TIMESTAMP
            )
            '''
        )

    theme_count = _execute("SELECT COUNT(*) FROM theme_settings", fetch="scalar")
    if int(theme_count or 0) == 0:
        _execute(
            '''
            INSERT INTO theme_settings (background_color, sidebar_color, text_color, card_color, primary_color)
            VALUES (?, ?, ?, ?, ?)
            ''',
            ["#0E1117", "#262730", "#FAFAFA", "#1E1E1E", "#FF4B4B"],
        )


def create_default_users():
    """Create default admin and staff users."""
    import bcrypt

    users_count = _execute("SELECT COUNT(*) FROM users", fetch="scalar")
    if int(users_count or 0) > 0:
        return

    users = [
        ("admin", "Admin@123", "admin", "Administrator"),
        ("staff1", "Staff@123", "staff", "Staff User 1"),
        ("staff2", "Staff@123", "staff", "Staff User 2"),
    ]

    for username, password, role, full_name in users:
        password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        _execute(
            """
            INSERT INTO users (username, password_hash, role, full_name)
            VALUES (?, ?, ?, ?)
            """,
            [username, password_hash, role, full_name],
        )


# ==================== USER OPERATIONS ====================

def verify_user(username, password):
    """Verify user credentials."""
    import bcrypt

    user = _execute(
        "SELECT * FROM users WHERE username = ? AND is_active = 1",
        [username],
        fetch="one",
    )

    if user and bcrypt.checkpw(password.encode("utf-8"), user["password_hash"].encode("utf-8")):
        return user
    return None


def create_session(user_id):
    """Create new session for user."""
    session_id = str(uuid.uuid4())
    _execute(
        "INSERT INTO sessions (session_id, user_id) VALUES (?, ?)",
        [session_id, user_id],
    )
    return session_id


def end_session(session_id):
    """End a session."""
    _execute(
        """
        UPDATE sessions
        SET is_active = 0, logout_time = CURRENT_TIMESTAMP
        WHERE session_id = ?
        """,
        [session_id],
    )


def get_all_users():
    """Get all users."""
    return _execute(
        "SELECT user_id, username, role, full_name, is_active, created_at FROM users",
        fetch="all",
    )


# ==================== ACTIVITY LOG OPERATIONS ====================

def log_activity(username, role, session_id, performa_name, action_type, reference_no=None, record_id=None, details=None):
    """Log user activity."""
    _execute(
        """
        INSERT INTO activity_logs
        (username, role, session_id, performa_name, action_type, reference_no, record_id, details)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [username, role, session_id, performa_name, action_type, reference_no, record_id, details],
    )


def get_recent_activities(limit=10):
    """Get recent activities."""
    return _execute(
        "SELECT * FROM activity_logs ORDER BY timestamp DESC LIMIT ?",
        [limit],
        fetch="all",
    )


def get_activities_filtered(username=None, start_date=None, end_date=None, performa=None, session_id=None):
    """Get filtered activities."""
    query = "SELECT * FROM activity_logs WHERE 1=1"
    params = []

    if username:
        query += " AND username = ?"
        params.append(username)

    if start_date:
        query += " AND DATE(timestamp) >= ?"
        params.append(start_date)

    if end_date:
        query += " AND DATE(timestamp) <= ?"
        params.append(end_date)

    if performa:
        query += " AND performa_name = ?"
        params.append(performa)

    if session_id:
        query += " AND session_id = ?"
        params.append(session_id)

    query += " ORDER BY timestamp DESC"
    return _execute(query, params, fetch="all")


def get_unique_sessions():
    """Get unique session IDs for filtering."""
    return _execute(
        """
        SELECT DISTINCT session_id, username, MIN(timestamp) AS first_activity
        FROM activity_logs
        GROUP BY session_id, username
        ORDER BY first_activity DESC
        """,
        fetch="all",
    )


# ==================== PERFORMA CRUD OPERATIONS ====================

def get_table_name(performa_display_name):
    """Convert display name to table name."""
    mapping = {
        "Data Retrieval Reports": "data_retrieval_reports",
        "Lab Activity": "lab_activity",
        "Special Checking in Lab": "special_checking_in_lab",
        "Daily Checking Report": "daily_checking_report",
        "Monthly Site Checking Report": "monthly_site_checking_report",
        "AMI MDI TCPs": "ami_mdi_tcps",
        "Audit Record": "audit_record",
        "Court Cases": "court_cases",
        "Log Book Record": "log_book_record",
        "TA/DA Record": "ta_da_record",
    }
    return mapping.get(performa_display_name, "")


def get_next_sno(table_name):
    """Get next S.No for a table."""
    table = _safe_table_name(table_name)
    value = _execute(f"SELECT COALESCE(MAX(s_no), 0) + 1 FROM {table}", fetch="scalar")
    return int(value or 1)


def add_record(table_name, data, created_by):
    """Add new record to performa."""
    table = _safe_table_name(table_name)

    bill_reading = float(data.get("bill_reading", 0) or 0)
    meter_reading = float(data.get("meter_reading", 0) or 0)
    difference = meter_reading - bill_reading
    s_no = get_next_sno(table)

    query = f'''
        INSERT INTO {table} (
            s_no, sub_division, reference_no, name, tariff, load, meter_no,
            make, mco_no, mco_date, bill_reading, meter_reading, difference,
            status, remarks, created_by, is_locked
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
    '''

    params = [
        s_no,
        data.get("sub_division"),
        data.get("reference_no"),
        data.get("name"),
        data.get("tariff"),
        data.get("load"),
        data.get("meter_no"),
        data.get("make"),
        data.get("mco_no"),
        data.get("mco_date"),
        bill_reading,
        meter_reading,
        difference,
        data.get("status", "Active"),
        data.get("remarks"),
        created_by,
    ]

    if _is_postgres():
        row = _execute(query + " RETURNING id", params, fetch="one")
        return row["id"]

    _execute(query, params)
    return _execute("SELECT last_insert_rowid()", fetch="scalar")


def update_record(table_name, record_id, data, edited_by):
    """Update existing record."""
    table = _safe_table_name(table_name)

    bill_reading = float(data.get("bill_reading", 0) or 0)
    meter_reading = float(data.get("meter_reading", 0) or 0)
    difference = meter_reading - bill_reading

    _execute(
        f'''
        UPDATE {table} SET
            sub_division = ?, reference_no = ?, name = ?, tariff = ?, load = ?,
            meter_no = ?, make = ?, mco_no = ?, mco_date = ?, bill_reading = ?,
            meter_reading = ?, difference = ?, status = ?, remarks = ?,
            last_edited_by = ?, last_edited_at = CURRENT_TIMESTAMP
        WHERE id = ?
        ''',
        [
            data.get("sub_division"),
            data.get("reference_no"),
            data.get("name"),
            data.get("tariff"),
            data.get("load"),
            data.get("meter_no"),
            data.get("make"),
            data.get("mco_no"),
            data.get("mco_date"),
            bill_reading,
            meter_reading,
            difference,
            data.get("status"),
            data.get("remarks"),
            edited_by,
            record_id,
        ],
    )


def delete_record(table_name, record_id):
    """Delete a record (Admin only)."""
    table = _safe_table_name(table_name)
    _execute(f"DELETE FROM {table} WHERE id = ?", [record_id])


def lock_record(table_name, record_id):
    """Lock a record after save/print."""
    table = _safe_table_name(table_name)
    _execute(
        f"UPDATE {table} SET is_locked = 1, locked_at = CURRENT_TIMESTAMP WHERE id = ?",
        [record_id],
    )


def unlock_record(table_name, record_id):
    """Unlock a record (Admin only)."""
    table = _safe_table_name(table_name)
    _execute(
        f"UPDATE {table} SET is_locked = 0, locked_at = NULL WHERE id = ?",
        [record_id],
    )


def get_record_by_id(table_name, record_id):
    """Get single record by ID."""
    table = _safe_table_name(table_name)
    return _execute(f"SELECT * FROM {table} WHERE id = ?", [record_id], fetch="one")


def get_all_records(table_name, search_term=None, start_date=None, end_date=None):
    """Get all records with optional filters."""
    table = _safe_table_name(table_name)

    query = f"SELECT * FROM {table} WHERE 1=1"
    params = []

    if search_term:
        query += " AND (name LIKE ? OR meter_no LIKE ? OR reference_no LIKE ?)"
        search_pattern = f"%{search_term}%"
        params.extend([search_pattern, search_pattern, search_pattern])

    if start_date:
        query += " AND DATE(entry_date) >= ?"
        params.append(start_date)

    if end_date:
        query += " AND DATE(entry_date) <= ?"
        params.append(end_date)

    query += " ORDER BY s_no DESC"
    return _execute(query, params, fetch="all")


def get_record_count(table_name):
    """Get total record count for a table."""
    table = _safe_table_name(table_name)
    return int(_execute(f"SELECT COUNT(*) FROM {table}", fetch="scalar") or 0)


# ==================== THEME OPERATIONS ====================

def get_theme_settings():
    """Get current theme settings."""
    theme = _execute("SELECT * FROM theme_settings ORDER BY setting_id DESC LIMIT 1", fetch="one")
    if theme:
        return theme
    return {
        "background_color": "#0E1117",
        "sidebar_color": "#262730",
        "text_color": "#FAFAFA",
        "card_color": "#1E1E1E",
        "primary_color": "#FF4B4B",
    }


def update_theme_settings(background_color, sidebar_color, text_color, card_color, primary_color, updated_by):
    """Update theme settings."""
    _execute(
        """
        UPDATE theme_settings SET
            background_color = ?, sidebar_color = ?, text_color = ?,
            card_color = ?, primary_color = ?, updated_by = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE setting_id = (SELECT MAX(setting_id) FROM theme_settings)
        """,
        [background_color, sidebar_color, text_color, card_color, primary_color, updated_by],
    )


# ==================== BACKUP OPERATIONS ====================

def backup_database(backup_path=None):
    """Create database backup.

    - SQLite: copies .db file.
    - PostgreSQL: creates JSON dump of all app tables.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if not _is_postgres():
        if backup_path is None:
            backup_path = f"backup_lab_management_{timestamp}.db"
        shutil.copy2(DATABASE_PATH, backup_path)
        return backup_path

    if backup_path is None:
        backup_path = f"backup_lab_management_{timestamp}.json"

    dump = {
        "generated_at": datetime.now().isoformat(),
        "database": "postgres",
        "users": _execute("SELECT * FROM users", fetch="all"),
        "sessions": _execute("SELECT * FROM sessions", fetch="all"),
        "activity_logs": _execute("SELECT * FROM activity_logs", fetch="all"),
        "theme_settings": _execute("SELECT * FROM theme_settings", fetch="all"),
        "performas": {},
    }

    for table in sorted(PERFORMA_TABLES):
        dump["performas"][table] = _execute(f"SELECT * FROM {table}", fetch="all")

    with open(backup_path, "w", encoding="utf-8") as f:
        json.dump(dump, f, default=str, ensure_ascii=False, indent=2)

    return backup_path


def get_dashboard_stats():
    """Get statistics for dashboard."""
    stats = {}
    total = 0

    for table in PERFORMA_TABLES:
        count = int(_execute(f"SELECT COUNT(*) FROM {table}", fetch="scalar") or 0)
        stats[table] = count
        total += count

    stats["total_records"] = total

    today_entries_query = (
        "SELECT COUNT(*) FROM activity_logs WHERE DATE(timestamp) = CURRENT_DATE AND action_type = 'Add'"
        if _is_postgres()
        else "SELECT COUNT(*) FROM activity_logs WHERE DATE(timestamp) = DATE('now') AND action_type = 'Add'"
    )

    active_users_query = (
        "SELECT COUNT(DISTINCT username) FROM activity_logs WHERE DATE(timestamp) = CURRENT_DATE"
        if _is_postgres()
        else "SELECT COUNT(DISTINCT username) FROM activity_logs WHERE DATE(timestamp) = DATE('now')"
    )

    stats["today_entries"] = int(_execute(today_entries_query, fetch="scalar") or 0)
    stats["active_users_today"] = int(_execute(active_users_query, fetch="scalar") or 0)

    return stats


if __name__ == "__main__":
    init_database()
    create_default_users()
    print(f"Database initialized successfully! Backend: {_db_kind()}")
