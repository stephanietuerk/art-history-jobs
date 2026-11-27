"""Fetch rendered page HTML from a Fandom wiki via the standard MediaWiki API.

Replaces the `wikia` package, which called Fandom's retired wikia.com API.
Docs: https://www.mediawiki.org/wiki/API:Parsing_wikitext
"""

import httpx

USER_AGENT = "art-history-jobs-scraper (https://github.com/stephanietuerk/art-history-jobs)"


class FandomPageError(Exception):
    """Raised when the API returns an error instead of a page (e.g., missing page)."""


class FandomClient:
    def __init__(self, wiki: str, timeout: float = 30.0) -> None:
        self.api_url = f"https://{wiki}.fandom.com/api.php"
        self._client = httpx.Client(
            headers={"User-Agent": USER_AGENT},
            timeout=timeout,
            follow_redirects=True,
        )

    def get_page_html(self, title: str) -> str:
        response = self._client.get(
            self.api_url,
            params={
                "action": "parse",
                "page": title,
                "prop": "text",
                "format": "json",
                "formatversion": 2,
                "disableeditsection": 1,  # drop the "[edit | edit source]" links
                "redirects": 1,  # follow wiki-level page redirects
            },
        )
        response.raise_for_status()  # turn 4xx/5xx into an exception
        data = response.json()
        if "error" in data:
            raise FandomPageError(f"{title!r}: {data['error'].get('info', data['error'])}")
        return data["parse"]["text"]

    def close(self) -> None:
        self._client.close()

    # These two methods let you write `with FandomClient(...) as client:`,
    # which guarantees close() runs even if an exception is raised.
    def __enter__(self) -> "FandomClient":
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()
