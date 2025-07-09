import asyncio

task_queue = asyncio.Queue(maxsize=100)

async def worker():
    while True:
        func, args, kwargs = await task_queue.get()
        try:
            await func(*args, **kwargs)
        except Exception as e:
            print(f"任务执行异常: {e}")
        finally:
            task_queue.task_done()

def add_task(func, *args, **kwargs):
    task_queue.put_nowait((func, args, kwargs))