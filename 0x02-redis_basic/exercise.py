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
        input_key = f"{method.__qualname__}:inputs"
        output_key = f"{method.__qualname__}:outputs"

        # Store inputs as string representation
        self._redis.rpush(input_key, str(args))

        # Call method and store the output in the Redis list
        result = method(self, *args, **kwargs)
        self._redis.rpush(output_key, str(result))

        return result  # Return the actual result of the method
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

    def get(self, key: str, fn: Callable = None) -> Union[str, bytes,
                                                          int, float, None]:
        """A method that takes a key and an optional callable as input"""
        data = self._redis.get(key)
        if data is None:
            return None  # Preserve original Redis.get behavior
        return fn(data) if fn else data

    def get_str(self, key: str) -> Union[str, None]:
        """Get a string from the redis cache"""
        return self.get(key, fn=lambda data: data.decode('utf-8'))

    def get_int(self, key: str) -> Union[int, None]:
        """Get an integer from the redis cache"""
        return self.get(key, fn=int)


def replay(method: Callable) -> None:
    """A function that displays the call history"""
    # Get the method's qualified name
    method_name = method.__qualname__
    # Access Redis instance through the method's instance (`__self__`)
    redis_instance = method.__self__._redis

    # Retrieve call count and input/output history
    call_count = int(redis_instance.get(method_name).decode("utf-8") or 0)
    input_history = redis_instance.lrange(f"{method_name}:inputs", 0, -1)
    output_history = redis_instance.lrange(f"{method_name}:outputs", 0, -1)

    # Display the replay information
    print(f"{method_name} was called {call_count} times:")
    for inputs, output in zip(input_history, output_history):
        print(f"{method_name}(*{inputs.decode(
            'utf-8')}) -> {output.decode('utf-8')}")
