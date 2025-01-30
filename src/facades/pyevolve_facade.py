import subprocess


# TODO (IMPORTANT): replace jar with the actual one
# Remove this after testing
def run_pyevolve():
    result = subprocess.run(["java", "-jar", "../jar/pycraft-1.0-SNAPSHOT.jar", "-h"],
                            shell=True,
                            capture_output=True,
                            text=True)
    return result


# TODO: filter needed results
def run_pyevolve_infer(patterns, rules):
    result = subprocess.run(["java", "-jar", "../jar/pycraft-1.0-SNAPSHOT.jar", "infer",
                             "-p", patterns, "-r", rules],
                            shell=True,
                            capture_output=True,
                            text=True)
    return result


# TODO: filter needed results
def run_pyevolve_transform(repositories, types, files, patterns):
    result = subprocess.run(["java", "-jar", "../jar/pycraft-1.0-SNAPSHOT.jar", "transform",
                             "-r", repositories,
                             "-t", types,
                             "-f", files,
                             "-p", patterns],
                            shell=True,
                            capture_output=True,
                            text=True)
    return result
