# -*- coding: UTF-8 -*-

# Link Shortener: Plugin to shorten URLs with NVDA
# Copyright (C) 2023 Noelia Ruiz Martínez
# Released under GPL 2

from abc import ABC, abstractmethod
from dataclasses import dataclass
from urllib.request import urlopen, Request
from urllib.parse import unquote
from typing import Optional

from logHandler import log


class UrlShortener(ABC):

	def __init__(self, originalUrl: str):
		self.originalUrl = originalUrl
		self.shortenedUrl = None
		self.shortenUrl()

	def getOriginalUrl(self) -> str:
		return self.originalUrl

	def getShortenedUrl(self) -> Optional[str]:
		return self.shortenedUrl

	@abstractmethod
	def shortenUrl(self):
		pass


class IsGd(UrlShortener):

	def shortenUrl(self) -> Optional[str]:
		url = self.originalUrl
		unquotedUrl = unquote(url)
		headers = {
			'User-Agent': 'Mozilla'
		}
		apiUrl = f"https://is.gd/create.php?format=simple&url={unquotedUrl}"
		try:
			resp = urlopen(Request(apiUrl, headers=headers))
			self.shortenedUrl = resp.read().decode("utf-8")
		except Exception as e:
			log.debugWarning(e)


@dataclass
class UrlMetadata:
	name: str = ""
	originalUrl: str = ""
	shortenedUrl: str = ""
