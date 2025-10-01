import configparser
import json
import os

from bpy import path

##
##  Directory Management
##
path_ref = ""
def ensure_path_exists(loc: str):
    # if path ends in a file, remove the file
    if '.' in loc.split('/')[-1]:
        dir_path = '/'.join(loc.split('/')[:-1])
        os.makedirs(dir_path, exist_ok=True)
    else:
        os.makedirs(loc, exist_ok=True)
    return os.path.normpath(loc)

def set_path_reference(path: str):
    global path_ref
    path_ref = path

def get_active_directory():
    abs_path = path.abspath(path_ref)
    return os.path.realpath(abs_path)

def get_ai_directory():
    return ensure_path_exists(get_active_directory() + '/ai/')

def get_data_directory():
    return ensure_path_exists(get_active_directory() + '/data/')

def get_ui_directory():
    return ensure_path_exists(get_active_directory() + '/ui/')

def get_content_directory():
    return ensure_path_exists(get_active_directory() + '/content/')

def get_extension_directory():
    return ensure_path_exists(get_active_directory() + '/extension/')

def get_sfx_directory():
    return ensure_path_exists(get_content_directory() + '/sfx/')

def get_texture_directory():
    return ensure_path_exists(get_content_directory() + '/texture/')

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
        return None
    return target_file

##
##  JSON Files
##
def load_json(filename: str):
    normalized_file = ensure_path_exists(filename)
    try:
        with open(normalized_file, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

def save_json(filename: str, data):
    normalized_file = ensure_path_exists(filename)
    with open(normalized_file, 'w') as file:
        json.dump(data, file)

##
##  INI Files
##
def load_ini(filename: str):
    config = configparser.ConfigParser(allow_no_value=True, strict=False)
    try:
        config.read(filename)
        return config
    except (FileNotFoundError, configparser.Error):
        return None

def save_ini(filename: str, config: dict):
    parser = configparser.ConfigParser()
    parser.optionxform = lambda option: option
    parser.read_dict(config)
    normalized_file = ensure_path_exists(filename)
    with open(normalized_file, 'w') as configfile:
        parser.write(configfile, False)

def find_maps():
    main_dir = get_active_directory()
    ui_dir = get_ui_directory()
    result = {}
    map = os.path.normpath(main_dir + '/map.png')
    outline = os.path.normpath(ui_dir + '/outline.png')
    preview = os.path.normpath(ui_dir + '/preview.png')
    result['map'] = map if os.path.exists(map) else None
    result['outline'] = outline if os.path.exists(outline) else None
    result['preview'] = preview if os.path.exists(preview) else None
    return result
