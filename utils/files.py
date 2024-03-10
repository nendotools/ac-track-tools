from bpy import path
import os, json, configparser
from ..lib.settings import get_settings

##
##  Directory Management
##
def ensure_path_exists(loc: str):
    # if path ends in a file, remove the file
    if '.' in loc.split('/')[-1]:
        dir_path = '/'.join(loc.split('/')[:-1])
        os.makedirs(dir_path, exist_ok=True)
    else:
        os.makedirs(loc, exist_ok=True)
    return os.path.normpath(loc)

def get_active_directory():
    # get full path of the working directory
    loc = os.path.abspath(get_settings().working_dir)
    if loc in ['/','//','\\']:
        return path.abspath('//')
    return ensure_path_exists(loc)

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
