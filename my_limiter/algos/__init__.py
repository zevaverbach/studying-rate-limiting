"""
These are implementations of different (in-application) rate limiting algorithms.

`identifier` is used as the first (usually only) argument for each implementation
because it might refer to IP address, a session ID, or perhaps an API key or token.
"""
from .token_bucket import token_bucket_in_memory_lazy_refill, TooManyRequests
from .leaky_bucket import (
    leaking_bucket_dequeue,
    leaking_bucket_enqueue,
    RUN_LEAKING_BUCKET_TASKS_EVERY_X_SECONDS,
)
