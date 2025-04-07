import os
from pathlib import Path

from src.config import configuration as cf

# TODO: workflow:
# 0. set config values
ROOT_DIR = Path.cwd().parent.parent
EVAL_ROOT_DIR = os.path.join(ROOT_DIR.parent, "_infer_data\\eval")

cf.PROJECT_REPO = os.path.join(EVAL_ROOT_DIR, "project_repo")
cf.TYPE_REPO = os.path.join(EVAL_ROOT_DIR, "type_repo")
cf.PATTERNS_PATH = os.path.join(EVAL_ROOT_DIR, "patterns")
cf.RULES_PATH = os.path.join(EVAL_ROOT_DIR, "rules")
cf.FILES_PATH = os.path.join(EVAL_ROOT_DIR, "files.txt")

# 1. collect all fixes from db to a temp dir
# 2. split the files (l and r sides should always stay connected!!!) 10-90 using scikit-learn
# 3. copy the 10 part to a dummy project_repo
# 4. copy the 90 to patterns_path
# 5. infer the 90
# 6. type_infer for project_repo
# 7. collect files into files.txt
# 8. run pyevolve.transform
# 9. evaluate results (how??? - bleu score?)
# 10. save results into a file
# 11. start over from step 2
