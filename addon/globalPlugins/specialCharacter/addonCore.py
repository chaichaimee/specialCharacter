# addonCore.py

import globalPluginHandler
from scriptHandler import script
import characterProcessing
import keyboardHandler
import api
import addonHandler
import ui
import wx
import time
import gui
from . import config
from . import settingsDialog
import core
import logHandler
from comtypes import COMError
import config as nvdaGlobalConfig

addonHandler.initTranslation()

def _getBrailleInputHandler():
	# NVDA 2026.x moved the handler to braille.input and deprecated brailleInput.handler
	try:
		from braille.input import handler
	except ImportError:
		from brailleInput import handler
	return handler

# Detect if we should use the new method (ONLY for NVDA 2026.1 64-bit)
_use_new = False
try:
	# Check if winBindings.user32 exists (new API in 2026.1 64-bit)
	from winBindings.user32 import keybd_event, KEYEVENTF
	from winUser import VK_CONTROL
	import speech
	_use_new = True
except ImportError:
	# Fallback to legacy method
	import winUser
	import speech

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	scriptCategory = addonHandler.getCodeAddon().manifest["summary"]

	# Delay (ms) between writing the clipboard and sending control+v so the
	# OS clipboard update has time to settle before the browser reads it.
	CLIPBOARD_SETTLE_DELAY_MS = 40

	def __init__(self):
		super(GlobalPlugin, self).__init__()
		self.enabled = True
		self.active_set = 1
		self.last_toggle_time = 0
		self.toggle_count = 0
		self.toggleTimer = None
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
		original_typed = nvdaGlobalConfig.conf["keyboard"]["speakTypedCharacters"]
		if original_typed:
			nvdaGlobalConfig.conf["keyboard"]["speakTypedCharacters"] = False

		try:
			focus = api.getFocusObject()
			app_name = focus.appModule.appName.lower() if hasattr(focus, 'appModule') and hasattr(focus.appModule, 'appName') else ""

			if app_name == 'winword':
				if self._insertViaWordObjectModel(focus, char):
					core.callLater(0, self._announce_and_restore, char, original_typed)
					return
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
					core.callLater(0, self._announce_and_restore, char, original_typed)
				else:
					api.copyToClip(char)
					# Some browser edit fields miss the paste if control+v is sent
					# in the same call stack as the clipboard write; give the OS
					# clipboard update a short moment to settle before pasting.
					core.callLater(self.CLIPBOARD_SETTLE_DELAY_MS, self._pasteAndAnnounce, char, original_typed)
				return

			elif _getBrailleInputHandler():
				_getBrailleInputHandler().sendChars(char)

			else:
				if hasattr(focus, 'edit') and hasattr(focus.edit, 'textInsert'):
					focus.edit.textInsert(char)
				else:
					api.copyToClip(char)
					core.callLater(self.CLIPBOARD_SETTLE_DELAY_MS, self._pasteAndAnnounce, char, original_typed)
					return

			core.callLater(0, self._announce_and_restore, char, original_typed)

		except Exception as e:
			ui.message(_("Cannot insert character") + " %s: %s" % (char, str(e)))
			if original_typed:
				nvdaGlobalConfig.conf["keyboard"]["speakTypedCharacters"] = original_typed

	def _sendCharacters_legacy(self, chars: str):
		inputHandler = _getBrailleInputHandler()
		if inputHandler is not None:
			inputHandler.sendChars(chars)

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
				if self._insertViaWordObjectModel(focus, char):
					core.callLater(0, self._announce_and_restore, char, original_typed)
					return
				try:
					api.copyToClip(char)
					keybd_event(VK_CONTROL, 0, 0, 0)
					keybd_event(0x56, 0x2f, 0, 0)
					keybd_event(0x56, 0x2f, KEYEVENTF.KEYUP, 0)
					keybd_event(VK_CONTROL, 0, KEYEVENTF.KEYUP, 0)
				except Exception:
					keyboardHandler.KeyboardInputGesture.fromName("control+v").send()

			elif app_name in ('chrome', 'firefox', 'brave', 'edge', 'safari'):
				if char in ('"', '/', '\\', '.', '|'):
					keyboardHandler.KeyboardInputGesture.fromName(char).send()
					core.callLater(0, self._announce_and_restore, char, original_typed)
				else:
					api.copyToClip(char)
					# Some browser edit fields miss the paste if control+v is sent
					# in the same call stack as the clipboard write; give the OS
					# clipboard update a short moment to settle before pasting.
					core.callLater(self.CLIPBOARD_SETTLE_DELAY_MS, self._pasteAndAnnounce, char, original_typed)
				return

			elif _getBrailleInputHandler():
				_getBrailleInputHandler().sendChars(char)

			else:
				if hasattr(focus, 'edit') and hasattr(focus.edit, 'textInsert'):
					focus.edit.textInsert(char)
				else:
					api.copyToClip(char)
					core.callLater(self.CLIPBOARD_SETTLE_DELAY_MS, self._pasteAndAnnounce, char, original_typed)
					return

			# Announce exactly once after insertion, then restore setting
			core.callLater(0, self._announce_and_restore, char, original_typed)

		except Exception as e:
			ui.message(_("Cannot insert character") + " %s: %s" % (char, str(e)))
			if original_typed:
				nvdaGlobalConfig.conf["keyboard"]["speakTypedCharacters"] = original_typed

	def _insertViaWordObjectModel(self, focus, char):
		# Selection.TypeText inserts at the caret through Word's own object
		# model, the same as real typing. It never touches the clipboard and
		# never triggers Word's Paste Options smart tag, unlike Ctrl+V.
		try:
			selection = focus.WinwordSelectionObject
		except AttributeError:
			return False
		try:
			selection.TypeText(char)
		except COMError:
			logHandler.log.debugWarning(
				"WinwordSelectionObject.TypeText failed, falling back to clipboard paste",
				exc_info=True,
			)
			return False
		return True

	def _pasteAndAnnounce(self, char, original_typed):
		keyboardHandler.KeyboardInputGesture.fromName("control+v").send()
		self._announce_and_restore(char, original_typed)

	def _announce_and_restore(self, char, original_typed):
		# Symbol level ALL so a bullet or tilde is spoken even when the user's level would drop it
		speech.speakText(char, symbolLevel=characterProcessing.SymbolLevel.ALL)
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

	def _get_char_and_send(self, key_name, gesture):
		if not self.enabled:
			gesture.send()
			return True
		char_to_send = config.get_char(key_name, self.active_set)
		if char_to_send:
			self._send(char_to_send)
		return True

	# --- Script Mappings (unchanged) ---
	@script(gesture="kb:control+1", description=_("Insert Slot 1"))
	def script_key1(self, gesture): return self._get_char_and_send("ctrl+1", gesture)
	@script(gesture="kb:control+2", description=_("Insert Slot 2"))
	def script_key2(self, gesture): return self._get_char_and_send("ctrl+2", gesture)
	@script(gesture="kb:control+3", description=_("Insert Slot 3"))
	def script_key3(self, gesture): return self._get_char_and_send("ctrl+3", gesture)
	@script(gesture="kb:control+4", description=_("Insert Slot 4"))
	def script_key4(self, gesture): return self._get_char_and_send("ctrl+4", gesture)
	@script(gesture="kb:control+5", description=_("Insert Slot 5"))
	def script_key5(self, gesture): return self._get_char_and_send("ctrl+5", gesture)
	@script(gesture="kb:control+6", description=_("Insert Slot 6"))
	def script_key6(self, gesture): return self._get_char_and_send("ctrl+6", gesture)
	@script(gesture="kb:control+7", description=_("Insert Slot 7"))
	def script_key7(self, gesture): return self._get_char_and_send("ctrl+7", gesture)
	@script(gesture="kb:control+8", description=_("Insert Slot 8"))
	def script_key8(self, gesture): return self._get_char_and_send("ctrl+8", gesture)
	@script(gesture="kb:control+9", description=_("Insert Slot 9"))
	def script_key9(self, gesture): return self._get_char_and_send("ctrl+9", gesture)
	@script(gesture="kb:control+0", description=_("Insert Slot 0"))
	def script_key0(self, gesture): return self._get_char_and_send("ctrl+0", gesture)
	@script(gesture="kb:control+-", description=_("Insert Slot hyphen"))
	def script_key_minus(self, gesture): return self._get_char_and_send("ctrl+-", gesture)
	@script(gesture="kb:control+=", description=_("Insert Slot equals"))
	def script_key_equals(self, gesture): return self._get_char_and_send("ctrl+=", gesture)

	@script(gesture="kb:shift+windows+|", description=_("Insert vertical bar"))
	def script_shiftWinPipe(self, gesture):
		if not self.enabled:
			gesture.send()
			return True
		self._send("|")
		return True

	@script(gesture="kb:shift+windows+.", description=_("Insert en dash"))
	def script_shiftWinDot(self, gesture):
		if not self.enabled:
			gesture.send()
			return True
		self._sendCharacters("\N{en dash}")
		return True

	@script(gesture="kb:shift+windows+/", description=_("Insert em dash"))
	def script_shiftWinSlash(self, gesture):
		if not self.enabled:
			gesture.send()
			return True
		self._sendCharacters("\N{em dash}")
		return True

	@script(gesture="kb:shift+backspace", description=_("Toggle character set or add-on"))
	def script_toggleAddon(self, gesture):
		current_time = time.time()
		if current_time - self.last_toggle_time < 0.5: self.toggle_count += 1
		else: self.toggle_count = 1
		self.last_toggle_time = current_time
		if self.toggle_count == 1: self.toggleTimer = wx.CallLater(500, self._process_toggle)
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
		if self.toggleTimer and self.toggleTimer.IsRunning():
			self.toggleTimer.Stop()
		try:
			if settingsDialog.SpecialCharacterSettingsPanel in gui.settingsDialogs.NVDASettingsDialog.categoryClasses:
				gui.settingsDialogs.NVDASettingsDialog.categoryClasses.remove(settingsDialog.SpecialCharacterSettingsPanel)
		except ValueError:
			pass
		super(GlobalPlugin, self).terminate()

