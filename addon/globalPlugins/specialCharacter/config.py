# config.py

import copy
import json
import os
import shutil
import addonHandler
import globalVars
import ui
import logHandler

# Initialize translation function for this module
addonHandler.initTranslation()

# Default configurations for special characters
# Fixed syntax: use single quotes for outer keys and escape inner quotes
DEFAULT_CHARACTERS = {
	'set1': {
		'ctrl+1': '\u2022',
		'ctrl+2': '()',
		'ctrl+3': '?',
		'ctrl+4': '?',
		'ctrl+5': '?',
		'ctrl+6': '\u0e3f',
		'ctrl+7': '\u20ac',
		'ctrl+8': '?',
		'ctrl+9': '?',
		'ctrl+0': '?',
		'ctrl+-': '?',
		'ctrl+=': '?',
	},
	'set2': {
		'ctrl+1': '?',
		'ctrl+2': '?',
		'ctrl+3': '?',
		'ctrl+4': '?',
		'ctrl+5': '?',
		'ctrl+6': "'",          # single quote inside single-quoted string is fine
		'ctrl+7': '"',           # double quote escaped by using single quotes outside
		'ctrl+8': '?',
		'ctrl+9': '?',
		'ctrl+0': '\u2026',
		'ctrl+-': '?',
		'ctrl+=': '\x15',        # using hex escape for control character
	},
}

CONFIG_FILE_NAME = "specialCharacters.json"

def get_config_path():
	"""Returns the path to specialCharacters.json in the ChaiChaimee\\specialCharacter subfolder."""
	return os.path.join(globalVars.appArgs.configPath, "ChaiChaimee", "specialCharacter", CONFIG_FILE_NAME)

def _legacy_config_paths():
	# Newest location first: the ChaiChaimee subfolder, then the userConfig root
	userConfigPath = globalVars.appArgs.configPath
	return [
		os.path.join(userConfigPath, "ChaiChaimee", CONFIG_FILE_NAME),
		os.path.join(userConfigPath, CONFIG_FILE_NAME),
	]

def migrate_old_config():
	"""Moves the config file from an older location to the current one. Retried on every load until it succeeds."""
	newPath = get_config_path()
	existing = [p for p in _legacy_config_paths() if os.path.exists(p)]
	if not existing:
		return
	oldPath = existing[0]
	if os.path.exists(newPath):
		logHandler.log.warning("Old config file %s found but %s already exists. Not migrating.", oldPath, newPath)
		return
	tempPath = newPath + ".tmp"
	try:
		os.makedirs(os.path.dirname(newPath), exist_ok=True)
		# Copy then delete, so a locked or half-copied file never loses the user's settings
		shutil.copyfile(oldPath, tempPath)
		os.replace(tempPath, newPath)
		os.remove(oldPath)
		logHandler.log.info("Config file moved from %s to %s", oldPath, newPath)
	except Exception as e:
		logHandler.log.error("Failed to migrate old config file: %s", e, exc_info=True)
		if not hasattr(migrate_old_config, "_shown_error"):
			ui.message(_("Could not migrate old configuration file: %s") % e)
			migrate_old_config._shown_error = True

# Perform migration before loading the config
migrate_old_config()

def load_config():
	"""Loads character configuration from file, filling any missing slot from the defaults."""
	merged = copy.deepcopy(DEFAULT_CHARACTERS)
	path = get_config_path()
	if not os.path.exists(path):
		return merged
	try:
		with open(path, "r", encoding="utf-8") as f:
			saved = json.load(f)
	except Exception as e:
		logHandler.log.error("Error loading config from %s: %s", path, e, exc_info=True)
		return merged
	if not isinstance(saved, dict):
		logHandler.log.error("Config file %s does not hold a JSON object; using defaults", path)
		return merged
	for setKey, slots in saved.items():
		if not isinstance(slots, dict):
			continue
		targetSet = merged.setdefault(setKey, {})
		for slotKey, char in slots.items():
			if isinstance(char, str):
				targetSet[slotKey] = char
	return merged

def save_config(char_config):
	"""Saves the character configuration to file."""
	path = get_config_path()
	tempPath = path + ".tmp"
	try:
		os.makedirs(os.path.dirname(path), exist_ok=True)
		# Write to a temp file first so a crash mid-write cannot leave a truncated config
		with open(tempPath, "w", encoding="utf-8") as f:
			json.dump(char_config, f, indent=4, ensure_ascii=False)
		os.replace(tempPath, path)
		return True
	except Exception as e:
		logHandler.log.error("Error saving config to %s: %s", path, e, exc_info=True)
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