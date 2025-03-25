import os
import sqlite3
from pathlib import Path

from src.data_source.queries import *


def is_database_available(database_path) -> bool:
    db_file = Path(database_path)
    return db_file.is_file() and db_file.suffix == ".db"


# TODO: optimize queries if possible
def extract_vulnerability_fixes(database_path, language, patterns_path):
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
    output = cursor.fetchall()  # .fetchmany(5)
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

        # kettesevel groupolni oket
        # if nem true-false par, kidob
        # if nem ugyanaz a method, kidob
        # ezt hogy kene nezni? - fejlec, vagy csak nev? (ha fejlec mas, akkor mashol is van change,
        # de a valtozonev lehet mas) - talan eleg a nev
        left: MethodChange
        right: MethodChange
        i = 0
        for row in cursor.fetchall():
            print(row)
            if i % 2 == 0:
                left = MethodChange(row[0], row[1], row[2], row[3])
            if i % 2 == 1:
                right = MethodChange(row[0], row[1], row[2], row[3])
                save_file_from_db_objects(patterns_path, left, right, row[4])
            i += 1

    connection.commit()
    connection.close()


class MethodChange:
    def __init__(self, name, before_change, file_change_id, code):
        self.name = name
        self.is_before_change = before_change
        self.file_change_id = file_change_id
        self.code = code


def save_file_from_db_objects(patterns_path, left, right, file_path):
    if left.is_before_change == right.is_before_change:
        return
    if not left.is_before_change:
        temp = left.copy()
        left = right.copy()
        right = temp.copy()
    file_path = file_path.replace("/", "\\")
    file_name = file_path.split("\\")[-1]

    # TODO: szures, hogy csak a valtozo kodresz legyen benne
    # import resz elmeletileg nem kell, mivel kicsereli a valtozokat, konyvtarakat a comby
    # legalabbis a talalt peldak ezt mutatjak
    write_code_to_file(patterns_path, file_path, file_name, "l_", left)
    write_code_to_file(patterns_path, file_path, file_name, "r_", right)


def write_code_to_file(patterns_path, file_path, file_name, file_name_prefix, method_change):
    new_file_path = file_path.replace(file_name, file_name_prefix + file_name)
    full_path = os.path.join(patterns_path, new_file_path)
    if not os.path.exists(full_path):
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w') as f:
        f.write(method_change.code)
