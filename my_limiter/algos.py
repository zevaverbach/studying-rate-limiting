import datetime as dt



TOKEN_BUCKET = {}
TIME_INTERVAL_SECONDS = 15

class TooManyRequests(Exception):
    pass


def token_bucket(ip: str) -> str:
    """
    Tokens are put in the bucket at preset rates periodically. 
    Once the bucket is full, no more tokens are added. 
    The refiller puts NUM_TOKENS_TO_REFILL tokens into the bucket every minute. 
    """
    REFILL_EVERY_SECONDS = TIME_INTERVAL_SECONDS
    NUM_TOKENS_TO_REFILL = 4
    MAX_CAPACITY = 8

    entry = TOKEN_BUCKET.get(ip)

    if entry is None:
        TOKEN_BUCKET[ip] = {'tokens': MAX_CAPACITY, 'last_refilled': dt.datetime.now().timestamp()}
    else:
        last_refilled = entry['last_refilled']
        now = dt.datetime.now().timestamp() 
        if now >= last_refilled + REFILL_EVERY_SECONDS:
            num_tokens_to_refill = int((now - last_refilled) // REFILL_EVERY_SECONDS * NUM_TOKENS_TO_REFILL)
            entry['last_refilled'] = dt.datetime.now().timestamp()
            entry['tokens'] = min(entry['tokens'] + num_tokens_to_refill, MAX_CAPACITY)

    left = TOKEN_BUCKET[ip]['tokens']
    if left == 0:
        raise TooManyRequests

    TOKEN_BUCKET[ip]['tokens'] -= 1