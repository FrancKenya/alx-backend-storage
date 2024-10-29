#!/usr/bin/env python3
"""Contains a function that tracks the number of times a web page is visited"""

import redis
import requests

count = 0


def get_page(url: str) -> str:
    """Returns the content of a web page"""
    r = redis.Redis()
    resp = requests.get(url)
    r.incr(f"count:{url}")
    r.setex(f"cached:{url}", 10, r.get(f"cached:{url}"))
    return resp.text


if __name__ == "__main__":
    get_page('http://slowwly.robertomurray.co.uk')
