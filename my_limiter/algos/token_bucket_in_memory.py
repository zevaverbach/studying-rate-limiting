import datetime as dt

import redis


r = redis.Redis()


class TooManyRequests(Exception):
    pass


TOKEN_BUCKET = {}
MAX_CAPACITY = 8
REFILL_EVERY_SECONDS = 15
NUM_TOKENS_TO_REFILL = 4


def get_entry_from_token_bucket_in_memory(identifier: str) -> dict | None:
    """
    This is implemented independently in order to decouple it from its caller.
    Here it is initially implemented in-memory, but for scalability we'd
    want to use something more long-lived.
    """
    return TOKEN_BUCKET.get(identifier)


def token_bucket_in_memory_lazy_refill(identifier: str) -> str:
    """
    Tokens are put in the bucket at preset rates periodically.
    Once the bucket is full, no more tokens are added.
    The refiller puts NUM_TOKENS_TO_REFILL tokens into the bucket every minute.

    To be explicit, there is a token bucket for every `identifier`,
    aka every user/IP
    """
    entry = get_entry_from_token_bucket(identifier)

    if entry is None:
        TOKEN_BUCKET[identifier] = {
            "tokens": MAX_CAPACITY,
            "last_refilled": dt.datetime.now().timestamp(),
        }
    else:
        last_refilled = entry["last_refilled"]
        now = dt.datetime.now().timestamp()
        if now >= last_refilled + REFILL_EVERY_SECONDS:
            num_tokens_to_refill = int(
                (now - last_refilled) // REFILL_EVERY_SECONDS * NUM_TOKENS_TO_REFILL
            )
            entry["last_refilled"] = dt.datetime.now().timestamp()
            entry["tokens"] = min(entry["tokens"] + num_tokens_to_refill, MAX_CAPACITY)

    left = TOKEN_BUCKET[identifier]["tokens"]
    if left == 0:
        raise TooManyRequests

    TOKEN_BUCKET[identifier]["tokens"] -= 1
