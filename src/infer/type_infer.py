from __future__ import print_function
import ast
import textwrap
from pytype import config
from pytype.tools.annotate_ast import annotate_ast
import sys
from git import Repo
import pytype

import subprocess

import json
import os

TYPE_INFER_PYTYPE_FILES = ''
TYPE_INFER_PYTYPE_SAVE = ''
TYPE_INFER_PROJECT_PATH = ''
TYPE_INFER_PROJECT_NAME = 'pythonInfer/PatternTest/'

# it was 3.7 originally
py_version_s = '3.12'
py_version = (3, 12)


def annotate(source, file_name, pytype_storage, type_repo):
    source = textwrap.dedent(source.lstrip('\n'))
    ast_factory = ast
    try:
        pytype_options = config.Options.create(python_version=py_version, nofail=True, protocols=True,
                                               imports_map=pytype_storage + '/imports/' + file_name)
        module = annotate_ast.annotate_source(source, ast_factory, pytype_options)
    except pytype.tools.annotate_ast.annotate_ast.PytypeError as e:
        print(e)
        return None
    except IndexError as e:
        print(e)
        return None
    except FileNotFoundError as e:
        print(e)
        return None
    except SyntaxError as e:
        print(e)
        return None
    except ValueError as e:
        return None

    return module


def get_annotations_dict(module, empty_line):
    return [{"lineNumber": _get_node_key(node)[0] + empty_line, "col_offset": _get_node_key(node)[1],
             "nodeName": _get_node_key(node)[2], "type": node.resolved_annotation}
            for node in ast.walk(module)
            if hasattr(node, 'resolved_type')]


def generate_pytype_folder(project_path, file_path, pytype_storage, type_repo):
    env = os.environ.copy()
    subprocess.run(['pytype', '--pythonpath=' + project_path, '--python-version=' + py_version_s, '--no-report-errors',
                    '--keep-going', '--protocols', '--output=' + pytype_storage, file_path], shell=False, env=env,
                   cwd=os.path.dirname(os.path.realpath(__file__)))


def _get_node_key(node):
    base = (node.lineno, node.col_offset)
    if isinstance(node, ast.Name):
        return base + (node.id,)
    elif isinstance(node, ast.Attribute):
        return base + (node.attr,)
    elif isinstance(node, ast.FunctionDef):
        return base + (node.name,)
    elif isinstance(node, ast.Param):
        return base + (node.name,)
    else:
        return base


def main1():
    if len(sys.argv) > 1:
        pytype_storage = sys.argv[1]
    else:
        pytype_storage = TYPE_INFER_PYTYPE_FILES

    if len(sys.argv) > 2:
        type_repo = sys.argv[2]
    else:
        type_repo = TYPE_INFER_PYTYPE_SAVE

    if len(sys.argv) > 2:
        project_path = sys.argv[3]
    else:
        project_path = TYPE_INFER_PROJECT_PATH

    if not os.path.exists(pytype_storage):
        os.makedirs(pytype_storage)
    if not os.path.exists(type_repo):
        os.makedirs(type_repo)
    project_name = TYPE_INFER_PROJECT_NAME
    project_path = os.path.join(TYPE_INFER_PROJECT_PATH, project_name)
    process_before_side(project_path, project_name, pytype_storage, type_repo)


def process_before_side(project_path, project_name, pytype_storage, type_repo):
    for root, dirs, files in os.walk(project_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)

                save_name = (type_repo + os.path.sep + project_name + os.path.sep
                             + file[:-3].replace(os.path.sep, '_') + '.json')
                dir = os.path.dirname(save_name)
                if not os.path.exists(dir):
                    os.makedirs(dir)
                try:
                    first_rev = generate_type_info(file_path, project_path, file.replace(os.path.sep, '_'), save_name,
                                                   pytype_storage, type_repo)
                except UnicodeEncodeError as e:
                    print(e)


def generate_type_info(file_path, project_path, file_name, save_name, pytype_storage, type_repo):
    generate_pytype_folder(project_path, file_path, pytype_storage, type_repo)
    try:
        with open(file_path, 'r') as f:
            src = f.read()
    except FileNotFoundError as e:
        return False
    except UnicodeDecodeError as e:
        return False
    first_empty_count = 0
    for line in src.split('\n'):
        if len(line) == 0:
            first_empty_count += 1
        else:
            break

    print(file_name[:-3] + 'imports')

    im_path = os.path.relpath(os.path.sep.join(file_path.split(os.path.sep)[:-1]), project_path).replace(os.path.sep,
                                                                                                         ".")

    if (im_path != "."):
        module = annotate(src, im_path + "." + file_name[:-3] + '.imports', pytype_storage, type_repo)
    else:
        module = annotate(src, file_name[:-3] + '.imports', pytype_storage, type_repo)
    if module is None:
        return False

    dic_str = get_annotations_dict(module, first_empty_count)

    with open(save_name, 'w') as outfile:
        json.dump(dic_str, outfile)
    return True


def repo_clone(url, location, repo_name):
    if (os.path.exists(location + repo_name)):
        return
    os.mkdir(location + repo_name)
    print("Repo is downloading to :" + location + os.path.sep + repo_name)
    Repo.clone_from(url=url, to_path=location + os.path.sep + repo_name)


if __name__ == '__main__':
    main1()
