from src.facades import pyevolve_facade

if __name__ == '__main__':
    # os.chdir(sys.argv[1])
    print("res: ", pyevolve_facade.run_pyevolve_infer("/patterns", "/rules"))
    print("res: ", pyevolve_facade.run_pyevolve_transform("/repos", "/types", "/files", "/pattsies"))
