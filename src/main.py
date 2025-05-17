import os
import sys
from pathlib import Path

from src.facades import pyevolve_facade
from src.config import configuration as cf
from src.infer import type_infer as ti
from src.infer import infer_cve
from src.utils import utils

IS_FORCE_INFER = True

# making it a cli app would be an extension point
if __name__ == '__main__':
    root_dir = Path.cwd().parent
    if len(sys.argv) > 1:
        root_dir = sys.argv[1]
    if len(sys.argv) > 2:
        IS_FORCE_INFER = sys.argv[2]

    if IS_FORCE_INFER or utils.is_directory_empty(cf.PATTERNS_PATH):
        infer_cve.extract_and_infer_cve(root_dir)

    extension = utils.match_extension_to_language(cf.LANGUAGE)
    utils.collect_file_names_to_text_file(cf.PROJECT_REPO, cf.FILES_PATH, extension)

    ti.TYPE_INFER_PYTYPE_FILES = os.path.join(cf.TYPE_REPO, "pytype_files")
    ti.TYPE_INFER_PYTYPE_SAVE = cf.TYPE_REPO
    ti.TYPE_INFER_PROJECT_PATH = cf.PROJECT_REPO
    ti.TYPE_INFER_PROJECT_NAME = cf.PROJECT_NAME
    ti.main1()

    print("res: ",
          pyevolve_facade.run_pyevolve_transform(root_dir, cf.PROJECT_REPO, cf.TYPE_REPO, cf.FILES_PATH, cf.RULES_PATH))
