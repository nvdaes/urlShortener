# -*- coding: UTF-8 -*-

# installTasks for the urlShortener add-on
# Copyright (C) 2023 Noelia Ruiz Martínez, other contributors
# Released under GPL2

import os

import globalVars

CONFIG_PATH = globalVars.appArgs.configPath
ADDON_CONFIG_PATH = os.path.join(CONFIG_PATH, "urlShortener")


def onInstall():
	if not os.path.isdir(ADDON_CONFIG_PATH):
		os.makedirs(ADDON_CONFIG_PATH)
