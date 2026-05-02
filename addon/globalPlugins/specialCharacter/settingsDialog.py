# settingsDialog.py

import wx
import gui
import addonHandler
import ui
from gui.settingsDialogs import SettingsPanel
from . import config
import gettext

# Initialize translation function for this module
addonHandler.initTranslation()
_ = gettext.gettext

class SpecialCharacterSettingsPanel(SettingsPanel):
	"""
	A settings panel for configuring special characters for set 1 and set 2.
	"""
	title = _("Special Character Settings")

	def makeSettings(self, settingsSizer):
		"""Create the settings controls."""
		self.controls = {}
		
		# Add a note about the save location (updated to reflect new subfolder)
		note = wx.StaticText(self, label=_("Configuration is stored in specialCharacters.json in the ChaiChaimee subfolder of NVDA user config folder."))
		settingsSizer.Add(note, flag=wx.ALL | wx.EXPAND, border=10)
		
		# Set selection Combo Box
		set_sizer = wx.BoxSizer(wx.HORIZONTAL)
		set_label = wx.StaticText(self, label=_("Select Character Set:"))
		set_sizer.Add(set_label, flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=5)

		self.set_combo = wx.ComboBox(self, choices=[_("Set 1"), _("Set 2")], style=wx.CB_READONLY)
		self.set_combo.SetSelection(0) # Default to Set 1
		set_sizer.Add(self.set_combo)
		
		self.set_combo.Bind(wx.EVT_COMBOBOX, self.on_set_change)
		
		settingsSizer.Add(set_sizer, flag=wx.ALL, border=10)

		# Character Edit Fields Grid
		self.grid_sizer = wx.FlexGridSizer(rows=12, cols=2, vgap=5, hgap=5)
		self.grid_sizer.AddGrowableCol(1)
		
		# The key names are the same as in config.py
		self.key_gestures = [
			"ctrl+1", "ctrl+2", "ctrl+3", "ctrl+4", "ctrl+5", "ctrl+6",
			"ctrl+7", "ctrl+8", "ctrl+9", "ctrl+0", "ctrl+-", "ctrl+=",
		]

		# Use translatable strings without colon here
		self.slot_names_base = [
			_("Slot 1"), _("Slot 2"), _("Slot 3"), _("Slot 4"), _("Slot 5"), _("Slot 6"),
			_("Slot 7"), _("Slot 8"), _("Slot 9"), _("Slot 0"), _("Slot -"), _("Slot ="),
		]
		
		for i, key in enumerate(self.key_gestures):
			# FIXED: Concatenate translated string with a literal colon. This is safer.
			label_text = self.slot_names_base[i] + ":"
			label = wx.StaticText(self, label=label_text)
			self.grid_sizer.Add(label, flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border=10)
			
			edit = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
			self.grid_sizer.Add(edit, flag=wx.EXPAND)
			self.controls[key] = edit
			
		settingsSizer.Add(self.grid_sizer, flag=wx.ALL | wx.EXPAND, border=10)

		# Load initial values
		self.active_set = 1
		self.load_set_values(self.active_set)

	def load_set_values(self, set_num):
		"""Loads values from the config into the edit fields for the current set."""
		for key in self.key_gestures:
			char_value = config.get_char(key, set_num)
			self.controls[key].SetValue(char_value)
			
	def save_current_set_values(self):
		"""Saves current values from edit fields back into the config."""
		for key in self.key_gestures:
			config.set_char(key, self.active_set, self.controls[key].GetValue())

	def on_set_change(self, evt):
		"""Handles changing between Set 1 and Set 2."""
		# Save the current set's values first
		self.save_current_set_values()
		
		# Change the active set
		self.active_set = self.set_combo.GetSelection() + 1
		
		# Load the new set's values
		self.load_set_values(self.active_set)
		
	def onSave(self):
		"""Saves the configuration when OK is pressed."""
		# Save the currently displayed set's values
		self.save_current_set_values()
		
		# Save the configuration to file
		if config.update_and_save_config(config.special_characters):
			ui.message(_("Special character settings saved successfully"))
		else:
			ui.message(_("Error saving special character settings"))

	def postInit(self):
		"""Called after the dialog is initialized."""
		self.set_combo.SetFocus()