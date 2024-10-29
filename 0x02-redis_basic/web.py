#!/usr/bin/env python3
"""URL visits count functions and caching."""

from functools import wraps
import redis
import requests

# Initialize Redis connection
redis_client = redis.Redis()


def count_access(method):
    """Decorator to count URL accesses."""
    @wraps(method)
    def wrapper(url: str) -> str:
        """Wrapper function"""
        redis_client.incr(f"count:{url}")
        return method(url)
    return wrapper


def cache_page(method):
    """Decorator to cache the page content with a 10-second expiration."""
    @wraps(method)
    def wrapper(url: str) -> str:
        """Wrapper function"""
        # Check if content is already cached
        cached_content = redis_client.get(f"cached:{url}")
        if cached_content:
            return cached_content.decode()

        # If not cached, fetch and cache the content
        page_content = method(url)
        redis_client.setex(f"cached:{url}", 10, page_content)
        return page_content
    return wrapper


@cache_page
@count_access
def get_page(url: str) -> str:
    """Fetches and returns the HTML content of a given URL."""
    response = requests.get(url)
    return response.text


# Example usage
if __name__ == "__main__":
    url = "http://slowwly.robertomurray.co.uk"
    print(get_page(url))
