# -*- coding: UTF-8 -*-

# installTasks for the urlShortener add-on
# Copyright (C) 2023 Noelia Ruiz Martínez, other contributors
# Released under GPL2

import os
import shutil
import glob

import addonHandler
import globalVars

ADDON_DIR = os.path.abspath(os.path.dirname(__file__))
URLS_PATH = os.path.join(ADDON_DIR, "globalPlugins", "urlShortener")
CONFIG_PATH = globalVars.appArgs.configPath

addonHandler.initTranslation()


def onInstall():
	previousUrlsPath = os.path.join(
		CONFIG_PATH, "addons", "urlShortener",
		"globalPlugins", "urlShortener"
	)
	if os.path.isdir(previousUrlsPath):
		validFiles = glob.glob(previousUrlsPath + "\\*.json")
		if not os.path.isdir(URLS_PATH):
			os.makedirs(URLS_PATH)
		for file in validFiles:
			try:
				shutil.copy(file, URLS_PATH)
			except Exception:
				pass
