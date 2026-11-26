import glob
import os
import re

import globalVars
from logHandler import log

_BOOL_ECHO_LINE = re.compile(
	rb"^([ \t]*(?:speakTypedCharacters|speakTypedWords)[ \t]*=[ \t]*)(true|false)(?=[ \t]*\r?$)",
	re.IGNORECASE | re.MULTILINE,
)


def _asMode(match):
	return match.group(1) + (b"1" if match.group(2).lower() == b"true" else b"0")


def onInstall():
	configDir = globalVars.appArgs.configPath
	configFiles = [os.path.join(configDir, "nvda.ini")]
	configFiles += glob.glob(os.path.join(configDir, "profiles", "*.ini"))
	for configFile in configFiles:
		try:
			with open(configFile, "rb") as readHandle:
				fileBytes = readHandle.read()
			repairedBytes, replacedCount = _BOOL_ECHO_LINE.subn(_asMode, fileBytes)
			if not replacedCount:
				continue
			with open(configFile, "wb") as writeHandle:
				writeHandle.write(repairedBytes)
			log.info("specialCharacter: repaired %d typing echo value(s) in %s", replacedCount, configFile)
		except OSError:
			log.debugWarning("specialCharacter: could not repair %s", configFile, exc_info=True)
