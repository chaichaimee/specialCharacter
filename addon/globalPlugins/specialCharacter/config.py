# config.py

import json
import os
import addonHandler
import globalVars
import ui # Need to import ui for error messages in save_config
import gettext

# Initialize translation function for this module
addonHandler.initTranslation()
_ = gettext.gettext

# Default configurations for special characters
DEFAULT_CHARACTERS = {
    "set1": {
        "ctrl+1": "•",
        "ctrl+2": "()",
        "ctrl+3": "±",
        "ctrl+4": "×",
        "ctrl+5": "÷",
        "ctrl+6": "฿",
        "ctrl+7": "€",
        "ctrl+8": "£",
        "ctrl+9": "¢",
        "ctrl+0": "©",
        "ctrl+-": "®",
        "ctrl+=": "™",
    },
    "set2": {
        "ctrl+1": "°",
        "ctrl+2": "½",
        "ctrl+3": "¼",
        "ctrl+4": "¾",
        "ctrl+5": "√",
        "ctrl+6": "′",
        "ctrl+7": "″",
        "ctrl+8": "µ",
        "ctrl+9": "¥",
        "ctrl+0": "…",
        "ctrl+-": "†",
        "ctrl+=": "§",
    },
}

def get_config_path():
    """Returns the path to the specialCharacters.json config file."""
    # Store directly in userConfig folder
    return os.path.join(globalVars.appArgs.configPath, "specialCharacters.json")

def load_config():
    """Loads character configuration from file or returns default if not found."""
    path = get_config_path()
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Ensure data has the correct structure; merge with defaults if needed
                if "set1" in data and "set2" in data:
                    return data
    except Exception:
        pass # Ignore errors and return default data

    # Return default characters if loading failed or file doesn't exist/is invalid
    return DEFAULT_CHARACTERS

def save_config(char_config):
    """Saves the character configuration to file."""
    path = get_config_path()
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(char_config, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        # Use %s placeholder for translation compatibility
        ui.message(_("Error saving special characters configuration: %s") % e)
        return False

# Global variable to hold the loaded configuration
special_characters = load_config()

def get_char(key, active_set):
    """Retrieves a character based on key and active set."""
    set_key = f"set{active_set}"
    return special_characters.get(set_key, {}).get(key, "")

def set_char(key, active_set, char):
    """Sets a character for a given key and active set."""
    set_key = f"set{active_set}"
    if set_key not in special_characters:
        special_characters[set_key] = {}
    special_characters[set_key][key] = char

def update_and_save_config(new_config):
    """Updates the global config and saves it to disk."""
    global special_characters
    special_characters = new_config
    return save_config(special_characters)
