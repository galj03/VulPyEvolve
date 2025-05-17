import io
import os
import shutil
import sys
import tokenize
from glob import glob
from pathlib import Path

import chardet
import nltk

from src.config import configuration as cf
from src.facades import pyevolve_facade
from src.infer import type_infer as ti
from src.infer.infer_cve import extract_fixes, infer_cve
from sklearn.model_selection import train_test_split

from src.utils import utils


def main(
        is_extract_from_db,
        is_transform_change_only,
        run_count=1,
        is_evaluate_on_self=False,
        is_run_type_infer_on_all=False,
        is_keep_type_info=True):
    # 0. set config values
    root_dir = Path.cwd().parent.parent
    if len(sys.argv) > 1:
        root_dir = sys.argv[1]
    eval_root_dir = os.path.join(root_dir, "_infer_data", "eval")
    patterns_dir = os.path.join(eval_root_dir, "patterns")
    temp_str = "temp"
    temp_dir = os.path.join(eval_root_dir, temp_str)
    temp_method_str = "temp_method"
    temp_method_dir = os.path.join(eval_root_dir, temp_method_str)
    compare_dir = os.path.join(eval_root_dir, "compare")

    cf.PROJECT_REPO = os.path.join(eval_root_dir, "project_repo") + os.path.sep
    cf.TYPE_REPO = os.path.join(eval_root_dir, "type_repo")
    cf.PATTERNS_PATH = temp_dir
    cf.RULES_PATH = os.path.join(eval_root_dir, "rules")
    cf.FILES_PATH = os.path.join(eval_root_dir, "files.txt")

    create_directory_if_not_exists(os.path.join(cf.PROJECT_REPO, "pythonInfer", "evaluation_set"))
    create_directory_if_not_exists(os.path.join(cf.TYPE_REPO, "pythonInfer", "evaluation_set"))
    create_directory_if_not_exists(patterns_dir)
    create_directory_if_not_exists(temp_dir)
    create_directory_if_not_exists(temp_method_dir)
    create_directory_if_not_exists(compare_dir)
    create_directory_if_not_exists(cf.RULES_PATH)

    # 1. collect all fixes from db to a temp dir
    if is_extract_from_db:
        if is_transform_change_only:
            extract_fixes(temp_dir)
        else:
            extract_fixes(temp_method_dir)

    # 2. type infer on all data, so it will only be required once
    if is_run_type_infer_on_all:
        ti.TYPE_INFER_PYTYPE_FILES = os.path.join(eval_root_dir, "pytype_files")
        ti.TYPE_INFER_PYTYPE_SAVE = cf.TYPE_REPO
        ti.TYPE_INFER_PROJECT_PATH = eval_root_dir
        if is_transform_change_only:
            ti.TYPE_INFER_PROJECT_NAME = temp_str
        else:
            ti.TYPE_INFER_PROJECT_NAME = temp_method_str

        ti.main1()

        # make a backup, then copy to the actual folder
        if is_transform_change_only:
            shutil.copytree(os.path.join(cf.TYPE_REPO, temp_str),
                            os.path.join(cf.TYPE_REPO, "pythonInfer", "evaluation_set"))
        else:
            shutil.copytree(os.path.join(cf.TYPE_REPO, temp_method_str),
                            os.path.join(cf.TYPE_REPO, "pythonInfer", "evaluation_set"))

    is_not_first_run = False

    count = 0
    while count < run_count:
        if is_not_first_run:
            cf.PATTERNS_PATH = temp_dir

            create_directory_if_not_exists(patterns_dir)
            create_directory_if_not_exists(compare_dir)
            create_directory_if_not_exists(cf.RULES_PATH)

        # 3. split the files (l and r sides should always stay connected!!!) 10-90 using scikit-learn
        files = get_files_from_dir(temp_dir)
        if not is_transform_change_only:
            files = files.intersection(get_files_from_dir(temp_method_dir))

        print(f"Number of fixes retrieved: {len(files)}")
        files_train, files_test = train_test_split(list(files), test_size=0.1)

        # 4. copy the 10 part to a dummy project_repo
        if is_transform_change_only:
            copy_l_files_to_dir(files_test, temp_dir, os.path.join(cf.PROJECT_REPO, "pythonInfer", "evaluation_set"))
            copy_r_files_to_dir(files_test, temp_dir, compare_dir)
        else:
            copy_l_files_to_dir(files_test, temp_method_dir,
                                os.path.join(cf.PROJECT_REPO, "pythonInfer", "evaluation_set"))
            copy_r_files_to_dir(files_test, temp_method_dir, compare_dir)

        # 5. copy the 90 to patterns_path
        if is_evaluate_on_self:
            # NOTE: in this version, all files are inferred
            copy_files_to_dir(files, temp_dir, patterns_dir)
        else:
            copy_files_to_dir(files_train, temp_dir, patterns_dir)

        # 6. infer the 90
        cf.PATTERNS_PATH = patterns_dir
        infer_cve(root_dir)

        # 7. type infer on current eval files
        if not is_run_type_infer_on_all:
            ti.TYPE_INFER_PYTYPE_FILES = os.path.join(eval_root_dir, "pytype_files")
            ti.TYPE_INFER_PYTYPE_SAVE = cf.TYPE_REPO
            ti.TYPE_INFER_PROJECT_PATH = cf.PROJECT_REPO
            ti.TYPE_INFER_PROJECT_NAME = os.path.join("pythonInfer", "evaluation_set")
            ti.main1()

        # 8. collect files into files.txt
        extension = utils.match_extension_to_language(cf.LANGUAGE)
        utils.collect_file_names_to_text_file(
            cf.PROJECT_REPO, cf.FILES_PATH, extension)

        # 9. run pyevolve.transform
        res = pyevolve_facade.run_pyevolve_transform(
            root_dir, cf.PROJECT_REPO, cf.TYPE_REPO, cf.FILES_PATH, cf.RULES_PATH)
        print("res: ", res)
        print("Return code: ", res.returncode)

        # 10. filter out invalid files
        filtered_count, filtered = filter_files(
            os.path.join(cf.PROJECT_REPO, "pythonInfer", "evaluation_set"), files_test, "l_")
        print(f"Filered files count: {filtered_count}")
        with open(f"{eval_root_dir}{os.path.sep}filtered_files_count.txt", "a") as f:
            f.write(f"{filtered_count}\n")

        # 11. evaluate results (bleu score)
        transformed_files_tokens = collect_tokens_from_files_in_dir(
            os.path.join(cf.PROJECT_REPO, "pythonInfer", "evaluation_set"), filtered, "l_")
        original_files_tokens = collect_reference_tokens_from_files_in_dir(compare_dir, filtered, "r_")

        score = nltk.translate.bleu_score.corpus_bleu(original_files_tokens, transformed_files_tokens)
        print(f"Bleu: {score}")

        # 12. save results into a file
        with open(f"{eval_root_dir}{os.path.sep}pre_transform_method_scores.txt", "a") as f:
            f.write(f"{score}\n")

        # 13. start over from step 3 (empty rules and patterns dirs)
        shutil.rmtree(cf.RULES_PATH)
        shutil.rmtree(cf.PATTERNS_PATH)
        shutil.rmtree(compare_dir)
        shutil.rmtree(os.path.join(cf.PROJECT_REPO, "pythonInfer", "evaluation_set"))
        create_directory_if_not_exists(os.path.join(cf.PROJECT_REPO, "pythonInfer", "evaluation_set"))

        if not is_run_type_infer_on_all:
            shutil.rmtree(os.path.join(cf.TYPE_REPO, "pythonInfer", "evaluation_set"))
            create_directory_if_not_exists(os.path.join(cf.TYPE_REPO, "pythonInfer", "evaluation_set"))

        is_not_first_run = True
        count += 1

    if not is_keep_type_info:
        shutil.rmtree(os.path.join(cf.TYPE_REPO, "pythonInfer", "evaluation_set"))
    create_directory_if_not_exists(os.path.join(cf.TYPE_REPO, "pythonInfer", "evaluation_set"))


