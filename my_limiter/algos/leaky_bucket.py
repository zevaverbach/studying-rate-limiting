import datetime as dt

import redis


r = redis.Redis()


class TooManyRequests(Exception):
    pass


MAX_CAPACITY = 8
STORE_NAME_PREFIX_LEAKING_BUCKET = "leaking_bucket:queue:tasks"
LEAKING_BUCKET_INDEX_NAME = "exporter:queue:tasks:index"
RUN_LEAKING_BUCKET_TASKS_EVERY_X_SECONDS = 15
NUM_TASKS_TO_RUN_FOR_EACH_USER_AT_INTERVAL = 2


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
