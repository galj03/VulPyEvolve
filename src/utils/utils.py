import os
from glob import glob


def is_directory_empty(path) -> bool:
    if os.path.exists(path) and not os.path.isfile(path):
        return not os.listdir(path)
    else:
        return False


def collect_file_names_to_text_file(base_directory: str, text_file: str, extension: str):
    with open(text_file, "w") as text_file:
        for path in glob(f'{base_directory}/**/*{extension}', recursive=True):
            path = path.replace("\\", "/").replace(base_directory, "")
            text_file.write(f"{path}\n")


def match_extension_to_language(language: str) -> str:
    match language:
        case "Python":
            return ".py"
        case _:
            return ".py"
