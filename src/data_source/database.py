import sqlite3
from pathlib import Path


def is_database_available(database_path) -> bool:
    db_file = Path(database_path)
    return db_file.is_file() and db_file.suffix == ".db"


def extract_vulnerability_fixes(database_path, language, patterns_path):
    # TODO: move db check here?
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()
    statement = '''select count(*) from file_change where programming_language=?'''

    cursor.execute(statement, (language,))
    output = cursor.fetchmany(5)
    for row in output:
        print(row)

    connection.commit()
    connection.close()
