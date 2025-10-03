import asyncio
import random
import time
from dataclasses import dataclass

@dataclass
class Job:
    name: str
    proto: str
    host: str
    coro: callable

class RateLimiter:
    def __init__(self, per_host_qps: float = 1.0, jitter: float = 0.4):
        self.host_next = {}
        self.per_host_qps = per_host_qps
        self.jitter = jitter

    async def acquire(self, host: str):
        now = time.time()
        next_time = self.host_next.get(host, now)
        wait = max(0, next_time - now) + random.uniform(0, self.jitter)
        await asyncio.sleep(wait)
        self.host_next[host] = time.time() + (1.0 / max(0.1, self.per_host_qps))

async def run_jobs(jobs, limiter: RateLimiter):
    for job in jobs:
        await limiter.acquire(job.host)
        await job.coro()