def create_directory_if_not_exists(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path, exist_ok=True)


def print_dir_files(base_dir, extension):
    for path in glob(f'{base_dir}/**/*{extension}', recursive=True):
        file_str = read_file(path)
        print(f"{path}: ", file_str)


def filter_files(directory, files, prefix):
    filtered_count = 0
    new_files = []
    for file_name in files:
        r_file_name = prefix + file_name
        file_path = os.path.join(directory, r_file_name)
        file_str: str
        try:
            file_str = read_file(file_path)
            tokens = tokenize.generate_tokens(io.StringIO(file_str).readline)
            _ = [token.string for token in tokens]
            new_files.append(file_name)
        except Exception:
            os.remove(file_path)
            filtered_count += 1
            # print(f"Filtered: {file_str}\n")
    return filtered_count, new_files


def get_files_from_dir(dir_path):
    files_dict = dict()
    for path in glob(f'{dir_path}/*', recursive=True):
        path = path.replace(f'{dir_path}{os.path.sep}', '')
        # path = path.replace(f'{dir_path}\\', '')
        if path.startswith('l_'):
            path = path.replace('l_', '')
        if path.startswith('r_'):
            path = path.replace('r_', '')
        if files_dict.__contains__(path):
            files_dict[path] = 2
        else:
            files_dict[path] = 1
    file_set = set()
    for path in files_dict.keys():
        if files_dict[path] == 2:
            file_set.add(path)
    return file_set


