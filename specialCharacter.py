# Special Character Add-on for NVDA
# Copyright (C) 2025 ['chai chaimee']
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

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
    scriptCategory = addonHandler.getCodeAddon().manifest["summary"]
    
    def __init__(self):
        super(GlobalPlugin, self).__init__()
        self.enabled = True  # Add-on enable/disable status
        self.active_set = 1  # 1 for set 1, 2 for set 2
        self.last_toggle_time = 0
        self.toggle_count = 0

    def _send(self, char):
        if brailleInputHandler:
            brailleInputHandler.sendChars(char)
        else:
            # If braille input is not available, attempt to insert character directly or via clipboard.
            # char_map is not used here as the intention seems to be sending the character directly.
            try:
                focus = api.getFocusObject()
                if hasattr(focus, 'edit') and hasattr(focus.edit, 'textInsert'):
                    focus.edit.textInsert(char)
                else:
                    api.copyToClip(char)
                    keyboardHandler.KeyboardInputGesture.fromName("control+v").send()
            except Exception:
                ui.message(f"Cannot insert {char}")

    @script(gesture="kb:control+1", description="Insert • or °")
    def script_key1(self, gesture):
        if not self.enabled:
            return gesture.send()
        self._send("•" if self.active_set == 1 else "°")

    @script(gesture="kb:control+2", description="Insert () or ½")
    def script_key2(self, gesture):
        if not self.enabled:
            return gesture.send()
        self._send("()" if self.active_set == 1 else "½")

    @script(gesture="kb:control+3", description="Insert ± or ¼")
    def script_key3(self, gesture):
        if not self.enabled:
            return gesture.send()
        self._send("±" if self.active_set == 1 else "¼")

    @script(gesture="kb:control+4", description="Insert × or ¾")
    def script_key4(self, gesture):
        if not self.enabled:
            return gesture.send()
        self._send("×" if self.active_set == 1 else "¾")

    @script(gesture="kb:control+5", description="Insert ÷ or √")
    def script_key5(self, gesture):
        if not self.enabled:
            return gesture.send()
        self._send("÷" if self.active_set == 1 else "√")

    @script(gesture="kb:control+6", description="Insert ฿ or ′")
    def script_key6(self, gesture):
        if not self.enabled:
            return gesture.send()
        self._send("฿" if self.active_set == 1 else "′")

    @script(gesture="kb:control+7", description="Insert € or ″")
    def script_key7(self, gesture):
        if not self.enabled:
            return gesture.send()
        self._send("€" if self.active_set == 1 else "″")

    @script(gesture="kb:control+8", description="Insert £ or µ")
    def script_key8(self, gesture):
        if not self.enabled:
            return gesture.send()
        self._send("£" if self.active_set == 1 else "µ")

    @script(gesture="kb:control+9", description="Insert ¢ or ¥")
    def script_key9(self, gesture):
        if not self.enabled:
            return gesture.send()
        self._send("¢" if self.active_set == 1 else "¥")

    @script(gesture="kb:control+0", description="Insert © or …")
    def script_key0(self, gesture):
        if not self.enabled:
            return gesture.send()
        self._send("©" if self.active_set == 1 else "…")

    @script(gesture="kb:control+-", description="Insert ® or †")
    def script_key_minus(self, gesture): # Changed function name to be Python-compliant
        if not self.enabled:
            return gesture.send()
        self._send("®" if self.active_set == 1 else "†")

    @script(gesture="kb:control+=", description="Insert ™ or §")
    def script_key_equals(self, gesture): # Changed function name to be Python-compliant
        if not self.enabled:
            return gesture.send()
        self._send("™" if self.active_set == 1 else "§")

    @script(gesture="kb:shift+windows+.", description="Insert –")
    def script_shiftWinDot(self, gesture):
        if not self.enabled:
            return gesture.send()
        self._send("–")

    @script(gesture="kb:shift+windows+/", description="Insert —")
    def script_shiftWinSlash(self, gesture):
        if not self.enabled:
            return gesture.send()
        self._send("—")

    # Script for Control + Backspace to toggle character set or add-on enable/disable
    @script(gesture="kb:control+backspace", description="Toggle character set or add-on")
    def script_toggleAddon(self, gesture):
        current_time = time.time()
        # Detect double press within 500 milliseconds
        if current_time - self.last_toggle_time < 0.5:
            self.toggle_count += 1
        else:
            self.toggle_count = 1
        self.last_toggle_time = current_time

        # Schedule processing of the press (to differentiate single vs. double press)
        if self.toggle_count == 1:
            wx.CallLater(500, self._process_toggle)

    def _process_toggle(self):
        if self.toggle_count == 1:  # Single press: toggle character set
            self.active_set = 2 if self.active_set == 1 else 1
            ui.message(f"Switched set {self.active_set}")
        elif self.toggle_count >= 2:  # Double press or more: enable/disable add-on
            self.enabled = not self.enabled
            state = "on" if self.enabled else "off"
            ui.message(f"Special Character {state}")
        self.toggle_count = 0 # Reset press counter
