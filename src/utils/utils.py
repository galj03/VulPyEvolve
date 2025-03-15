import os


def is_directory_empty(path) -> bool:
    if os.path.exists(path) and not os.path.isfile(path):
        return not os.listdir(path)
    else:
        return False
