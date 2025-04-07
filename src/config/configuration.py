import sys
from configparser import ConfigParser
from pathlib import Path

# TODO: defaults
DATABASE_PATH = 'Data'
PATTERNS_PATH = 'TODO'
RULES_PATH = 'TODO'
PROJECT_REPO = 'TODO'
TYPE_REPO = 'TODO'
FILES_PATH = 'TODO'
LANGUAGE = 'TODO'

config_read = False


def read_config() -> None:
    """
    Read VulPyEvolve configuration from VulPyEvolve.ini, $HOME/src/config/VulPyEvolve.ini or $HOME/VulPyEvolve.ini

    Sets global constants with values found in the ini file.
    """
    global DATABASE_PATH, PATTERNS_PATH, PROJECT_REPO, TYPE_REPO, FILES_PATH, RULES_PATH, LANGUAGE, config_read

    config = ConfigParser()
    if config.read(['../VulPyEvolve.ini',
                    '../../VulPyEvolve.ini',
                    Path.home() / 'src' / 'config' / 'VulPyEvolve.ini',
                    Path.home() / 'VulPyEvolve.ini']):
        DATABASE_PATH = config.get('Rules', 'database_path', fallback=DATABASE_PATH)
        PATTERNS_PATH = config.get('Rules', 'patterns_path', fallback=PATTERNS_PATH)
        RULES_PATH = config.get('Rules', 'rules_path', fallback=RULES_PATH)
        PROJECT_REPO = config.get('Project', 'project_repository', fallback=PROJECT_REPO)
        TYPE_REPO = config.get('Project', 'type_repository', fallback=TYPE_REPO)
        FILES_PATH = config.get('Project', 'files_path', fallback=FILES_PATH)
        LANGUAGE = config.get('Project', 'language', fallback=LANGUAGE)
        config_read = True
    else:
        print('Cannot find VulPyEvolve config file in the working or $HOME directory')
        sys.exit()


if not config_read:
    read_config()
