from src.data_source import database
from src.config import configuration as cf
from src.facades import pyevolve_facade


def infer_cve():
    # 1. check for database
    if not database.is_database_available(cf.DATABASE_PATH):
        print('Database does not exist')
        # loading the db will be an extension point
        exit(1)

    # 2. extract data from db
    database.extract_vulnerability_fixes(cf.DATABASE_PATH, cf.LANGUAGE, cf.PATTERNS_PATH)

    # 3. run run_pyevolve_infer
    # pyevolve_facade.run_pyevolve_infer(cf.PATTERNS_PATH, cf.RULES_PATH)
