# -*- coding: UTF-8 -*-

# URL Shortener: Plugin to shorten URLs with NVDA
# Copyright (C) 2023 Noelia Ruiz Martínez
# Released under GPL 2

import wx

import globalPluginHandler
import globalVars
from scriptHandler import script
import gui
import addonHandler

from .urlsGui import UrlsDialog

addonHandler.initTranslation()

ADDON_SUMMARY = addonHandler.getCodeAddon().manifest["summary"]


def disableInSecureMode(decoratedCls):
	if globalVars.appArgs.secure:
		return globalPluginHandler.GlobalPlugin
	return decoratedCls


@disableInSecureMode
class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	scriptCategory = ADDON_SUMMARY

	def __init__(self):
		super().__init__()
		self.toolsMenu = gui.mainFrame.sysTrayIcon.toolsMenu
		# Translators: the name of a menu item.
		self.urlsListItem = self.toolsMenu.Append(wx.ID_ANY, _("&Shorten URL..."))
		gui.mainFrame.sysTrayIcon.Bind(
			wx.EVT_MENU,
			self.onShortenUrl,
			self.urlsListItem,
		)

	def terminate(self):
		try:
			self.toolsMenu.Remove(self.urlsListItem)
		except Exception:
			pass

	def onShortenUrl(self, evt):
		gui.mainFrame.prePopup()
		d = UrlsDialog(gui.mainFrame)
		d.Show()
		gui.mainFrame.postPopup()

	@script(
		# Translators: message presented in input mode.
		description=_("Activates the Shorten URL dialog."),
	)
	def script_activateShortenUrlDialog(self, gesture):
		wx.CallAfter(self.onShortenUrl, None)
