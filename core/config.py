import os
import sys


APP_VERSION = "1.1.2"


def get_app_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))


APP_DIR = get_app_dir()
DB_DIR = os.path.join(APP_DIR, "db")
DATABASE_PATH = os.path.join(DB_DIR, "database.db")
GROUPS_JSON_PATH = os.path.join(DB_DIR, "marking_groups.json")

os.makedirs(DB_DIR, exist_ok=True)