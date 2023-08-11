"""
These are implementations of different (in-application) rate limiting algorithms.

`identifier` is used as the first (usually only) argument for each implementation
because it might refer to IP address, a session ID, or perhaps an API key or token.
"""
import datetime as dt

import redis


r = redis.Redis()


MAX_CAPACITY = 8


class TooManyRequests(Exception):
    pass


class EntryDoesntExist(Exception):
    pass



def leaking_bucket(identifier: str, data: str) -> None:
    """
    When a request arrives, the system checks if the queue for this particular
    `identifier` is full. If it is not full, the request is added to the queue.
    Otherwise, the request is dropped. 

    Requests are pulled from the queue and processed at regular intervals.
    (a separate process implemented elsewhere)
    TODO: implement that other process!
      - [ ] done
    """
    STORE_NAME_PREFIX = "leaking_bucket:queue:tasks"
    store_name = f"{STORE_NAME_PREFIX}:{identifier}"
    
    if r.llen(store_name) == MAX_CAPACITY:
        raise TooManyRequests
    r.lpush(store_name, data)


TOKEN_BUCKET = {}


def get_entry_from_token_bucket(identifier: str) -> dict | None:
    """
    This is implemented independently in order to decouple it from its caller.
    Here it is initially implemented in-memory, but for scalability we'd
    want to use something more long-lived.
    """
    return TOKEN_BUCKET.get(identifier)


def token_bucket(identifier: str) -> str:
    """
    Tokens are put in the bucket at preset rates periodically. 
    Once the bucket is full, no more tokens are added. 
    The refiller puts NUM_TOKENS_TO_REFILL tokens into the bucket every minute. 

    To be explicit, there is a token bucket for every `identifier`,
    aka every user/IP
    """
    REFILL_EVERY_SECONDS = 15
    NUM_TOKENS_TO_REFILL = 4

    entry = get_entry_from_token_bucket(identifier)

    if entry is None:
        TOKEN_BUCKET[identifier] = {'tokens': MAX_CAPACITY, 'last_refilled': dt.datetime.now().timestamp()}
    else:
        last_refilled = entry['last_refilled']
        now = dt.datetime.now().timestamp() 
        if now >= last_refilled + REFILL_EVERY_SECONDS:
            num_tokens_to_refill = int((now - last_refilled) // REFILL_EVERY_SECONDS * NUM_TOKENS_TO_REFILL)
            entry['last_refilled'] = dt.datetime.now().timestamp()
            entry['tokens'] = min(entry['tokens'] + num_tokens_to_refill, MAX_CAPACITY)

    left = TOKEN_BUCKET[identifier]['tokens']
    if left == 0:
        raise TooManyRequests

    TOKEN_BUCKET[identifier]['tokens'] -= 1