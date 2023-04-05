# -*- coding: UTF-8 -*-

# installTasks for the urlShortener add-on
# Copyright (C) 2023 Noelia Ruiz Martínez, other contributors
# Released under GPL2

import json
import os

import addonHandler
import globalVars

ADDON_DIR = os.path.abspath(os.path.dirname(__file__))
URLS_PATH = os.path.join(ADDON_DIR, "globalPlugins", "urlShortener")
CONFIG_PATH = globalVars.appArgs.configPath

addonHandler.initTranslation()


def onInstall():
	previousUrlsPath = os.path.join(
		CONFIG_PATH, "addons", "urlShortener",
		"globalPlugins", "urlShortener", "urls.json"
	)
	if not os.path.isfile(previousUrlsPath):
		return
	with open(previousUrlsPath, "rt") as f:
		data = json.load(f)
	with open(URLS_PATH, "wt") as f:
		json.dump(data, f, indent="\t")
