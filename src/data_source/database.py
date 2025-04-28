import ast
import os
import sqlite3
from pathlib import Path

from src.data_source.queries import *
from src.utils.code_parser import *


def is_database_available(database_path) -> bool:
    db_file = Path(database_path)
    return db_file.is_file() and db_file.suffix == ".db"


# TODO: technical debt: optimize queries if possible
def extract_vulnerability_fixes(database_path, language, patterns_path, methods_path):
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()

    statement = f'''select cve_id, count(file_change_id) as fix_count
        from fixes join commits on fixes.hash=commits.hash and fixes.repo_url=commits.repo_url
        join file_change on commits.hash=file_change.hash
        where file_change_id in
        ({GET_FILE_CHANGE_ID_WITH_TWO_METHOD_CHANGES})
        group by cve_id'''

    cves = []
    cursor.execute(statement, (language,))
    output = cursor.fetchall()
    for row in output:
        cves.append(row[0])
    print(len(cves))

    for cve in cves:
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
                try:
                    save_file_from_db_objects(patterns_path, methods_path, left, right, row[4], cve)
                except Exception as e:
                    print(e)
            i += 1

    connection.commit()
    connection.close()


class MethodChange:
    def __init__(self, name, before_change, file_change_id, code):
        self.name = name
        self.is_before_change = before_change
        self.file_change_id = file_change_id
        self.code = code


def save_file_from_db_objects(patterns_path, methods_path, left, right, file_path, cve):
    if left.is_before_change == right.is_before_change \
            or left.name != right.name:
        return
    if not left.is_before_change:
        temp = left.copy()
        left = right.copy()
        right = temp.copy()
    file_path = file_path.replace("/", os.path.sep)
    file_name = file_path.split(os.path.sep)[-1]

    a = left.code
    b = right.code

    first_diff_index = next((i for i in range(min(len(a), len(b))) if a[i] != b[i]), None)
    last_diff_index = next((i for i in range(max(len(a), len(b))) if a[-i] != b[-i]), None)
    last_diff_index_a = len(a) - last_diff_index + 1
    last_diff_index_b = len(b) - last_diff_index + 1

    # TODO: technical debt: consider this: instead of full rows, check if it is only one row (might be an if clause)
    diff_a = a[first_diff_index:last_diff_index_a]
    diff_a, first_diff_index_a, last_diff_index_a = expand_to_include_full_function(a, diff_a, first_diff_index,
                                                                                    last_diff_index_a)
    diff_a, first_diff_index_a, last_diff_index_a = include_full_rows(a, diff_a, first_diff_index_a, last_diff_index_a)
    diff_a = trim_unnecessary_indentations(diff_a)

    diff_b = b[first_diff_index:last_diff_index_b]
    diff_b, first_diff_index_b, last_diff_index_b = expand_to_include_full_function(b, diff_b, first_diff_index,
                                                                                    last_diff_index_b)
    diff_b, first_diff_index_b, last_diff_index_b = include_full_rows(b, diff_b, first_diff_index_b, last_diff_index_b)
    diff_b = trim_unnecessary_indentations(diff_b)

    print("-----------------")
    print(diff_a)
    print("-----------------")
    print(diff_b)
    print("-----------------")

    try:
        _ = ast.parse(diff_a)
        _ = ast.parse(diff_b)
    except Exception:
        print("Error while parsing AST. File will not be saved.")
        return

    # write_code_to_file(patterns_path, file_path, file_name, "old_l_", left.code)
    # write_code_to_file(patterns_path, file_path, file_name, "old_r_", right.code)
    write_code_to_file(patterns_path, file_name, "l_", cve, diff_a)
    write_code_to_file(patterns_path, file_name, "r_", cve, diff_b)
    if methods_path is not None:
        write_code_to_file(methods_path, file_name, "l_", cve, trim_unnecessary_indentations(left.code))
        write_code_to_file(methods_path, file_name, "r_", cve, trim_unnecessary_indentations(right.code))
    print(left.name)


def write_code_to_file(patterns_path, file_name, file_name_prefix, cve, content):
    # new_file_path = file_path.replace(file_name, file_name_prefix + file_name)
    new_file_path = file_name_prefix + file_name
    new_file_path = new_file_path.replace(".py", f"-{cve}.py")  # TODO: technical debt: generalize extension
    full_path = os.path.join(patterns_path, new_file_path)
    if not os.path.exists(full_path):
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w') as f:
        f.write(content)
