#!/usr/bin/env python3
"""Contains a function that tracks the number of times a web page is visited"""

import redis
import requests

count = 0


def get_page(url: str) -> str:
    """Returns the content of a web page"""
    i = redis.Redis()
    response = requests.get(url)
    i.incr(f'count:{url}')
    i.setex(f'cached:{url}', 10, i.get(f"cached:{url}"))
    return response.text


if __name__ == '__main__':
    get_page('http://slowwly.robertomurray.co.uk')
