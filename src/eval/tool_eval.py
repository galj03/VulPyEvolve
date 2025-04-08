import os
import shutil
from glob import glob
from pathlib import Path

from src.config import configuration as cf
from src.infer.infer_cve import extract_fixes, infer_cve
from sklearn.model_selection import train_test_split

from src.utils import utils


def main():
    # 0. set config values
    root_dir = Path.cwd().parent.parent
    eval_root_dir = os.path.join(root_dir.parent, "_infer_data\\eval")
    patterns_dir = os.path.join(eval_root_dir, "patterns")
    temp_dir = os.path.join(eval_root_dir, "temp")

    cf.PROJECT_REPO = os.path.join(eval_root_dir, "project_repo")
    cf.TYPE_REPO = os.path.join(eval_root_dir, "type_repo")
    cf.PATTERNS_PATH = temp_dir
    cf.RULES_PATH = os.path.join(eval_root_dir, "rules")
    cf.FILES_PATH = os.path.join(eval_root_dir, "files.txt")

    create_directory_if_not_exists(patterns_dir)
    create_directory_if_not_exists(temp_dir)
    create_directory_if_not_exists(cf.RULES_PATH)

    # 1. collect all fixes from db to a temp dir
    # extract_fixes()

    # 2. split the files (l and r sides should always stay connected!!!) 10-90 using scikit-learn
    files = get_files_from_dir(temp_dir)
    print(len(files))
    # TODO: remove random state
    files_train, files_test = train_test_split(list(files), test_size=0.1, random_state=42)

    # 3. copy the 10 part to a dummy project_repo
    copy_files_to_dir(files_test, temp_dir, os.path.join(cf.PROJECT_REPO, "pythonInfer\\evaluation_set"))

    # 4. copy the 90 to patterns_path
    copy_files_to_dir(files_train, temp_dir, patterns_dir)

    # 5. infer the 90
    cf.PATTERNS_PATH = patterns_dir
    infer_cve(root_dir)

    # 6. type_infer for project_repo
    # TODO

    # 7. collect files into files.txt
    extension = utils.match_extension_to_language(cf.LANGUAGE)
    utils.collect_file_names_to_text_file(
        os.path.join(cf.PROJECT_REPO, "pythonInfer\\evaluation_set"), cf.FILES_PATH, extension)

    # 8. run pyevolve.transform
    # TODO: finish docker first
    # print("res: ",
    # pyevolve_facade.run_pyevolve_transform(
    # root_dir, cf.PROJECT_REPO, cf.TYPE_REPO, cf.FILES_PATH, cf.RULES_PATH))

    # 9. evaluate results (how??? - bleu score?)
    # 10. save results into a file
    # 11. start over from step 2 (empty rules and patterns dirs)
    # TODO: put these in a loop
    shutil.rmtree(cf.RULES_PATH)
    shutil.rmtree(cf.PATTERNS_PATH)
    shutil.rmtree(os.path.join(cf.PROJECT_REPO, "pythonInfer\\evaluation_set"))
    create_directory_if_not_exists(os.path.join(cf.PROJECT_REPO, "pythonInfer\\evaluation_set"))
    shutil.rmtree(os.path.join(cf.TYPE_REPO, "pythonInfer\\evaluation_set"))
    create_directory_if_not_exists(os.path.join(cf.TYPE_REPO, "pythonInfer\\evaluation_set"))


def create_directory_if_not_exists(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path, exist_ok=True)


def get_files_from_dir(dir_path):
    files_dict = dict()
    for path in glob(f'{dir_path}/*', recursive=True):
        path = path.replace(f'{dir_path}/', '')
        path = path.replace(f'{dir_path}\\', '')
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
    for file_name in files_test:
        l_file_name = 'l_' + file_name
        curr_file_path = os.path.join(source_dir, l_file_name)
        dest_file_path = os.path.join(destination_dir, l_file_name)
        shutil.copy2(str(curr_file_path), str(dest_file_path))

        r_file_name = 'r_' + file_name
        curr_file_path = os.path.join(source_dir, r_file_name)
        dest_file_path = os.path.join(destination_dir, r_file_name)
        shutil.copy2(str(curr_file_path), str(dest_file_path))


if __name__ == '__main__':
    main()
