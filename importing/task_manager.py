from concurrent.futures import ThreadPoolExecutor
import threading

executor = ThreadPoolExecutor()
running_tasks = {}

class Task:
    def __init__(self):
        self.cancelled = threading.Event()

    def cancel(self):
        self.cancelled.set()

    def is_cancelled(self):
        return self.cancelled.is_set()

def submit_task(process_id, func, *args):
    task = Task()
    future = executor.submit(func, task, *args)
    running_tasks[process_id] = (future, task)
    return future

def cancel_task(upload_id):
    if upload_id in running_tasks:
        future, task = running_tasks[upload_id]
        task.cancel()
        # Note: future.cancel() will not cancel a running task in ThreadPoolExecutor
        del running_tasks[upload_id]
        return True
    return False