from __future__ import absolute_import
import __init__

import wx, os, sys, platform, types

from gui import validators
from util import profile

def main():
	app = wx.App(False)
	mainWindow()
	app.MainLoop()

class configWindowBase(wx.Frame):
	"A base class for configuration dialogs. Handles creation of settings, and popups"
	def __init__(self, title):
		super(configWindowBase, self).__init__(None, title=title)
		
		self.settingControlList = []
		
		#Create the popup window
		self.popup = wx.PopupWindow(self, flags=wx.BORDER_SIMPLE)
		self.popup.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_INFOBK))
		self.popup.setting = None
		self.popup.text = wx.StaticText(self.popup, -1, '');
		self.popup.sizer = wx.BoxSizer()
		self.popup.sizer.Add(self.popup.text, flag=wx.EXPAND|wx.ALL, border=1)
		self.popup.SetSizer(self.popup.sizer)
	
	def CreateConfigTab(self, nb, name):
		leftConfigPanel, rightConfigPanel, configPanel = self.CreateConfigPanel(nb)
		nb.AddPage(configPanel, name)
		return leftConfigPanel, rightConfigPanel
	
	def CreateConfigPanel(self, parent):
		configPanel = wx.Panel(parent);
		leftConfigPanel = wx.Panel(configPanel)
		rightConfigPanel = wx.Panel(configPanel)
		sizer = wx.GridBagSizer(2, 2)
		leftConfigPanel.SetSizer(sizer)
		sizer = wx.GridBagSizer(2, 2)
		rightConfigPanel.SetSizer(sizer)
		sizer = wx.BoxSizer(wx.HORIZONTAL)
		configPanel.SetSizer(sizer)
		sizer.Add(leftConfigPanel)
		sizer.Add(rightConfigPanel)
		leftConfigPanel.main = self
		rightConfigPanel.main = self
		return leftConfigPanel, rightConfigPanel, configPanel

	def OnPopupDisplay(self, setting):
		self.popup.setting = setting
		self.UpdatePopup(setting)
		self.popup.Show(True)
		
	def OnPopupHide(self, e):
		self.popup.Show(False)
	
	def UpdatePopup(self, setting):
		if self.popup.setting == setting:
			if setting.validationMsg != '':
				self.popup.text.SetLabel(setting.validationMsg + '\n\n' + setting.helpText)
			else:
				self.popup.text.SetLabel(setting.helpText)
			self.popup.text.Wrap(350)
			self.popup.Fit()
			if os.name == 'darwin':
				x, y = self.ClientToScreenXY(0, 0)
				sx, sy = self.GetClientSizeTuple()
			else:
				x, y = setting.ctrl.ClientToScreenXY(0, 0)
				sx, sy = setting.ctrl.GetSizeTuple()
			#if platform.system() == "Windows":
			#	for some reason, under windows, the popup is relative to the main window... in some cases. (Wierd ass bug)
			#	wx, wy = self.ClientToScreenXY(0, 0)
			#	x -= wx
			#	y -= wy
			self.popup.SetPosition((x, y+sy))
	
	def updateProfileToControls(self):
		"Update the configuration wx controls to show the new configuration settings"
		for setting in self.settingControlList:
			if setting.type == 'profile':
				setting.SetValue(profile.getProfileSetting(setting.configName))
			else:
				setting.SetValue(profile.getPreference(setting.configName))

class TitleRow():
	def __init__(self, panel, name):
		"Add a title row to the configuration panel"
		sizer = panel.GetSizer()
		x = sizer.GetRows()
		self.title = wx.StaticText(panel, -1, name)
		self.title.SetFont(wx.Font(wx.SystemSettings.GetFont(wx.SYS_ANSI_VAR_FONT).GetPointSize(), wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.FONTWEIGHT_BOLD))
		sizer.Add(self.title, (x,0), (1,3), flag=wx.EXPAND)
		sizer.Add(wx.StaticLine(panel), (x+1,0), (1,3), flag=wx.EXPAND)
		sizer.SetRows(x + 2)

