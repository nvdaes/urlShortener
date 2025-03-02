# -*- coding: UTF-8 -*-

# URL Shortener: Plugin to shorten URLs with NVDA
# Copyright (C) 2023 Noelia Ruiz Martínez
# Released under GPL 2

from abc import ABC, abstractmethod
from dataclasses import dataclass
from urllib.request import urlopen, Request
from urllib.parse import quote
from typing import Optional

from logHandler import log


class UrlShortener(ABC):
	def __init__(self, originalUrl: str, *args, **kwargs):
		self.originalUrl = originalUrl
		self.shortenedUrl = None
		self.shortenUrl(*args, **kwargs)

	def getOriginalUrl(self) -> str:
		return self.originalUrl

	def getShortenedUrl(self) -> Optional[str]:
		return self.shortenedUrl

	@abstractmethod
	def shortenUrl(self, *args, **kwargs):
		pass


class IsGd(UrlShortener):
	def shortenUrl(self, customUrl: Optional[str] = None) -> Optional[str]:
		url = self.originalUrl
		quotedUrl = quote(url)
		headers = {
			"User-Agent": "Mozilla",
		}
		if customUrl and len(customUrl) >= 5 and len(customUrl) <= 30:
			apiUrl = f"https://is.gd/create.php?format=simple&url={quotedUrl}&shorturl={customUrl}"
		else:
			apiUrl = f"https://is.gd/create.php?format=simple&url={quotedUrl}"
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
