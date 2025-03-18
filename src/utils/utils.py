import os
from pathlib import Path


def is_directory_empty(path) -> bool:
    if os.path.exists(path) and not os.path.isfile(path):
        return not os.listdir(path)
    else:
        return False


def collect_file_names_to_text_file(base_directory: str, text_file: str, extension: str):
    with open(text_file, "w") as text_file:
        for path in Path(base_directory).rglob(f"*{extension}"):
            text_file.write(path.name)


def match_extension_to_language(language: str) -> str:
    match language:
        case "Python":
            return ".py"
        case _:
            return ".py"
