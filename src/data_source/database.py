from pathlib import Path


def is_database_available(database_path) -> bool:
    db_file = Path(database_path)
    return db_file.is_file() and db_file.suffix == ".db"


def extract_vulnerability_fixes(database_path, language, patterns_path):
    return None
