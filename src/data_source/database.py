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

    repos = []
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
            repos.append(row[6])
            if i % 2 == 0:
                left = MethodChange(row[0], row[1], row[2], row[3])
            if i % 2 == 1:
                right = MethodChange(row[0], row[1], row[2], row[3])
                # save_file_from_db_objects(patterns_path, left, right, row[4])
            i += 1

        with open(patterns_path + 'repos.txt', 'w') as f:
            for repo in repos:
                f.write(repo + '\n')

    connection.commit()
    connection.close()


class MethodChange:
    def __init__(self, name, before_change, file_change_id, code):
        self.name = name
        self.is_before_change = before_change
        self.file_change_id = file_change_id
        self.code = code


def save_file_from_db_objects(patterns_path, left, right, file_path):
    if left.is_before_change == right.is_before_change \
            or left.name != right.name:
        return
    if not left.is_before_change:
        temp = left.copy()
        left = right.copy()
        right = temp.copy()
    file_path = file_path.replace("/", "\\")  # TODO: normal handling
    file_name = file_path.split("\\")[-1]

    # TODO: szures, hogy csak a valtozo kodresz legyen benne
    a = left.code  # 'testing this is working \n testing this is working 1 \n'
    b = right.code  # 'testing this is working \n testing this is working 1 \n testing this is working 2'

    first_diff_index = next((i for i in range(min(len(a), len(b))) if a[i] != b[i]), None)
    last_diff_index = next((i for i in range(max(len(a), len(b))) if a[-i] != b[-i]), None)
    last_diff_index_a = len(a) - last_diff_index + 1
    last_diff_index_b = len(b) - last_diff_index + 1

    diff_a = a[first_diff_index:last_diff_index_a]
    diff_b = b[first_diff_index:last_diff_index_b]

    # TODO: zarojelek!!! - megkeresni a veget/elejet, amelyik nincs benne, es odaig kiterjeszteni a diffet
    diff_a = expand_to_include_full_function(a, diff_a, first_diff_index, last_diff_index_a)
    diff_b = expand_to_include_full_function(b, diff_b, first_diff_index, last_diff_index_b)

    # import resz elmeletileg nem kell, mivel kicsereli a valtozokat, konyvtarakat a comby
    # legalabbis a talalt peldak ezt mutatjak
    # TODO: pass differing lines only (maybe indices as params?)
    write_code_to_file(patterns_path, file_path, file_name, "old_l_", left.code)
    write_code_to_file(patterns_path, file_path, file_name, "old_r_", right.code)
    write_code_to_file(patterns_path, file_path, file_name, "l_", diff_a)
    write_code_to_file(patterns_path, file_path, file_name, "r_", diff_b)
    print(left.name)


# TODO: this does not work for a lot of cases
# consider R-CPATMiner somehow
# or extract by hand for now...
def expand_to_include_full_function(a, diff_a, first_diff_index, last_diff_index):
    if a[last_diff_index] == '(':
        diff_a += a[last_diff_index]
        last_diff_index += 1
    counter = 0
    for i in range(first_diff_index, last_diff_index):
        if a[i] == '(':
            counter += 1
        if a[i] == ')':
            counter -= 1
            if counter < 0:
                j = i
                while counter < 0 <= j:
                    if a[j] == '(':
                        counter += 1
                    if a[j] == ')':
                        counter -= 1
                    j -= 1
                diff_a = a[j:last_diff_index]
    if counter > 0:
        j = last_diff_index
        while counter > 0 and j < len(a):
            if a[j] == '(':
                counter += 1
            if a[j] == ')':
                counter -= 1
            j += 1
        diff_a = diff_a + a[last_diff_index:j]
    i = first_diff_index - 1
    is_assignment = False
    while i >= 0:
        match a[i]:
            case ' ':
                pass
            case '=':
                is_assignment = True
            case _:
                if not is_assignment:
                    return diff_a
                break
        i -= 1
    is_name_found = False
    while i >= 0:
        match a[i]:
            case ' ' | '\n':
                if is_name_found:
                    diff_a = a[i:first_diff_index] + diff_a
                    break
            case '-' | '+' | '*' | '/' | '%' | '&' | '|' | '^' | '>' | '<' | ':':  # assignment operators
                pass
            case _:
                is_name_found = True
        i -= 1

    return diff_a


def write_code_to_file(patterns_path, file_path, file_name, file_name_prefix, content):
    new_file_path = file_path.replace(file_name, file_name_prefix + file_name)
    full_path = os.path.join(patterns_path, new_file_path)
    if not os.path.exists(full_path):
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w') as f:
        f.write(content)
