"""
These are implementations of different (in-application) rate limiting algorithms.

`identifier` is used as the first (usually only) argument for each implementation
because it might refer to IP address, a session ID, or perhaps an API key or token.
"""
import datetime as dt

import redis


r = redis.Redis()


class TooManyRequests(Exception):
    pass


class EntryDoesntExist(Exception):
    pass


MAX_CAPACITY = 8
STORE_NAME_PREFIX_LEAKING_BUCKET = "leaking_bucket:queue:tasks"
LEAKING_BUCKET_INDEX_NAME = "exporter:queue:tasks:index"


def leaking_bucket_enqueue(identifier: str, data: str) -> None:
    """
    When a request arrives, the system checks if the queue for this particular
    `identifier` is full. If it is not full, the request is added to the queue.
    Otherwise, the request is dropped.

    Requests are pulled from the queue and processed at regular intervals in
    `leaking_bucket_dequeue`
    """
    store_name = f"{STORE_NAME_PREFIX_LEAKING_BUCKET}:{identifier}"

    if r.llen(store_name) == MAX_CAPACITY:
        raise TooManyRequests
    r.lpush(store_name, data)
    # this is to enable iterating through all the queues in the system
    r.sadd(LEAKING_BUCKET_INDEX_NAME, identifier)


RUN_LEAKING_BUCKET_TASKS_EVERY_X_SECONDS = 15
NUM_TASKS_TO_RUN_FOR_EACH_USER_AT_INTERVAL = 2


def leaking_bucket_dequeue():
    """
    Iterate through all leaking bucket queues and process at least one task
    from each of them.

    To be run on a schedule.
    """

    def run_task(data):
        ...

    for identifier_bytes in r.smembers(LEAKING_BUCKET_INDEX_NAME):
        identifier = identifier_bytes.decode()
        task_list = f"{STORE_NAME_PREFIX_LEAKING_BUCKET}:{identifier}"
        print(
            f"{dt.datetime.now().isoformat()}: dequeueing "
            f"{NUM_TASKS_TO_RUN_FOR_EACH_USER_AT_INTERVAL} tasks from {task_list}"
        )
        for _ in range(NUM_TASKS_TO_RUN_FOR_EACH_USER_AT_INTERVAL):
            data = r.rpop(task_list)
            if data is not None:
                data = data.decode()
                print(f"running task with data '{data}'")
                run_task(data)
            else:
                print("there wasn't anything there")


TOKEN_BUCKET = {}


def get_entry_from_token_bucket(identifier: str) -> dict | None:
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
    REFILL_EVERY_SECONDS = 15
    NUM_TOKENS_TO_REFILL = 4

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
