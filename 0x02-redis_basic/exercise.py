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
        # Increment call count
        self._redis.incr(key)
        # Call the original method and return its result
        return method(self, *args, **kwargs)
    return wrapper


def call_history(method: Callable) -> Callable:
    """Decorator that stores the history of inputs and outputs"""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """Wrapper function"""
        input_key = method.__qualname__ + ":inputs"
        output_key = method.__qualname__ + ":outputs"

        # Store inputs as string representation
        self._redis.rpush(input_key, str(args))

        # Call method and store the output in the Redis list
        result = method(self, *args, **kwargs)
        self._redis.rpush(output_key, str(result))

        return result  # Return the actual result of the method
    return wrapper


class Cache():
    """The Cache class"""
    def __init__(self) -> None:
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

    def get(self, key: str,
            fn: Optional[Callable] = None) -> Union[int, bytes, float, int]:
        """A method that takes a key and an optional callable as input"""
        data = self._redis.get(key)
        if data is None:
            return None  # Preserve original Redis.get behavior
        return fn(data) if fn else data

    def get_str(self, key: str) -> str:
        """Get a string from the redis cache"""
        return self.get(key).decode()

    def get_int(self, key: str) -> int:
        """Get an integer from the redis cache"""
        result = self.get(key).decode()
        try:
            value = int(result)
        except ValueError:
            value = 0
        return value


def replay(method: Callable) -> None:
    """A function that displays the call history"""
    # Get the method's qualified name
    method_name = method.__qualname__
    # Access Redis instance through the method's instance (`__self__`)
    redis_instance = method.__self__._redis

    # Retrieve call count and input/output history
    input_history = redis_instance.lrange(
        "{}:inputs".format(method_name), 0, -1)
    output_history = redis_instance.lrange(
        "{}:outputs".format(method_name), 0, -1)

    # Display the replay information
    print("{} was called {} times:".format(
        method_name, method.__self__.get_int(method_name)))
    for key, value in zip(input_history, output_history):
        print("{}(*{}) -> {}".format(
            method_name, key.decode(), value.decode()))