def copy_files_to_dir(files_test, source_dir, destination_dir):
    copy_l_files_to_dir(files_test, source_dir, destination_dir)
    copy_r_files_to_dir(files_test, source_dir, destination_dir)


def copy_l_files_to_dir(files_test, source_dir, destination_dir):
    for file_name in files_test:
        l_file_name = 'l_' + file_name
        curr_file_path = os.path.join(source_dir, l_file_name)
        dest_file_path = os.path.join(destination_dir, l_file_name)
        shutil.copy2(str(curr_file_path), str(dest_file_path))


def copy_r_files_to_dir(files_test, source_dir, destination_dir):
    for file_name in files_test:
        r_file_name = 'r_' + file_name
        curr_file_path = os.path.join(source_dir, r_file_name)
        dest_file_path = os.path.join(destination_dir, r_file_name)
        shutil.copy2(str(curr_file_path), str(dest_file_path))


def read_file(file_path):
    with open(file_path, 'rb') as f:
        encoding_dict = chardet.detect(f.read())
    with open(file_path, 'r', encoding=encoding_dict["encoding"]) as f:
        file_str = f.read()
    return file_str


def collect_reference_tokens_from_files_in_dir(directory, files, prefix):
    token_list = list()
    for file_name in files:
        r_file_name = prefix + file_name
        file_path = os.path.join(directory, r_file_name)
        file_str = read_file(file_path)
        tokens = tokenize.generate_tokens(io.StringIO(file_str).readline)
        token_list.append([[token.string for token in tokens]])
    return token_list


def collect_tokens_from_files_in_dir(directory, files, prefix):
    token_list = list()
    for file_name in files:
        r_file_name = prefix + file_name
        file_path = os.path.join(directory, r_file_name)
        file_str = read_file(file_path)
        tokens = tokenize.generate_tokens(io.StringIO(file_str).readline)
        token_list.append([token.string for token in tokens])
    return token_list


# IMPORTANT: if is_transform_change_only changes, then:
# 1. replace temp with correct folder
# 2. replace type repo with correct folder
if __name__ == '__main__':
    # main(True, True) - this is the default - executes 1 run
    # main(False, False, 200)
    main(False, True, 1)
