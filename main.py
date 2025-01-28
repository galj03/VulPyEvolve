import subprocess


# TODO: args
# TODO (IMPORTANT): replace jar with the actual one
def run_pyevolve():
    result = subprocess.run(["java", "-jar", "jar/pycraft-1.0-SNAPSHOT.jar", "-h"], shell=True, capture_output=True, text=True)
    return result


if __name__ == '__main__':
    # os.chdir(sys.argv[1])
    print("res: ", run_pyevolve())
