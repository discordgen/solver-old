from .base import Agent
from typing import Literal
from urllib.parse import urlsplit, urlencode
from http.client import HTTPSConnection
import random
import time
import json

class ChromeAgent(Agent):
    header_order = {
        "host": 0,
        "connection": 1,
        "content-length": 2.1,
        "sec-ch-ua": 2,
        "cache-control": 3,
        "content-type": 4,
        "sec-ch-ua-mobile": 5,
        "user-agent": 6,
        "sec-ch-ua-platform": 7,
        "accept": 8,
        "origin": 9,
        "sec-fetch-site": 10,
        "sec-fetch-mode": 11,
        "sec-fetch-dest": 12,
        "referer": 13,
        "accept-encoding": 14,
        "accept-language": 15
    }

    def __init__(self, user_agent, screen_properties, navigator_properties, platform):
        super().__init__()
        self.platform = platform
        self.user_agent = user_agent
        self.chrome_version = user_agent.split("Chrome/", 1)[1].split(" ", 1)[0]

        self.screen_properties = screen_properties  
        self.navigator_properties = navigator_properties

    def get_screen_properties(self):
        return self.screen_properties

    def get_navigator_properties(self):
        return self.navigator_properties

    def epoch(self, ms: int = True):
        t = time.time() * 1000
        t += self._epoch_delta
        if not ms: t /= 1000
        return int(t)

    def epoch_travel(self, delta: float, ms: bool = True):
        if not ms: delta *= 1000
        self._epoch_delta += delta

    def epoch_wait(self):
        print("Sleeping for " + str(self._epoch_delta / 1000) + " seks bcs y not")
        time.sleep(self._epoch_delta/1000)
        self._epoch_delta = 0

    def json_encode(self, data: Literal) -> str:
        return json.dumps(data, separators=(",", ":"))

    def url_encode(self, data: dict) -> str:
        return urlencode(data)
    
    def format_headers(
        self,
        url: str,
        body: bytes = None,
        headers: dict = {},
        origin_url: str = None,
        sec_site: str = "cross-site",
        sec_mode: str = "cors",
        sec_dest: str = "empty"
    ) -> dict:
        p_url = urlsplit(url)
        p_origin_url = urlsplit(origin_url) if origin_url else None

        headers["Host"] = p_url.hostname
        headers["Connection"] = "keep-alive"
        headers["sec-ch-ua"] = f'"Chromium";v="{self.chrome_version.split(".", 1)[0]}", "Google Chrome";v="{self.chrome_version.split(".", 1)[0]}", ";Not A Brand";v="99"'
        headers["sec-ch-ua-mobile"] = "?0"
        headers["User-Agent"] = self.user_agent
        headers["sec-ch-ua-platform"] = '"' + self.platform + '"'
        headers.setdefault("Accept", "*/*")
        headers["Accept-Encoding"] = "gzip, deflate, br"
        headers["Accept-Language"] = 'en-US,en;q=0.9'

        if body is not None:
            headers["Content-Length"] = str(len(body))

        headers["Sec-Fetch-Site"] = sec_site
        headers["Sec-Fetch-Mode"] = sec_mode
        headers["Sec-Fetch-Dest"] = sec_dest

        if sec_mode == "navigate":
            headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
            if sec_site == "same-origin" and origin_url:
                headers["Referer"] = p_origin_url.scheme + "://" + p_origin_url.hostname + p_origin_url.path + (("?" + p_origin_url.query) if p_origin_url.query else "")
            elif origin_url:
                headers["Referer"] = p_origin_url.scheme + "://" + p_origin_url.hostname + p_origin_url.path + "/"
        
        elif sec_mode == "cors" and origin_url:
            headers["Origin"] = p_origin_url.scheme + "://" + p_origin_url.hostname
            headers["Referer"] = p_origin_url.scheme + "://" + p_origin_url.hostname + p_origin_url.path + (("?" + p_origin_url.query) if p_origin_url.query else "")
        
        elif sec_mode == "no-cors" and origin_url:
            headers["Origin"] = p_origin_url.scheme + "://" + p_origin_url.hostname
            headers["Referer"] = p_origin_url.scheme + "://" + p_origin_url.hostname + p_origin_url.path + (("?" + p_origin_url.query) if p_origin_url.query else "")

        headers = dict(sorted(
            headers.items(),
            key=lambda x: self.header_order.get(x[0].lower(), 9999)
        ))
        return headers