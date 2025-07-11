import multiprocessing
from workers.text_worker import start_text_worker
from workers.image_worker import start_image_worker
from workers.audio_worker import start_audio_worker


def worker_wrapper(target_func):
    """包装函数确保每个进程独立初始化"""
    from services.di import container
    container.release_resources()
    target_func()


if __name__ == "__main__":
    processes = []

    for _ in range(1):
        p = multiprocessing.Process(
            target=worker_wrapper,
            args=(start_text_worker,)
        )
        processes.append(p)

    for _ in range(1):
        p = multiprocessing.Process(
            target=worker_wrapper,
            args=(start_image_worker,)
        )
        processes.append(p)

    for _ in range(1):
        p = multiprocessing.Process(
            target=worker_wrapper,
            args=(start_audio_worker,)
        )
        processes.append(p)

    for p in processes:
        p.start()

    for p in processes:
        p.join()