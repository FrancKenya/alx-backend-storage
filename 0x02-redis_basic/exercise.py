#!/usr/bin/env python3
""" Exercise: Caching function """

from functools import wraps
import redis
from uuid import uuid4
from typing import Callable, Optional, Union


def count_calls(method: Callable) -> Callable:
    """Decorator that counts the number of times a function is called"""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """Wrapper function"""
        key = method.__qualname__
        self._redis.incr(key)
        return method(self, *args, **kwargs)
    return wrapper


def call_history(method: Callable) -> Callable:
    """Decorator that stores the history of inputs and outputs"""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """Wrapper function"""
        input_key = method.__qualname__ + ":inputs"
        self._redis.rpush(input_key, str(args))
        output_key = method.__qualname__ + ":outputs"
        self._redis.rpush(output_key, str(method(self, *args, **kwargs)))
        return method(self, *args, **kwargs)
    return wrapper


class Cache:
    def __init__(self, _redis: redis.Redis = None):
        """Initialize the client and flush the database"""
        self._redis = redis.Redis()
        self._redis.flushdb()

    @call_history
    @count_calls
    def store(self, data: Union[int, str, bytes, float]) -> str:
        """Store the input data in Redis using a random key"""
        key = str(uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str, fn: callable = None) -> Union[str, bytes,
                                                          int, float]:
        """A method that takes a key and an optional callable as input"""
        data = self._redis.get(key)
        if fn:
            return fn(data)
        return data

    def get_str(self, key: str) -> Union[str, None]:
        """Get a string from the redis cache"""
        return self.get(key, fn=lambda data: data.decode('utf-8'))

    def get_int(self, key: int) -> Union[int, None]:
        """Get an integer from the redis cache"""
        return self.get(key, fn=int)


def replay(method: Callable) -> Callable:
    """A function that displays the call history"""
    method_name = method.__qualname__
    redis_instance = method.__self__._redis

    input_key = redis_instance.lrange("{}:inputs".format(method_name), 0, -1)
    output_key = redis_instance.lrange("{}:outputs".format(method_name), 0, -1)
    print("{} was called {} times:".format(
        method_name, method.__self__.get_int(method_name)))
    for key, value in zip(input_key, output_key):
        print("{}(*{}) -> {}".format(
            method_name, key.decode(), value.decode()))
