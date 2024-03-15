from bpy import path
import os, re, json, configparser
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
    abs_path = path.abspath(get_settings().working_dir)
    return os.path.realpath(abs_path)

def get_ai_directory():
    return ensure_path_exists(get_active_directory() + '/ai/')

def get_data_directory():
    return ensure_path_exists(get_active_directory() + '/data/')

def get_ui_directory():
    return ensure_path_exists(get_active_directory() + '/ui/')

def get_content_directory():
    return ensure_path_exists(get_active_directory() + '/content/')

def get_sfx_directory():
    return ensure_path_exists(get_content_directory() + '/sfx/')

##
## Import File
##

def verify_local_file(file_path: str, folder: str):
    if not file_path or not os.path.exists(file_path):
        return None
    if file_path.startswith(get_active_directory()):
        return file_path
    if not os.path.exists(file_path):
        return None
    target_file = ensure_path_exists(get_active_directory() + '/' + folder + '/' + file_path.split('/')[-1])
    if not os.path.exists(target_file):
        os.system('cp "' + file_path + '" "' + target_file + '"')
    return target_file

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
        parser.write(configfile, False)
