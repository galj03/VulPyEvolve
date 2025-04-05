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

    # gets all cve fixes with at least two different commits
    # TODO: remove having statement
    statement = f'''select cve_id, count(file_change_id) as fix_count
        from fixes join commits on fixes.hash=commits.hash and fixes.repo_url=commits.repo_url
        join file_change on commits.hash=file_change.hash
        where file_change_id in
        ({GET_FILE_CHANGE_ID_WITH_TWO_METHOD_CHANGES})
        group by cve_id having count(fixes.hash)>1'''

    cves = []
    cursor.execute(statement, (language,))
    output = cursor.fetchall()
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
                try:
                    save_file_from_db_objects(patterns_path, left, right, row[4])
                except Exception as e:
                    print(e)
            i += 1

        # TODO: reconsider this, may not be relevant!!!
        # with open(patterns_path + 'repos.txt', 'w') as f:
        #     for repo in repos:
        #         f.write(repo + '\n')  # TODO: extract repos for each cve to enable cross-validation

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
    file_path = file_path.replace("/", "\\")  # TODO: technical debt - use multiplatform solution
    file_name = file_path.split("\\")[-1]

    a = left.code  # 'testing this is working \n testing this is working 1 \n'
    b = right.code  # 'testing this is working \n testing this is working 1 \n testing this is working 2'

    first_diff_index = next((i for i in range(min(len(a), len(b))) if a[i] != b[i]), None)
    last_diff_index = next((i for i in range(max(len(a), len(b))) if a[-i] != b[-i]), None)
    last_diff_index_a = len(a) - last_diff_index + 1
    last_diff_index_b = len(b) - last_diff_index + 1

    # TODO: consider this: instead of full rows, check if it is only one row (might be an if clause)
    diff_a = a[first_diff_index:last_diff_index_a]
    diff_a, first_diff_index_a, last_diff_index_a = expand_to_include_full_function(a, diff_a, first_diff_index, last_diff_index_a)
    diff_a, first_diff_index_a, last_diff_index_a = include_full_rows(a, diff_a, first_diff_index_a, last_diff_index_a)
    diff_a = trim_unnecessary_indentations(diff_a)

    diff_b = b[first_diff_index:last_diff_index_b]
    diff_b, first_diff_index_b, last_diff_index_b = expand_to_include_full_function(b, diff_b, first_diff_index, last_diff_index_b)
    diff_b, first_diff_index_b, last_diff_index_b = include_full_rows(b, diff_b, first_diff_index_b, last_diff_index_b)
    diff_b = trim_unnecessary_indentations(diff_b)

    # TODO: if has syntax error, then throw it away
    # TODO: file path: "{patterns_path}/{file_name}-{cve}.py"
    # print(differences.edit_script())
    print("-----------------")
    print(diff_a)
    # print(differences.source_text)
    print("-----------------")
    # print(differences.target_text)
    print(diff_b)
    print("-----------------")

    # write_code_to_file(patterns_path, file_path, file_name, "old_l_", left.code)
    # write_code_to_file(patterns_path, file_path, file_name, "old_r_", right.code)
    # write_code_to_file(patterns_path, file_path, file_name, "l_", diff_a)
    # write_code_to_file(patterns_path, file_path, file_name, "r_", diff_b)
    print(left.name)


def expand_to_include_full_function(a, diff_a, first_diff_index, last_diff_index):
    if (first_diff_index > 0 and
            (a[first_diff_index - 1] == '.' or a[first_diff_index - 1].isalnum() or a[first_diff_index - 1] == '_')):
        first_diff_index -= 1
        while (first_diff_index > 0
               and (a[first_diff_index] == '.' or a[first_diff_index].isalnum() or a[first_diff_index] == '_')):
            first_diff_index -= 1
        diff_a = a[first_diff_index:last_diff_index]

    if a[first_diff_index] == '.' and first_diff_index > 0:
        while (first_diff_index > 0
               and (a[first_diff_index] == '.' or a[first_diff_index].isalnum() or a[first_diff_index] == '_')):
            first_diff_index -= 1
        diff_a = a[first_diff_index:last_diff_index]

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
                j = i - 1  # changed
                while counter < 0 <= j:
                    if a[j] == '(':
                        counter += 1
                    if a[j] == ')':
                        counter -= 1
                    j -= 1
                diff_a = a[j:last_diff_index]
                first_diff_index = j
    if counter > 0:
        j = last_diff_index
        while counter > 0 and j < len(a):
            if a[j] == '(':
                counter += 1
            if a[j] == ')':
                counter -= 1
            j += 1
        diff_a = diff_a + a[last_diff_index:j]
        last_diff_index = j
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
                    return diff_a, first_diff_index, last_diff_index
                break
        i -= 1
    is_name_found = False
    while i >= 0:
        match a[i]:
            case ' ' | '\n':
                if is_name_found:
                    diff_a = a[i:first_diff_index] + diff_a
                    first_diff_index = i
                    break
            case '-' | '+' | '*' | '/' | '%' | '&' | '|' | '^' | '>' | '<' | ':':  # assignment operators
                pass
            case _:
                is_name_found = True
        i -= 1

    return diff_a, first_diff_index, last_diff_index


def trim_unnecessary_indentations(diff_a):
    if not (diff_a[0] == ' ' or diff_a[0] == '\t'):
        return diff_a.strip()
    # expand to include the whole line - another function will handle this
    i = 0
    for j in range(len(diff_a)):
        if not (diff_a[j] == ' ' or diff_a[j] == '\t'):
            break
        i += 1
    start_indentation = diff_a[:i]
    diff_a = diff_a.replace(f"\n{start_indentation}", "\n")
    return diff_a.strip()


def include_full_rows(a, diff_a, first_diff_index, last_diff_index):
    original_first_index = first_diff_index
    while first_diff_index > 0 and a[first_diff_index - 1] != '\n':
        first_diff_index -= 1
    diff_a = a[first_diff_index:original_first_index] + diff_a

    # original_last_index = last_diff_index
    # while last_diff_index < len(a) and a[last_diff_index] != '\n':
    #     last_diff_index += 1
    # diff_a = diff_a + a[original_last_index:last_diff_index]
    return diff_a, first_diff_index, last_diff_index


def write_code_to_file(patterns_path, file_path, file_name, file_name_prefix, content):
    new_file_path = file_path.replace(file_name, file_name_prefix + file_name)
    full_path = os.path.join(patterns_path, new_file_path)
    if not os.path.exists(full_path):
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w') as f:
        f.write(content)
