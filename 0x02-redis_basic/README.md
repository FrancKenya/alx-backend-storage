Redis Caching System
Overview
This project implements a simple caching system using Redis, demonstrating the use of decorators for tracking function calls, caching web page content, and counting accesses to URLs. The system includes a Cache class that interacts with a Redis database to store and retrieve data efficiently.

Features
Caching Mechanism: Automatically caches results of web page requests for a specified duration, improving performance for repeated accesses.
Access Counting: Tracks how many times each URL is accessed, incrementing a counter in Redis with each request.
Function Call History: Uses decorators to maintain a history of inputs and outputs for tracked functions.
Replay Functionality: Allows users to display the history of calls for specific functions, including their input parameters and outputs.
Installation
Prerequisites
Python 3.x
Redis server running locally or accessible remotely
Required Python packages
Setup
Install Redis: Ensure that Redis is installed and running on your machine. Refer to Redis documentation for installation instructions.

Install Required Packages: Use pip to install the necessary Python packages

