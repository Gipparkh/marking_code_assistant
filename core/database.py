import sqlite3
import os
import sys
from core.config import DATABASE_PATH


def get_db_path():
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    db_dir = os.path.join(base_path, "db")
    os.makedirs(db_dir, exist_ok=True)
    return os.path.join(db_dir, "database.db")


DB_PATH = get_db_path()


def init_db():
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL CHECK(type IN ('generated', 'manual')),
                marking_group TEXT,
                short_ean TEXT,
                full_code TEXT,
                comment TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


def add_generated_item(name: str, marking_group: str, short_ean: str, comment: str = ""):
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.execute("""
            INSERT INTO items (name, type, marking_group, short_ean, comment)
            VALUES (?, ?, ?, ?, ?)
        """, (name, "generated", marking_group, short_ean, comment or None))
        conn.commit()


def add_manual_item(name: str, full_code: str, comment: str = ""):
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.execute("""
            INSERT INTO items (name, type, full_code, comment)
            VALUES (?, ?, ?, ?)
        """, (name, "manual", full_code, comment or None))
        conn.commit()


def delete_item_by_id(item_id: int):
    with sqlite3.connect(DATABASE_PATH) as conn:
        cur = conn.execute("DELETE FROM items WHERE id = ?", (item_id,))
        conn.commit()
        return cur.rowcount > 0


def search_items(item_type: str = None, group_filter: str = None, name_query: str = ""):
    with sqlite3.connect(DATABASE_PATH) as conn:
        conditions = []
        params = []

        if item_type:
            conditions.append("type = ?")
            params.append(item_type)

        if group_filter and item_type != "manual":
            conditions.append("marking_group = ?")
            params.append(group_filter)

        if name_query:
            conditions.append("name LIKE ?")
            params.append(f"%{name_query}%")

        where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
        query = f"SELECT id, name, type, marking_group, short_ean, full_code, comment FROM items{where_clause} ORDER BY created_at DESC"
        cursor = conn.execute(query, params)
        return cursor.fetchall()