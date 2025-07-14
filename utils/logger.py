import os
import logging
from logging.handlers import TimedRotatingFileHandler

def setup_logger(
    name: str,
    level: int = logging.INFO,
    log_dir: str = "./logs",
    when: str = "midnight",
    backup_count: int = 7,
) -> logging.Logger:
    """
    创建并返回一个日志记录器，输出到控制台和日志文件。

    参数:
    - name: 记录器名称，也将作为日志文件名。
    - level: 日志级别，默认 logging.INFO。
    - log_dir: 日志文件存放目录，默认 'logs'。
    - when: 切割周期，默认为 'midnight'（每天）。
    - backup_count: 保留文件数量，默认保留最近7个日志文件。
    """

    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logger = logging.getLogger(name)
    logger.setLevel(level)


    if logger.handlers:
        return logger


    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s [%(name)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = TimedRotatingFileHandler(
        filename=os.path.join(log_dir, f"{name}.log"),
        when=when,
        backupCount=backup_count,
        encoding='utf-8',
        utc=True
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
