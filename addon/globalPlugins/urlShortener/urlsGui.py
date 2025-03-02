# -*- coding: UTF-8 -*-

# URL Shortener: Plugin to shorten URLs with NVDA
# Copyright (C) 2023-2025 Noelia Ruiz Martínez
# Released under GPL 2

import json
import os
import re
import shutil
import wx

from dataclasses import asdict

import addonHandler
import api
import globalVars
import ui
from logHandler import log
from gui import guiHelper
from gui.message import MessageDialog, ReturnCode

from .isGd import IsGd, UrlMetadata
from .skipTranslation import translate

addonHandler.initTranslation()

CONFIG_PATH = globalVars.appArgs.configPath
ADDON_CONFIG_PATH = os.path.join(CONFIG_PATH, "urlShortener")
URLS_PATH = os.path.join(ADDON_CONFIG_PATH, "urls.json")


def getUrlMetadataName(urlMetadata):
	return urlMetadata.name


class UrlsDialog(wx.Dialog):
	_instance = None

	def __new__(cls, *args, **kwargs):
		# Make this a singleton.
		if UrlsDialog._instance is None:
			return super(UrlsDialog, cls).__new__(cls, *args, **kwargs)
		return UrlsDialog._instance

	def __init__(self, parent):
		if UrlsDialog._instance is not None:
			return
		UrlsDialog._instance = self
		self._urls = []
		jsonUrls = []
		try:
			with open(URLS_PATH, "rt") as f:
				jsonUrls = json.load(f)
			for url in jsonUrls:
				self._urls.append(UrlMetadata(**url))
			self._urls.sort(key=getUrlMetadataName)
		except Exception as e:
			self._urls = [
				UrlMetadata("example.com", "example.com", "https://is.gd/iKpnPV")
			]
			log.debugWarning(f"Could not open URLs file: {e}")
		super().__init__(
			parent,
			# Translators: The title of a dialog.
			title=_("urls"),
		)

		mainSizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		# Translators: Label of a dialog (message translated in NVDA's core in different contexts).
		searchTextLabel = _("&Filter by:")
		self.searchTextEdit = sHelper.addLabeledControl(searchTextLabel, wx.TextCtrl)
		self.searchTextEdit.Bind(wx.EVT_TEXT, self.onSearchEditTextChange)

		urlsListGroupSizer = wx.StaticBoxSizer(wx.StaticBox(self), wx.HORIZONTAL)
		urlsListGroupContents = wx.BoxSizer(wx.HORIZONTAL)
		changeUrlsSizer = wx.BoxSizer(wx.VERTICAL)
		self.choices = []
		for item in self._urls:
			self.choices.append(item.name)

		self.filteredItems = []
		for n in range(len(self.choices)):
			self.filteredItems.append(n)
		self.urlsList = wx.ListBox(
			self,
			choices=self.choices,
		)
		self.urlsList.Selection = 0
		self.urlsList.Bind(wx.EVT_LISTBOX, self.onUrlsListChoice)

		changeUrlsSizer.Add(self.urlsList, proportion=1)
		changeUrlsSizer.AddSpacer(guiHelper.SPACE_BETWEEN_BUTTONS_VERTICAL)
		urlsListGroupContents.Add(changeUrlsSizer, flag=wx.EXPAND)
		urlsListGroupContents.AddSpacer(
			guiHelper.SPACE_BETWEEN_ASSOCIATED_CONTROL_HORIZONTAL
		)

		buttonHelper = guiHelper.ButtonHelper(wx.VERTICAL)

		# Translators: The label of a button to copy the URL.
		self.copyButton = buttonHelper.addButton(self, label=_("C&opy shortened URL"))
		self.AffirmativeId = self.copyButton.Id
		self.copyButton.SetDefault()
		self.copyButton.Bind(wx.EVT_BUTTON, self.onCopy)

		# Translators: The label of an edit box to show more details about the selected URL.
		detailsLabel = _("Deta&ils:")
		detailsLabeledCtrl = guiHelper.LabeledControlHelper(
			self,
			detailsLabel,
			wx.TextCtrl,
			style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_DONTWRAP,
		)
		self.detailsEdit = detailsLabeledCtrl.control

		# Translators: The label of a field to enter an address for a new shortened URL.
		urlLabelText = _("New &URL")
		self.urlTextCtrl = sHelper.addLabeledControl(urlLabelText, wx.TextCtrl)
		self.urlTextCtrl.Bind(wx.EVT_TEXT, self.onUrlTextCtrlChange)

		# Translators: The label of a field to enter the name for a new URL.
		nameLabelText = _("&Name for new URL")
		self.nameTextCtrl = sHelper.addLabeledControl(nameLabelText, wx.TextCtrl)

		# Translators: The label of a field to enter a custom URL.
		customUrlLabelText = _("Cus&tom URL")
		self.customUrlTextCtrl = sHelper.addLabeledControl(
			customUrlLabelText, wx.TextCtrl
		)

		# Translators: The label of a button to add a new URL.
		self.newButton = buttonHelper.addButton(self, label=_("Short&en New URL"))
		self.newButton.Bind(wx.EVT_BUTTON, self.onNew)
		self.newButton.Disable()

		# Translators: The label of a button to rename an URL.
		self.renameButton = buttonHelper.addButton(self, label=_("&Rename..."))
		self.renameButton.Bind(wx.EVT_BUTTON, self.onRename)

		# Translators: The label of a button to delete an URL.
		self.deleteButton = buttonHelper.addButton(self, label=_("&Delete..."))
		self.deleteButton.Bind(wx.EVT_BUTTON, self.onDelete)

		self.removeSettingsButton = buttonHelper.addButton(
			# Translators: The label of a button to delete settings folder.
			self, label=_("Remove &saved URLs...")
		)
		self.removeSettingsButton.Bind(wx.EVT_BUTTON, self.onRemoveSettings)

		urlsListGroupContents.Add(buttonHelper.sizer)
		urlsListGroupSizer.Add(
			urlsListGroupContents, border=guiHelper.BORDER_FOR_DIALOGS, flag=wx.ALL
		)
		sHelper.addItem(urlsListGroupSizer)

		# Message translated in NVDA core.
		closeButton = wx.Button(self, wx.ID_CLOSE, label=translate("&Close"))
		closeButton.Bind(wx.EVT_BUTTON, lambda evt: self.Close())
		sHelper.addDialogDismissButtons(closeButton)
		self.Bind(wx.EVT_CLOSE, self.onClose)
		self.EscapeId = wx.ID_CLOSE

		self.onUrlsListChoice(None)
		mainSizer.Add(sHelper.sizer, flag=wx.ALL, border=guiHelper.BORDER_FOR_DIALOGS)
		mainSizer.Fit(self)
		self.Sizer = mainSizer
		self.urlsList.SetFocus()
		self.CentreOnScreen()

	def __del__(self):
		UrlsDialog._instance = None

	def shortenUrl(self, address, customUrl):
		name = self.nameTextCtrl.GetValue()
		if not name:
			name = address
		originalUrls = [url.originalUrl for url in self._urls]
		customUrls = [url.shortenedUrl.split("/")[-1] for url in self._urls]
		if address in originalUrls:
			# Translators: Message presented when an URL was already saved.
			ui.message(_("This URL was already saved."))
			self.urlsList.SetFocus()
			return
		if customUrl in customUrls:
			# Translators: Message presented when a custom URL is already saved.
			ui.message(_("This custom URL was already used. Try a different one."))
			self.customUrlTextCtrl.SetFocus()
			return
		if customUrl and (len(customUrl) < 5 or len(customUrl) > 30):
			ui.message(
				# Translators: Message presented when a custom URL has a wrong length.
				_("This custom URL has %d characters. Length must be between 5 and 30.")
				% len(customUrl)
			)
			self.customUrlTextCtrl.SetFocus()
			return
		try:
			url = IsGd(address, customUrl).getShortenedUrl()
			if not url:
				if customUrl:
					ui.message(
						# Translators: Message presented when a custom URL cannot be added.
						_("This custom URL is not available. Try a different one.")
					)
					self.customUrlTextCtrl.SetFocus()
				else:
					# Translators: Message presented when an URL cannot be shortened.
					ui.message(_("Cannot shorten URL. Check Internet connectivity."))
					self.urlTextCtrl.SetFocus()
				return
		except Exception as e:
			wx.CallAfter(
				MessageDialog.alert,
				# Translators: Message presented when a shortened URL cannot be added.
				_("Cannot add URL: %s" % e),
				# Translators: Error message.
				_("Error"),
			)
			raise e
		urlMetadata = UrlMetadata(name, address, url)
		self._urls.append(urlMetadata)
		jsonUrls = [asdict(url) for url in self._urls]
		if not os.path.isdir(ADDON_CONFIG_PATH):
			os.makedirs(ADDON_CONFIG_PATH)
		try:
			with open(URLS_PATH, "wt") as f:
				json.dump(jsonUrls, f, indent="\t")
		except Exception as e:
			raise e
		self.urlsList.Append(name)
		self.choices.append(name)
		newItem = self.filteredItems[-1] + 1
		self.filteredItems.append(newItem)
		self.urlsList.Selection = self.urlsList.Count - 1
		self.onUrlsListChoice(None)
		self.urlsList.SetFocus()
		self.urlTextCtrl.SetValue("")
		self.nameTextCtrl.SetValue("")
		self.customUrlTextCtrl.SetValue("")

	def onSearchEditTextChange(self, evt):
		self.urlsList.Clear()
		self.filteredItems = []
		# Based on the filter of the Input gestures dialog of NVDA's core.
		filter = self.searchTextEdit.Value
		if filter:
			filter = re.escape(filter)
			filterReg = re.compile(
				r"(?=.*?" + r")(?=.*?".join(filter.split(r"\ ")) + r")",
				re.U | re.IGNORECASE,
			)
		for index, choice in enumerate(self.choices):
			if filter and not filterReg.match(choice):
				continue
			self.filteredItems.append(index)
			self.urlsList.Append(choice)
		if len(self.filteredItems) >= 1:
			self.urlsList.Selection = 0
			self.onUrlsListChoice(None)

	def onUrlsListChoice(self, evt):
		self.urlsList.Enable()
		self.sel = self.urlsList.Selection
		self.stringSel = self.urlsList.GetString(self.sel)
		url = self._urls[self.filteredItems[self.sel]]
		urlInfo = _(
			# Translators: Info about the selected URL.
			"Original URL: {}\n" "Name: {}\n" "Shortened URL: {}".format(
				url.originalUrl,
				url.name,
				url.shortenedUrl,
			),
		)
		self.detailsEdit.Value = urlInfo
		self.renameButton.Enabled = self.sel >= 0
		self.deleteButton.Enabled = self.sel >= 0 and self.urlsList.Count > 1
		self.removeSettingsButton.Enabled = os.path.isdir(ADDON_CONFIG_PATH)

	def onCopy(self, evt):
		shortenUrl = self._urls[self.filteredItems[self.sel]].shortenedUrl
		if api.copyToClip(shortenUrl):
			# Translators: Message presented when the selected URL has been copied.
			ui.message(_("Copied"))
		self.urlsList.SetFocus()

	def onUrlTextCtrlChange(self, evt):
		urlToShorten = self.urlTextCtrl.Value
		if urlToShorten:
			self.newButton.Enable()
		else:
			self.newButton.Disable()

	def onNew(self, evt):
		address = self.urlTextCtrl.GetValue()
		customUrl = self.customUrlTextCtrl.GetValue()
		self.shortenUrl(address, customUrl)

	def onDelete(self, evt):
		url = self._urls[self.filteredItems[self.sel]]
		if (
			MessageDialog.ask(
				# Translators: The confirmation prompt displayed when the user requests to delete an URL.
				_("Are you sure you want to delete this URL: %s?") % url.name,
				# Message translated in NVDA core.
				translate("Confirm Deletion"),
				self,
			)
			== ReturnCode.NO
		):
			self.urlsList.SetFocus()
			return

		del self._urls[self.filteredItems[self.sel]]
		jsonUrls = [asdict(url) for url in self._urls]
		if not os.path.isdir(ADDON_CONFIG_PATH):
			os.makedirs(ADDON_CONFIG_PATH)
		try:
			with open(URLS_PATH, "wt") as f:
				json.dump(jsonUrls, f, indent="\t")
		except Exception as e:
			raise e
		del self.choices[self.filteredItems[self.sel]]
		self.filteredItems = []
		self.urlsList.Clear()
		for choice in self.choices:
			self.urlsList.Append(choice)
		for n in range(len(self.choices)):
			self.filteredItems.append(n)
		self.urlsList.Selection = 0
		self.onUrlsListChoice(None)
		self.urlsList.SetFocus()

	def onRename(self, evt):
		with wx.TextEntryDialog(
			self,
			# Translators: The label of a field to enter a new name for an URL.
			_("New name:"),
			# Translators: The title of a dialog to rename an URL.
			_("Rename URL"),
			value=self.stringSel,
		) as d:
			if d.ShowModal() == wx.ID_CANCEL or not d.GetValue():
				self.urlsList.SetFocus()
				return
		newName = d.GetValue()
		self._urls[self.filteredItems[self.sel]].name = newName
		jsonUrls = [asdict(url) for url in self._urls]
		if not os.path.isdir(ADDON_CONFIG_PATH):
			os.makedirs(ADDON_CONFIG_PATH)
		try:
			with open(URLS_PATH, "wt") as f:
				json.dump(jsonUrls, f, indent="\t")
		except Exception as e:
			raise e
		self.urlsList.SetString(self.sel, newName)
		self.choices[self.filteredItems[self.sel]] = newName
		self.onUrlsListChoice(None)
		self.urlsList.SetFocus()

	def onRemoveSettings(self, evt):
		if (
			MessageDialog.ask(
				# Translators: The confirmation prompt displayed when the user requests to delete saved URLs.
				_("Are you sure you want to delete your saved URLs?"),
				# Message translated in NVDA core.
				translate("Confirm Deletion"),
				self,
			)
			== ReturnCode.NO
		):
			self.urlsList.SetFocus()
			return
		shutil.rmtree(ADDON_CONFIG_PATH, ignore_errors=True)
		self.onUrlsListChoice(None)
		self.urlsList.SetFocus()

	def onClose(self, evt):
		self.Destroy()
		UrlsDialog._instance = None
