import datetime as dt



TOKEN_BUCKET = {}
TIME_INTERVAL_SECONDS = 15

class TooManyRequests(Exception):
    pass


def token_bucket(ip: str):
    """
    Tokens are put in the bucket at preset rates periodically. 
    Once the bucket is full, no more tokens are added. 
    The refiller puts NUM_TOKENS_TO_REFILL tokens into the bucket every minute. 
    """
    REFILL_EVERY_SECONDS = TIME_INTERVAL_SECONDS
    NUM_TOKENS_TO_REFILL = 4
    MAX_CAPACITY = 4

    entry = TOKEN_BUCKET.get(ip)

    if entry is None:
        TOKEN_BUCKET[ip] = {'tokens': 4, 'last_refilled': dt.datetime.now().timestamp()}
    else:
        if dt.datetime.now().timestamp() >= entry['last_refilled'] + REFILL_EVERY_SECONDS:
            entry['last_refilled'] = dt.datetime.now().timestamp()
            entry['tokens'] = min(entry['tokens'] + NUM_TOKENS_TO_REFILL, MAX_CAPACITY)
    left = TOKEN_BUCKET[ip]['tokens']
    if left == 0:
        raise TooManyRequests
    TOKEN_BUCKET[ip]['tokens'] -= 1