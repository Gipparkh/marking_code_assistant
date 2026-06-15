import json
import sqlite3
import os
import sys
from core.config import GROUPS_JSON_PATH, DATABASE_PATH


def get_resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
        base_path = os.path.dirname(base_path)

    return os.path.join(base_path, relative_path)


GROUPS_FILE = get_resource_path(os.path.join("assets", "marking_groups.json"))


def get_group_names():
    if not os.path.exists(GROUPS_FILE):
        raise FileNotFoundError(f"Файл не найден по пути: {GROUPS_FILE}")
    with open(GROUPS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        return list(data.keys())


def get_mask_by_group(group_name: str) -> str:
    if not os.path.exists(GROUPS_FILE):
        raise FileNotFoundError(f"Файл не найден по пути: {GROUPS_FILE}")
    with open(GROUPS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        if group_name not in data:
            raise ValueError(f"Группа '{group_name}' не найдена в {GROUPS_FILE}")
        return data[group_name]


DEFAULT_GROUPS = {
    "Пиво": "010{ean}215{random:6}{gs}93{random:4}",
    "Пиво БА": "010{ean}215{random:6}{gs}93{random:4}",
    "Вода": "010{ean}215{random:12}{gs}93{random:4}",
    "Напитки БА": "010{ean}215{random:12}{gs}93{random:4}",
    "Молочная продукция": "010{ean}215{random:5}{gs}93{random:4}",
    "Молочная продукция с весом": "010{ean}215{random:5}{gs}93{random:4}{gs}310{random:6}"
}


def _ensure_default_groups():
    if not os.path.exists(GROUPS_JSON_PATH):
        with open(GROUPS_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_GROUPS, f, ensure_ascii=False, indent=2)


def load_marking_groups():
    _ensure_default_groups()
    with open(GROUPS_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_group_names():
    return list(load_marking_groups().keys())


def get_mask_by_group(group_name: str) -> str:
    groups = load_marking_groups()
    if group_name not in groups:
        raise ValueError(f"Группа '{group_name}' не найдена в справочнике")
    return groups[group_name]


def init_db():
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    with sqlite3.connect(DATABASE_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                marking_group TEXT NOT NULL,
                short_ean TEXT NOT NULL,
                saved_code TEXT NOT NULL,
                comment TEXT
            )
        """)
        conn.commit()
