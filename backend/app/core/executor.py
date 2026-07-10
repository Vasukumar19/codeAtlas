from typing import Callable, Any, Awaitable
from fastapi import BackgroundTasks
from app.core.logger import get_logger

logger = get_logger(__name__)

class JobExecutor:
    def submit(self, job_func: Callable[..., Awaitable[Any]], *args: Any, **kwargs: Any):
        raise NotImplementedError

class LocalBackgroundExecutor(JobExecutor):
    def __init__(self, background_tasks: BackgroundTasks):
        self.background_tasks = background_tasks

    def submit(self, job_func: Callable[..., Awaitable[Any]], *args: Any, **kwargs: Any):
        self.background_tasks.add_task(job_func, *args, **kwargs)
        logger.info("Job submitted to LocalBackgroundExecutor", job_func=job_func.__name__)
