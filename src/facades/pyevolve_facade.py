import subprocess


def run_pyevolve(root_dir):
    result = subprocess.run(f"java -jar {root_dir}/jar/pycraft-1.0-SNAPSHOT.jar -h",
                            shell=True,
                            capture_output=True,
                            text=True)
    return result


def run_pyevolve_infer(root_dir, patterns, rules):
    result = subprocess.run(f"java -jar {root_dir}/jar/pycraft-1.0-SNAPSHOT.jar infer -p {patterns} -r {rules}",
                            shell=True,
                            capture_output=True,
                            text=True)
    return result


def run_pyevolve_transform(root_dir, repositories, types, files, patterns):
    result = subprocess.run((f"java -jar {root_dir}/jar/pycraft-1.0-SNAPSHOT.jar transform"
                             + f" -r {repositories} -t {types} -f {files} -p {patterns}"),
                            shell=True,
                            capture_output=True,
                            text=True)
    return result
