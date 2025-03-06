from src.facades import pyevolve_facade

if __name__ == '__main__':
    # TODO: check whether the rules are inferred (check if patterns path is empty???)
    # if not, then:
    # TODO: move these 3 steps to infer_cve.py
    # TODO: 1. check for database
    # (if not present, then just exit with an error (for now) - loading the db will be an extension point)
    # TODO: 2. extract data from db
    # TODO: 3. run run_pyevolve_infer
    # else: just continue

    # TODO: if all is good, run_pyevolve_transform on the given repo
    print("res: ", pyevolve_facade.run_pyevolve_infer("/patterns", "/rules"))
    print("res: ", pyevolve_facade.run_pyevolve_transform("/repos", "/types", "/files", "/pattsies"))
