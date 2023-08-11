"""
adapted from https://pravash-techie.medium.com/python-sched-for-automating-tasks-in-python-396618864658
"""
import sched
import time

from algos import leaking_bucket_dequeue, RUN_LEAKING_BUCKET_TASKS_EVERY_X_SECONDS

scheduler = sched.scheduler(time.time, time.sleep)


def repeat_task(first_time=False) -> None:
    scheduler.enter(
        delay=RUN_LEAKING_BUCKET_TASKS_EVERY_X_SECONDS if not first_time else 0,
        priority=1,
        action=leaking_bucket_dequeue,
    )
    scheduler.enter(
        delay=RUN_LEAKING_BUCKET_TASKS_EVERY_X_SECONDS if not first_time else 0,
        priority=1,
        action=repeat_task,
    )


print()
repeat_task(True)
scheduler.run()
