# -*- coding: UTF-8 -*-

# Link Shortener: Plugin to shorten URLs with NVDA
# Copyright (C) 2023 Noelia Ruiz Martínez
# Released under GPL 2

import os
import pickle
import re
import wx

import api
import gui
from gui import guiHelper

from .isGd import IsGd, UrlMetadata
from .skipTranslation import translate

URLS_PATH = os.path.join(os.path.dirname(__file__), "urls.pickle")


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
		try:
			with open(URLS_PATH, "rb") as f:
				self._urls = pickle.load(f)
		except Exception:
			self._urls = [UrlMetadata("example.com", "example.com", "https://is.gd/iKpnPV")]

		super(UrlsDialog, self).__init__(
			# Translators: Title of a dialog.
			parent, title=_("urls")
		)

		mainSizer = wx.BoxSizer(wx.VERTICAL)
		sHelper = guiHelper.BoxSizerHelper(self, orientation=wx.VERTICAL)
		# Translators: Label of a dialog (message translated in NVDA's core in different contexts).
		searchTextLabel = _("&Filter by:")
		self.searchTextEdit = sHelper.addLabeledControl(searchTextLabel, wx.TextCtrl)

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
			self, choices=self.choices
		)
		self.urlsList.Selection = 0
		self.urlsList.Bind(wx.EVT_LISTBOX, self.onUrlsListChoice)

		changeUrlsSizer.Add(self.urlsList, proportion=1.0)
		changeUrlsSizer.AddSpacer(guiHelper.SPACE_BETWEEN_BUTTONS_VERTICAL)

		urlsListGroupContents.Add(changeUrlsSizer, flag=wx.EXPAND)
		urlsListGroupContents.AddSpacer(guiHelper.SPACE_BETWEEN_ASSOCIATED_CONTROL_HORIZONTAL)

		self.searchTextEdit.Bind(wx.EVT_TEXT, self.onSearchEditTextChange)

		buttonHelper = guiHelper.ButtonHelper(wx.VERTICAL)

		# Translators: The label of a button to copy the URL.
		self.copyButton = buttonHelper.addButton(self, label=_("&Copy shortened URL..."))
		self.copyButton.Bind(wx.EVT_BUTTON, self.onCopy)

		# Translators: The label of a button to add a new URL.
		newButton = buttonHelper.addButton(self, label=_("&New..."))
		newButton.Bind(wx.EVT_BUTTON, self.onNew)

		# Translators: The label of a button to rename an URL entry.
		self.renameButton = buttonHelper.addButton(self, label=_("&Rename..."))
		self.renameButton.Bind(wx.EVT_BUTTON, self.onRename)

		# Translators: The label of a button to delete an URL.
		self.deleteButton = buttonHelper.addButton(self, label=_("&Delete..."))
		self.deleteButton.Bind(wx.EVT_BUTTON, self.onDelete)

		urlsListGroupContents.Add(buttonHelper.sizer)
		urlsListGroupSizer.Add(urlsListGroupContents, border=guiHelper.BORDER_FOR_DIALOGS, flag=wx.ALL)
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

	def shortenUrl(self, address):
		try:
			url = IsGd(address).getShortenedUrl()
		except Exception as e:
			wx.CallAfter(
				gui.messageBox,
				# Translators: Message presented when a shortened URL cannot be added.
				_('Cannot add URL: %s' % e),
				# Translators: error message.
				_("Error"),
				wx.OK | wx.ICON_ERROR
			)
			raise e
		urlMetadata = UrlMetadata(address, address, url)
		return urlMetadata

	def onSearchEditTextChange(self, evt):
		self.urlsList.Clear()
		self.filteredItems = []
		# Based on the filter of the Input gestures dialog of NVDA's core.
		filter = self.searchTextEdit.Value
		if filter:
			filter = re.escape(filter)
			filterReg = re.compile(r"(?=.*?" + r")(?=.*?".join(filter.split(r"\ ")) + r")", re.U | re.IGNORECASE)
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
		self.renameButton.Enabled = self.sel >= 0
		self.deleteButton.Enabled = (self.sel >= 0 and self.urlsList.Count > 1)

	def onCopy(self, evt):
		if gui.messageBox(
			# Translators: the label of a message box dialog.
			_("Do you want to copy shortened URL to the clipboard?"),
			# Translators: the title of a message box dialog.
			_("Copy shortened URL"),
			wx.YES | wx.NO | wx.CANCEL | wx.ICON_QUESTION
		) == wx.YES:
			shortenUrl = self._urls[self.filteredItems[self.sel]].shortenedUrl
			api.copyToClip(shortenUrl)
			self.urlsList.SetFocus()

	def onNew(self, evt):
		# Translators: The label of a field to enter an address for a new shortened URL.
		with wx.TextEntryDialog(
			# Translators: Label of a dialog.
			self, _("URL to shorten"),
			# Translators: The title of a dialog to shorten an URL.
			_("Shorten URL")
		) as d:
			if d.ShowModal() == wx.ID_CANCEL:
				self.urlsList.SetFocus()
				return
		originalUrls = [url.name for url in self._urls]
		if d.Value in originalUrls:
			self.urlsList.SetFocus()
			return
		urlMetadata = self.shortenUrl(d.Value)
		self._urls.append(urlMetadata)
		self._urls.sort(key=getUrlMetadataName)
		try:
			with open(URLS_PATH, "wb") as f:
				pickle.dump(self._urls, f, protocol=0)
		except Exception as e:
			raise e
		name = urlMetadata.name
		self.urlsList.Append(name)
		self.choices.append(name)
		newItem = self.filteredItems[-1] + 1
		self.filteredItems.append(newItem)
		self.urlsList.Selection = self.urlsList.Count - 1
		self.onUrlsListChoice(None)
		self.urlsList.SetFocus()

	def onDelete(self, evt):
		if gui.messageBox(
			# Translators: The confirmation prompt displayed when the user requests to delete an URL.
			_("Are you sure you want to delete this URL? This cannot be undone."),
			# Message translated in NVDA core.
			translate("Confirm Deletion"),
			wx.YES | wx.NO | wx.ICON_QUESTION, self
		) == wx.NO:
			self.urlsList.SetFocus()
			return
		del self._urls[self.filteredItems[self.sel]]
		try:
			with open(URLS_PATH, "wb") as f:
				pickle.dump(self._urls, f, protocol=0)
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
			# Translators: The label of a field to enter a new name for an URL.
			self, _("New name:"),
			# Translators: The title of a dialog to rename an URL.
			_("Rename URL"), value=self.stringSel
		) as d:
			if d.ShowModal() == wx.ID_CANCEL or not d.Value:
				self.urlsList.SetFocus()
				return
		newName = d.Value
		self._urls[self.filteredItems[self.sel]].name = newName
		try:
			with open(URLS_PATH, "wb") as f:
				pickle.dump(self._urls, f, protocol=0)
		except Exception as e:
			raise e
		self.urlsList.SetString(self.sel, newName)
		self.choices[self.filteredItems[self.sel]] = newName
		self.onUrlsListChoice(None)
		self.urlsList.SetFocus()

	def onClose(self, evt):
		self.Destroy()
		UrlsDialog._instance = None
