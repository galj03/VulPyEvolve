import sqlite3

from src.data_source import database
from src.config import configuration as cf
from src.facades import pyevolve_facade


def extract_and_infer_cve(root_dir, methods_path=None):
    extract_fixes(methods_path)
    infer_cve(root_dir)


def extract_fixes(methods_path=None):
    # 1. check for database
    if not database.is_database_available(cf.DATABASE_PATH):
        print('Database does not exist')
        # loading the db will be an extension point
        exit(1)

    # 2. extract data from db
    try:
        database.extract_vulnerability_fixes(cf.DATABASE_PATH, cf.LANGUAGE, cf.PATTERNS_PATH, methods_path)
    except sqlite3.DatabaseError as e:
        print(f"A database error occurred in {cf.DATABASE_PATH}. Error: {e}")
        exit(1)
    except sqlite3.Error as e:
        print(f"Unexpected error with db '{cf.DATABASE_PATH}'.\nCheck if db really is a CVEFixes database.\nError: {e}")


def infer_cve(root_dir):
    # 3. run run_pyevolve_infer
    res = pyevolve_facade.run_pyevolve_infer(root_dir, cf.PATTERNS_PATH, cf.RULES_PATH)
    # print(res)
