# __init__.py
# Copyright (C) 2026 Chai Chaimee
# Licensed under GNU General Public License. See COPYING.txt for details.

import globalPluginHandler
from scriptHandler import script
from brailleInput import handler as brailleInputHandler
import keyboardHandler
import api
import addonHandler
import ui
import wx
import time
import os
import globalVars
import gui
import sys
from . import config
from . import settingsDialog

addonHandler.initTranslation()

# Detect if we should use the new method (ONLY for NVDA 2026.1 64-bit)
_use_new = False
try:
	# Check if winBindings.user32 exists (new API in 2026.1 64-bit)
	from winBindings.user32 import keybd_event, KEYEVENTF
	from winUser import VK_CONTROL
	import speech
	import core
	import config as nvdaGlobalConfig
	_use_new = True
except ImportError:
	# Fallback to legacy method
	import winUser
	import speech

if not _use_new:
	# Legacy imports (for 32-bit or older NVDA)
	from NVDAObjects.IAccessible.winword import WordDocument
	from NVDAObjects.UIA import UIA

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	scriptCategory = addonHandler.getCodeAddon().manifest["summary"]
	
	def __init__(self):
		super(GlobalPlugin, self).__init__()
		self.enabled = True
		self.active_set = 1
		self.last_toggle_time = 0
		self.toggle_count = 0
		wx.CallAfter(self.registerSettingsPanel)

	def registerSettingsPanel(self):
		try:
			if settingsDialog.SpecialCharacterSettingsPanel not in gui.settingsDialogs.NVDASettingsDialog.categoryClasses:
				gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(settingsDialog.SpecialCharacterSettingsPanel)
		except Exception as e:
			ui.message(_("Error registering settings panel") + ": %s" % str(e))

	# ============================================================
	# LEGACY METHOD (for 32-bit and NVDA before 2026.1 64-bit)
	# ============================================================
	def _send_legacy(self, char):
		try:
			focus = api.getFocusObject()
			app_name = focus.appModule.appName.lower() if hasattr(focus, 'appModule') and hasattr(focus.appModule, 'appName') else ""
			
			speech.speakText(char)

			if app_name == 'winword':
				try:
					api.copyToClip(char)
					winUser.keybd_event(winUser.VK_CONTROL, 0, 0, 0)
					winUser.keybd_event(0x56, 0x2f, 0, 0)
					winUser.keybd_event(0x56, 0x2f, winUser.KEYEVENTF_KEYUP, 0)
					winUser.keybd_event(winUser.VK_CONTROL, 0, winUser.KEYEVENTF_KEYUP, 0)
				except Exception:
					keyboardHandler.KeyboardInputGesture.fromName("control+v").send()

			elif app_name in ('chrome', 'firefox', 'brave', 'edge', 'safari'):
				if char in ('"', '/', '\\', '.', '|'):
					keyboardHandler.KeyboardInputGesture.fromName(char).send()
				else:
					api.copyToClip(char)
					keyboardHandler.KeyboardInputGesture.fromName("control+v").send()

			elif brailleInputHandler:
				brailleInputHandler.sendChars(char)

			else:
				if hasattr(focus, 'edit') and hasattr(focus.edit, 'textInsert'):
					focus.edit.textInsert(char)
				else:
					api.copyToClip(char)
					keyboardHandler.KeyboardInputGesture.fromName("control+v").send()

		except Exception as e:
			ui.message(_("Cannot insert character") + " %s: %s" % (char, str(e)))

	def _sendCharacters_legacy(self, chars: str):
		if brailleInputHandler is not None:
			brailleInputHandler.sendChars(chars)

	# ============================================================
	# NEW METHOD for NVDA 2026.1 64-bit (NO double speaking)
	# ============================================================
	def _send_new(self, char):
		# Temporarily disable NVDA's automatic typed character announcement
		original_typed = nvdaGlobalConfig.conf["keyboard"]["speakTypedCharacters"]
		if original_typed:
			nvdaGlobalConfig.conf["keyboard"]["speakTypedCharacters"] = False

		try:
			focus = api.getFocusObject()
			app_name = focus.appModule.appName.lower() if hasattr(focus, 'appModule') and hasattr(focus.appModule, 'appName') else ""

			# Insert character using appropriate method (no announcement yet)
			if app_name == 'winword':
				try:
					api.copyToClip(char)
					keybd_event(0x56, 0x2f, 0, 0)
					keybd_event(0x56, 0x2f, KEYEVENTF.KEYUP, 0)
					keybd_event(VK_CONTROL, 0, KEYEVENTF.KEYUP, 0)
				except Exception:
					keyboardHandler.KeyboardInputGesture.fromName("control+v").send()

			elif app_name in ('chrome', 'firefox', 'brave', 'edge', 'safari'):
				if char in ('"', '/', '\\', '.', '|'):
					keyboardHandler.KeyboardInputGesture.fromName(char).send()
				else:
					api.copyToClip(char)
					keyboardHandler.KeyboardInputGesture.fromName("control+v").send()

			elif brailleInputHandler:
				brailleInputHandler.sendChars(char)

			else:
				if hasattr(focus, 'edit') and hasattr(focus.edit, 'textInsert'):
					focus.edit.textInsert(char)
				else:
					api.copyToClip(char)
					keyboardHandler.KeyboardInputGesture.fromName("control+v").send()

			# Announce exactly once after insertion, then restore setting
			core.callLater(0, self._announce_and_restore, char, original_typed)

		except Exception as e:
			ui.message(_("Cannot insert character") + " %s: %s" % (char, str(e)))
			if original_typed:
				nvdaGlobalConfig.conf["keyboard"]["speakTypedCharacters"] = original_typed

	def _announce_and_restore(self, char, original_typed):
		speech.speakText(char)
		if original_typed:
			nvdaGlobalConfig.conf["keyboard"]["speakTypedCharacters"] = original_typed

	def _sendCharacters_new(self, chars: str):
		for ch in chars:
			self._send_new(ch)

	# ============================================================
	# WRAPPER
	# ============================================================
	def _send(self, char):
		if _use_new:
			self._send_new(char)
		else:
			self._send_legacy(char)

	def _sendCharacters(self, chars: str):
		if _use_new:
			self._sendCharacters_new(chars)
		else:
			self._sendCharacters_legacy(chars)

	def _get_char_and_send(self, key_name):
		if not self.enabled:
			ui.message(_("Special Character Add-on is currently disabled."))
			return True
		char_to_send = config.get_char(key_name, self.active_set)
		if char_to_send:
			self._send(char_to_send)
		return True

	# --- Script Mappings (unchanged) ---
	@script(gesture="kb:control+1", description=_("Insert Slot 1"))
	def script_key1(self, gesture): return self._get_char_and_send("ctrl+1")
	@script(gesture="kb:control+2", description=_("Insert Slot 2"))
	def script_key2(self, gesture): return self._get_char_and_send("ctrl+2")
	@script(gesture="kb:control+3", description=_("Insert Slot 3"))
	def script_key3(self, gesture): return self._get_char_and_send("ctrl+3")
	@script(gesture="kb:control+4", description=_("Insert Slot 4"))
	def script_key4(self, gesture): return self._get_char_and_send("ctrl+4")
	@script(gesture="kb:control+5", description=_("Insert Slot 5"))
	def script_key5(self, gesture): return self._get_char_and_send("ctrl+5")
	@script(gesture="kb:control+6", description=_("Insert Slot 6"))
	def script_key6(self, gesture): return self._get_char_and_send("ctrl+6")
	@script(gesture="kb:control+7", description=_("Insert Slot 7"))
	def script_key7(self, gesture): return self._get_char_and_send("ctrl+7")
	@script(gesture="kb:control+8", description=_("Insert Slot 8"))
	def script_key8(self, gesture): return self._get_char_and_send("ctrl+8")
	@script(gesture="kb:control+9", description=_("Insert Slot 9"))
	def script_key9(self, gesture): return self._get_char_and_send("ctrl+9")
	@script(gesture="kb:control+0", description=_("Insert Slot 0"))
	def script_key0(self, gesture): return self._get_char_and_send("ctrl+0")
	@script(gesture="kb:control+-", description=_("Insert Slot hyphen"))
	def script_key_minus(self, gesture): return self._get_char_and_send("ctrl+-")
	@script(gesture="kb:control+=", description=_("Insert Slot equals"))
	def script_key_equals(self, gesture): return self._get_char_and_send("ctrl+=")

	@script(gesture="kb:shift+windows+|", description=_("Insert vertical bar"))
	def script_shiftWinPipe(self, gesture):
		if not self.enabled: return True
		self._send("|")
		return True

	@script(gesture="kb:shift+windows+.", description=_("Insert –"))
	def script_shiftWinDot(self, gesture):
		if not self.enabled: return True
		self._sendCharacters("\N{en dash}")
		return True

	@script(gesture="kb:shift+windows+/", description=_("Insert —"))
	def script_shiftWinSlash(self, gesture):
		if not self.enabled: return True
		self._sendCharacters("\N{em dash}")
		return True

	@script(gesture="kb:shift+backspace", description=_("Toggle character set or add-on"))
	def script_toggleAddon(self, gesture):
		current_time = time.time()
		if current_time - self.last_toggle_time < 0.5: self.toggle_count += 1
		else: self.toggle_count = 1
		self.last_toggle_time = current_time
		if self.toggle_count == 1: wx.CallLater(500, self._process_toggle)
		return True

	def _process_toggle(self):
		if self.toggle_count == 1:
			self.active_set = 2 if self.active_set == 1 else 1
			ui.message(_("Switched set %s") % self.active_set)
		elif self.toggle_count >= 2:
			self.enabled = not self.enabled
			state = _("on") if self.enabled else _("off")
			ui.message(_("Special Character %s") % state)
		self.toggle_count = 0

	def terminate(self):
		try:
			if settingsDialog.SpecialCharacterSettingsPanel in gui.settingsDialogs.NVDASettingsDialog.categoryClasses:
				gui.settingsDialogs.NVDASettingsDialog.categoryClasses.remove(settingsDialog.SpecialCharacterSettingsPanel)
		except ValueError:
			pass
		super(GlobalPlugin, self).terminate()