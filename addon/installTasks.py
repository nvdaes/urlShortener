# -*- coding: UTF-8 -*-

# installTasks for the urlShortener add-on
# Copyright (C) 2023 Noelia Ruiz Martínez, other contributors
# Released under GPL2

import os
import shutil
import glob

import globalVars

ADDON_DIR = os.path.abspath(os.path.dirname(__file__))
URL_PATH = os.path.join(ADDON_DIR, "globalPlugins", "urlShortener")
CONFIG_PATH = globalVars.appArgs.configPath


def onInstall():
	previousUrlPath = os.path.join(
		CONFIG_PATH, "addons", "urlShortener",
		"globalPlugins", "urlShortener"
	)
	if os.path.isdir(previousUrlPath):
		validFiles = glob.glob(previousUrlPath + "\\url.json")
		if not os.path.isdir(URL_PATH):
			os.makedirs(URL_PATH)
		for file in validFiles:
			try:
				shutil.copy(file, URL_PATH)
			except IOError:
				pass
