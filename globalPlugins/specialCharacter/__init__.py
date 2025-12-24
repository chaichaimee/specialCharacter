# __init__.py

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
from NVDAObjects.IAccessible.winword import WordDocument
from NVDAObjects.UIA import UIA
from . import config
from . import settingsDialog

addonHandler.initTranslation()

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
    scriptCategory = addonHandler.getCodeAddon().manifest["summary"]
    
    def __init__(self):
        super(GlobalPlugin, self).__init__()
        self.enabled = True  # Add-on enable/disable status
        # Active set is stored/managed by the config module now, but we use a local variable for the current session state
        self.active_set = 1  # 1 for set 1, 2 for set 2
        self.last_toggle_time = 0
        self.toggle_count = 0
        # Add settings panel with a slight delay to avoid conflicts with other plugins
        wx.CallAfter(self.registerSettingsPanel)

    def registerSettingsPanel(self):
        """Register the settings panel to avoid conflicts with other plugins."""
        try:
            if settingsDialog.SpecialCharacterSettingsPanel not in gui.settingsDialogs.NVDASettingsDialog.categoryClasses:
                gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(settingsDialog.SpecialCharacterSettingsPanel)
        except Exception as e:
            # Fixed: Remove %s from translatable string
            ui.message(_("Error registering settings panel") + ": %s" % str(e))

    def _send(self, char):
        """
        Sends the character to the current focus object, handling various scenarios.
        """
        try:
            focus = api.getFocusObject()
            app_name = focus.appModule.appName.lower() if hasattr(focus, 'appModule') and hasattr(focus.appModule, 'appName') else ""
            
            # Handle Microsoft Word specifically - use text insertion without clipboard to avoid "paste" announcement
            if app_name == 'winword':
                # Try multiple methods for Word 2024 compatibility
                success = False
                
                # Method 1: Direct text insertion for Word documents
                if hasattr(focus, 'edit') and hasattr(focus.edit, 'textInsert'):
                    try:
                        focus.edit.textInsert(char)
                        success = True
                    except Exception:
                        success = False
                
                # Method 2: Try UIA automation for newer Word versions
                if not success and isinstance(focus, UIA):
                    try:
                        # Try to set value for editable controls
                        if hasattr(focus, 'value'):
                            focus.value = focus.value + char
                            success = True
                    except Exception:
                        success = False
                
                # Method 3: Fallback to clipboard for Word
                if not success:
                    api.copyToClip(char)
                    keyboardHandler.KeyboardInputGesture.fromName("control+v").send()
                    
            # Handle web browsers and other applications
            elif app_name in ('chrome', 'firefox', 'brave', 'edge', 'safari'):
                # Use direct input for specific characters, fallback to clipboard for others
                if char in ('"', '/', '\\', '.', '|'):
                    keyboardHandler.KeyboardInputGesture.fromName(char).send()
                else:
                    api.copyToClip(char)
                    keyboardHandler.KeyboardInputGesture.fromName("control+v").send()
            # Handle braille input
            elif brailleInputHandler:
                brailleInputHandler.sendChars(char)
            else:
                # Try direct text insertion for edit controls
                if hasattr(focus, 'edit') and hasattr(focus.edit, 'textInsert'):
                    focus.edit.textInsert(char)
                else:
                    # Fallback for other applications
                    api.copyToClip(char)
                    keyboardHandler.KeyboardInputGesture.fromName("control+v").send()
        except Exception as e:
            # Fixed: Remove %s from translatable string
            ui.message(_("Cannot insert character") + " %s: %s" % (char, str(e)))

    def _get_char_and_send(self, key_name):
        """Retrieves character from config and sends it."""
        if not self.enabled:
            ui.message(_("Special Character Add-on is currently disabled."))
            return True
        
        # Get the character from the dynamically loaded configuration
        char_to_send = config.get_char(key_name, self.active_set)
        if char_to_send:
            self._send(char_to_send)
        return True # Handled

    # Group 1: Special Characters controlled by config

    @script(gesture="kb:control+1", description=_("Insert Slot 1"))
    def script_key1(self, gesture):
        return self._get_char_and_send("ctrl+1")

    @script(gesture="kb:control+2", description=_("Insert Slot 2"))
    def script_key2(self, gesture):
        return self._get_char_and_send("ctrl+2")

    @script(gesture="kb:control+3", description=_("Insert Slot 3"))
    def script_key3(self, gesture):
        return self._get_char_and_send("ctrl+3")

    @script(gesture="kb:control+4", description=_("Insert Slot 4"))
    def script_key4(self, gesture):
        return self._get_char_and_send("ctrl+4")

    @script(gesture="kb:control+5", description=_("Insert Slot 5"))
    def script_key5(self, gesture):
        return self._get_char_and_send("ctrl+5")

    @script(gesture="kb:control+6", description=_("Insert Slot 6"))
    def script_key6(self, gesture):
        return self._get_char_and_send("ctrl+6")

    @script(gesture="kb:control+7", description=_("Insert Slot 7"))
    def script_key7(self, gesture):
        return self._get_char_and_send("ctrl+7")

    @script(gesture="kb:control+8", description=_("Insert Slot 8"))
    def script_key8(self, gesture):
        return self._get_char_and_send("ctrl+8")

    @script(gesture="kb:control+9", description=_("Insert Slot 9"))
    def script_key9(self, gesture):
        return self._get_char_and_send("ctrl+9")

    @script(gesture="kb:control+0", description=_("Insert Slot 0"))
    def script_key0(self, gesture):
        return self._get_char_and_send("ctrl+0")

    @script(gesture="kb:control+-", description=_("Insert Slot hyphen"))
    def script_key_minus(self, gesture):
        return self._get_char_and_send("ctrl+-")

    @script(gesture="kb:control+=", description=_("Insert Slot equals"))
    def script_key_equals(self, gesture):
        return self._get_char_and_send("ctrl+=")

    # Group 2: Fixed Special Characters (Unchanged)
    
    @script(gesture="kb:shift+windows+|", description=_("Insert vertical bar"))
    def script_shiftWinPipe(self, gesture):
        if not self.enabled:
            ui.message(_("Special Character Add-on is currently disabled."))
            return True
        self._send("|")
        return True

    @script(gesture="kb:shift+windows+.", description=_("Insert –"))
    def script_shiftWinDot(self, gesture):
        if not self.enabled:
            ui.message(_("Special Character Add-on is currently disabled."))
            return True
        self._send("–")
        return True

    @script(gesture="kb:shift+windows+/", description=_("Insert —"))
    def script_shiftWinSlash(self, gesture):
        if not self.enabled:
            ui.message(_("Special Character Add-on is currently disabled."))
            return True
        self._send("—")
        return True

    # Group 3: Toggle Script (Changed gesture)

    @script(gesture="kb:shift+backspace", description=_("Toggle character set or add-on"))
    def script_toggleAddon(self, gesture):
        """
        Single tap: toggle character set (1 or 2).
        Double tap: toggle add-on enable/disable.
        """
        current_time = time.time()
        # Check if this is a potential double-tap (within 0.5 seconds)
        if current_time - self.last_toggle_time < 0.5:
            self.toggle_count += 1
        else:
            self.toggle_count = 1
            
        self.last_toggle_time = current_time

        # Use wx.CallLater to wait and check if a second tap occurs
        if self.toggle_count == 1:
            wx.CallLater(500, self._process_toggle)
        
        return True # Handled

    def _process_toggle(self):
        """Performs the actual toggle based on the number of taps."""
        if self.toggle_count == 1:
            # Single tap: toggle character set
            self.active_set = 2 if self.active_set == 1 else 1
            ui.message(_("Switched set %s") % self.active_set)
        elif self.toggle_count >= 2:
            # Double tap: toggle add-on enable/disable
            self.enabled = not self.enabled
            state = _("on") if self.enabled else _("off")
            ui.message(_("Special Character %s") % state)
            
        # Reset the count after processing
        self.toggle_count = 0

    def terminate(self):
        """Clean-up when the add-on is disabled or NVDA exits."""
        try:
            if settingsDialog.SpecialCharacterSettingsPanel in gui.settingsDialogs.NVDASettingsDialog.categoryClasses:
                gui.settingsDialogs.NVDASettingsDialog.categoryClasses.remove(settingsDialog.SpecialCharacterSettingsPanel)
        except ValueError:
            pass  # Ignore if the panel is not in the list
        super(GlobalPlugin, self).terminate()
