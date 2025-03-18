from src.facades import pyevolve_facade
from src.config import configuration as cf
from src.infer import infer_cve
from src.utils import utils

# TODO: consider making it a cli app (possible extension point?)

if __name__ == '__main__':
    if utils.is_directory_empty(cf.PATTERNS_PATH):
        infer_cve.infer_cve()

    # if all is good:
    extension = utils.match_extension_to_language(cf.LANGUAGE)
    utils.collect_file_names_to_text_file(cf.PROJECT_REPO, cf.FILES_PATH, extension)
    # TODO: run_pyevolve_transform on the given repo
    print("Db path: ", cf.DATABASE_PATH)
    print("res: ", pyevolve_facade.run_pyevolve())
    # print("res: ", pyevolve_facade.run_pyevolve_transform(cf.PROJECT_REPO, cf.TYPE_REPO, cf.FILES_PATH, cf.PATTERNS_PATH))
    # TODO: patterns or rules for last param?