class SettingRow():
	def __init__(self, panel, label, configName, defaultValue = '', helpText = 'Help: TODO', type = 'profile'):
		"Add a setting to the configuration panel"
		sizer = panel.GetSizer()
		x = sizer.GetRows()
		y = 0
		
		self.validators = []
		self.validationMsg = ''
		self.helpText = helpText
		self.configName = configName
		self.panel = panel
		self.type = type
		
		self.label = wx.StaticText(panel, -1, label)
		getSettingFunc = profile.getPreference
		if self.type == 'profile':
			getSettingFunc = profile.getProfileSetting
		if isinstance(defaultValue, types.StringTypes):
			self.ctrl = wx.TextCtrl(panel, -1, getSettingFunc(configName))
			self.ctrl.Bind(wx.EVT_TEXT, self.OnSettingChange)
		elif isinstance(defaultValue, types.BooleanType):
			self.ctrl = wx.CheckBox(panel, -1, style=wx.ALIGN_RIGHT)
			self.SetValue(getSettingFunc(configName))
			self.ctrl.Bind(wx.EVT_CHECKBOX, self.OnSettingChange)
		else:
			self.ctrl = wx.ComboBox(panel, -1, getSettingFunc(configName), choices=defaultValue, style=wx.CB_DROPDOWN|wx.CB_READONLY)
			self.ctrl.Bind(wx.EVT_COMBOBOX, self.OnSettingChange)

		sizer.Add(self.label, (x,y), flag=wx.ALIGN_CENTER_VERTICAL)
		sizer.Add(self.ctrl, (x,y+1), flag=wx.ALIGN_BOTTOM|wx.EXPAND)
		sizer.SetRows(x+1)
		
		if os.name == 'darwin':
			self.ctrl.Bind(wx.EVT_SET_FOCUS, self.OnMouseEnter)
			self.ctrl.Bind(wx.EVT_KILL_FOCUS, self.OnMouseExit)
		else:
			self.ctrl.Bind(wx.EVT_ENTER_WINDOW, self.OnMouseEnter)
			self.ctrl.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseExit)
		
		self.defaultBGColour = self.ctrl.GetBackgroundColour()
		
		panel.main.settingControlList.append(self)

	def OnMouseEnter(self, e):
		self.panel.main.OnPopupDisplay(self)

	def OnMouseExit(self, e):
		self.panel.main.OnPopupHide(self)

	def OnSettingChange(self, e):
		if self.type == 'profile':
			profile.putProfileSetting(self.configName, self.GetValue())
		else:
			profile.putPreference(self.configName, self.GetValue())
		result = validators.SUCCESS
		msgs = []
		for validator in self.validators:
			res, err = validator.validate()
			if res == validators.ERROR:
				result = res
			elif res == validators.WARNING and result != validators.ERROR:
				result = res
			if res != validators.SUCCESS:
				msgs.append(err)
		if result == validators.ERROR:
			self.ctrl.SetBackgroundColour('Red')
		elif result == validators.WARNING:
			self.ctrl.SetBackgroundColour('Yellow')
		else:
			self.ctrl.SetBackgroundColour(self.defaultBGColour)
		self.ctrl.Refresh()

		self.validationMsg = '\n'.join(msgs)
		self.panel.main.UpdatePopup(self)

	def GetValue(self):
		return str(self.ctrl.GetValue())

	def SetValue(self, value):
		if isinstance(self.ctrl, wx.CheckBox):
			self.ctrl.SetValue(str(value) == "True")
		else:
			self.ctrl.SetValue(value)

#Settings notify works as a validator, but instead of validating anything, it calls another function, which can use the value.
# A bit hacky, bit it works.
class settingNotify():
	def __init__(self, setting, func):
		self.setting = setting
		self.setting.validators.append(self)
		self.func = func
	
	def validate(self):
		try:
			f = float(self.setting.GetValue())
			self.func(f)
			return validators.SUCCESS, ''
		except ValueError:
			self.func()
			return validators.SUCCESS, ''
