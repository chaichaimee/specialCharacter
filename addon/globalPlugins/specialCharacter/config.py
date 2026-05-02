# config.py

import json
import os
import shutil
import addonHandler
import globalVars
import ui
import gettext
import logHandler

# Initialize translation function for this module
addonHandler.initTranslation()
_ = gettext.gettext

# Default configurations for special characters
# Fixed syntax: use single quotes for outer keys and escape inner quotes
DEFAULT_CHARACTERS = {
	'set1': {
		'ctrl+1': '•',
		'ctrl+2': '()',
		'ctrl+3': '?',
		'ctrl+4': '?',
		'ctrl+5': '?',
		'ctrl+6': '฿',
		'ctrl+7': '€',
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
		'ctrl+0': '…',
		'ctrl+-': '?',
		'ctrl+=': '\x15',        # using hex escape for control character
	},
}

def get_config_path():
	"""Returns the path to the specialCharacters.json config file in the ChaiChaimee subfolder."""
	return os.path.join(globalVars.appArgs.configPath, "ChaiChaimee", "specialCharacters.json")

def migrate_old_config():
	"""
	Checks for the existence of the old config file (directly in userConfig folder)
	and moves it to the new location (userConfig\ChaiChaimee\) if found.
	Uses a safe copy-and-delete approach to avoid issues with locked files.
	This function is called every time the module is loaded, ensuring retry if previous attempts failed.
	"""
	old_path = os.path.join(globalVars.appArgs.configPath, "specialCharacters.json")
	new_path = get_config_path()
	
	# Log the paths for debugging
	logHandler.log.debug("migrate_old_config: old_path=%s, new_path=%s", old_path, new_path)
	
	# If old file doesn't exist, nothing to do
	if not os.path.exists(old_path):
		logHandler.log.debug("Old config file does not exist, no migration needed.")
		return
	
	logHandler.log.info("Old config file found at %s", old_path)
	
	# If new file already exists, we should not overwrite; but we may still want to delete the old file if it's identical?
	# For safety, we will not delete old file if new exists; just log a warning.
	if os.path.exists(new_path):
		logHandler.log.warning("Old config file exists at %s but new config already exists at %s. Not migrating.", old_path, new_path)
		# Optionally, we could compare contents and delete old if identical, but that's more complex.
		return
	
	try:
		# Ensure the destination directory exists
		os.makedirs(os.path.dirname(new_path), exist_ok=True)
		logHandler.log.debug("Destination directory ensured: %s", os.path.dirname(new_path))
		
		# Read the old file content
		with open(old_path, "r", encoding="utf-8") as f:
			data = f.read()
		logHandler.log.debug("Old file read successfully, size=%d bytes", len(data))
		
		# Write to new file
		with open(new_path, "w", encoding="utf-8") as f:
			f.write(data)
		logHandler.log.debug("New file written successfully")
		
		# Verify that the new file was written correctly (optional)
		if os.path.exists(new_path):
			logHandler.log.info("New config file created at %s", new_path)
		else:
			logHandler.log.error("New file does not exist after write!")
			return
		
		# If write succeeded, remove the old file
		os.remove(old_path)
		logHandler.log.info("Old config file removed successfully")
		
		# Final verification
		if not os.path.exists(old_path) and os.path.exists(new_path):
			logHandler.log.info("Migration completed successfully.")
		else:
			logHandler.log.warning("Migration may be incomplete: old exists=%s, new exists=%s",
								   os.path.exists(old_path), os.path.exists(new_path))
		
	except Exception as e:
		logHandler.log.error("Failed to migrate old config file: %s", e, exc_info=True)
		# Optionally, show a message to the user, but only once to avoid spam.
		# We'll use a flag to prevent repeated messages.
		if not hasattr(migrate_old_config, "_shown_error"):
			ui.message(_("Could not migrate old configuration file: %s") % e)
			migrate_old_config._shown_error = True

# Perform migration before loading the config
migrate_old_config()

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
	except Exception as e:
		logHandler.log.error("Error loading config from %s: %s", path, e, exc_info=True)

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