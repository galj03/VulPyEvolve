import sqlite3
from pathlib import Path

from src.data_source.queries import *


def is_database_available(database_path) -> bool:
    db_file = Path(database_path)
    return db_file.is_file() and db_file.suffix == ".db"


# TODO: optimize queries if possible
def extract_vulnerability_fixes(database_path, language, patterns_path):
    # TODO: move db check here?
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()
    # statement = '''select count(*) from file_change where programming_language=?'''

    # gets all cve fixes with at least two different commits
    statement = f'''select cve_id, count(file_change_id) as fix_count
        from fixes join commits on fixes.hash=commits.hash and fixes.repo_url=commits.repo_url
        join file_change on commits.hash=file_change.hash
        where file_change_id in
        ({GET_FILE_CHANGE_ID_WITH_TWO_METHOD_CHANGES})
        group by cve_id having count(fixes.hash)>1'''

    cves = []
    cursor.execute(statement, (language,))
    output = cursor.fetchall()# .fetchmany(5)
    for row in output:
        # print(row[0])
        cves.append(row[0])
        # row['cve_id']
    print(len(cves))

    for cve in cves:
        # query = GET_FILE_CHANGE_ID_FROM_CVE_ID
        # cursor.execute(query, (cve,))
        # file_changes = []
        # for row in cursor.fetchall():
        #     file_changes.append(row[0])
        query = GET_METHOD_INFO_FROM_FILE_CHANGES_FOR_GIVEN_CVE
        cursor.execute(query, (cve,))

        print(f"\n{cve}")

        # TODO: kettesevel groupolni oket
        # if nem true-false par, kidob
        # if nem ugyanaz a method, kidob
        # ezt hogy kene nezni? - fejlec, vagy csak nev? (ha fejlec mas, akkor mashol is van change,
        # de a valtozonev lehet mas) - talan eleg a nev
        i = 0
        for row in cursor.fetchall():
            print(row)
            if i%2 == 1:
                pass
            i += 1
        # TODO: extract file changes

    connection.commit()
    connection.close()
