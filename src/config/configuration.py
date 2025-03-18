import sys
# import logging
from configparser import ConfigParser
from pathlib import Path

# TODO: remove unnecessary code

# TODO: defaults
DATABASE_PATH = 'Data'
PATTERNS_PATH = 'TODO'
RULES_PATH = 'TODO'
PROJECT_REPO = 'TODO'
TYPE_REPO = 'TODO'
FILES_PATH = 'TODO'
LANGUAGE = 'TODO'
# LOGGING_LEVEL = logging.WARNING

config_read = False


# log_level_map = {'DEBUG': logging.DEBUG,
#                  'INFO': logging.INFO,
#                  'WARNING': logging.WARNING,
#                  'ERROR': logging.ERROR,
#                  'CRITICAL': logging.CRITICAL
#                  }

# logging.basicConfig(level=LOGGING_LEVEL,
#                     format='%(asctime)s %(name)s %(levelname)s %(message)s',
#                     datefmt='%m/%d/%Y %H:%M:%S')
# logger = logging.getLogger('CVEfixes')
# logger.removeHandler(sys.stderr)


def read_config() -> None:
    """
    Read VulPyEvolve configuration from VulPyEvolve.ini, $HOME/src/config/VulPyEvolve.ini or $HOME/VulPyEvolve.ini

    Sets global constants with values found in the ini file.
    """
    global DATABASE_PATH, PATTERNS_PATH, PROJECT_REPO, TYPE_REPO, FILES_PATH, RULES_PATH, LANGUAGE, config_read

    config = ConfigParser()
    if config.read(['../VulPyEvolve.ini',
                    Path.home() / 'src' / 'config' / 'VulPyEvolve.ini',
                    Path.home() / 'VulPyEvolve.ini']):
        # try and update settings for each of the values, use
        DATABASE_PATH = config.get('Rules', 'database_path', fallback=DATABASE_PATH)
        PATTERNS_PATH = config.get('Rules', 'patterns_path', fallback=PATTERNS_PATH)
        RULES_PATH = config.get('Rules', 'rules_path', fallback=RULES_PATH)
        PROJECT_REPO = config.get('Project', 'project_repository', fallback=PROJECT_REPO)
        TYPE_REPO = config.get('Project', 'type_repository', fallback=TYPE_REPO)
        FILES_PATH = config.get('Project', 'files_path', fallback=FILES_PATH)
        LANGUAGE = config.get('Project', 'language', fallback=LANGUAGE)
        # TODO: is logging needed?
        # LOGGING_LEVEL = log_level_map.get(config.get('CVEfixes', 'logging_level', fallback='WARNING'),logging.WARNING)
        config_read = True
    else:
        # logger.warning('Cannot find CVEfixes config file in the working or $HOME directory, see INSTALL.md')
        print('Cannot find VulPyEvolve config file in the working or $HOME directory')
        sys.exit()


if not config_read:
    read_config()
    # logger.setLevel(LOGGING_LEVEL)
    # logging.getLogger("requests").setLevel(LOGGING_LEVEL)
    # logging.getLogger("urllib3").setLevel(logging.WARNING)
    # logging.getLogger("urllib3.connection").setLevel(logging.WARNING)
    # logging.getLogger("pathlib").setLevel(LOGGING_LEVEL)
    # logging.getLogger("subprocess").setLevel(LOGGING_LEVEL)
    # logging.getLogger("h5py._conv").setLevel(logging.WARNING)
    # logging.getLogger("git.cmd").setLevel(LOGGING_LEVEL)
    # logging.getLogger("github.Requester").setLevel(LOGGING_LEVEL)
