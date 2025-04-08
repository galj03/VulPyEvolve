import subprocess


def run_pyevolve(root_dir):
    result = subprocess.run(["java", "-jar", f"{root_dir}/jar/pycraft-1.0-SNAPSHOT.jar", "-h"],
                            shell=True,
                            capture_output=True,
                            text=True)
    return result


def run_pyevolve_infer(root_dir, patterns, rules):
    result = subprocess.run(["java", "-jar", f"{root_dir}/jar/pycraft-1.0-SNAPSHOT.jar", "infer",
                             "-p", patterns, "-r", rules],
                            shell=True,
                            capture_output=True,
                            text=True)
    return result


def run_pyevolve_transform(root_dir, repositories, types, files, patterns):
    result = subprocess.run(["java", "-jar", f"{root_dir}/jar/pycraft-1.0-SNAPSHOT.jar", "transform",
                             "-r", repositories,
                             "-t", types,
                             "-f", files,
                             "-p", patterns],
                            shell=True,
                            capture_output=True,
                            text=True)
    return result
