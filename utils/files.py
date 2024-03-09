import os, json, configparser
from ..lib.settings import get_settings

##
##  Directory Management
##
def ensure_path_exists(path: str):
    # if path ends in a file, remove the file
    if '.' in path.split('/')[-1]:
        dir_path = '/'.join(path.split('/')[:-1])
        os.makedirs(dir_path, exist_ok=True)
    else:
        os.makedirs(path, exist_ok=True)
    return os.path.normpath(path)

def get_active_directory():
    return ensure_path_exists(get_settings().working_dir)

def get_ai_directory():
    return ensure_path_exists(get_active_directory() + '/ai/')

def get_data_directory():
    return ensure_path_exists(get_active_directory() + '/data/')

def get_ui_directory():
    return ensure_path_exists(get_active_directory() + '/ui/')

##
##  JSON Files
##
def load_json(filename: str):
    normalized_file = ensure_path_exists(filename)
    try:
        with open(normalized_file, 'r') as file:
            return json.load(file)
    except:
        return None

def save_json(filename: str, data):
    normalized_file = ensure_path_exists(filename)
    with open(normalized_file, 'w') as file:
        json.dump(data, file)

##
##  INI Files
##
def load_ini(filename: str):
    config = configparser.ConfigParser()
    try:
        config.read(filename)
        return config
    except:
        return None

def save_ini(filename: str, config: dict):
    parser = configparser.ConfigParser()
    parser.read_dict(config)
    normalized_file = ensure_path_exists(filename)
    with open(normalized_file, 'w') as configfile:
        parser.write(configfile)
