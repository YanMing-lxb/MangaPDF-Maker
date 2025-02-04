

import logging
import logging.config
from rich.logging import RichHandler  # 导入rich库的日志处理模块


# --------------------------------------------------------------------------------
# 定义日志记录器
# --------------------------------------------------------------------------------
def setup_logger(verbose):
    """
    配置并设置日志记录器。

    参数:
    - verbose (bool): 如果为True，则启用详细日志输出；否则，仅输出警告及以上级别的日志。

    返回:
    - logger: 配置好的日志记录器实例。

    行为逻辑:
    1. 根据verbose参数决定日志级别（INFO或WARNING）。
    2. 使用RichHandler配置日志格式，包括消息格式、日期格式等。
    3. 获取并返回名为'pytexmk.py'的日志记录器实例。
    """
    FORMAT = "%(message)s"
    
    # 如果设置了verbose 选项，则将日志级别设置为INFO，以便输出更多信息
    if verbose:
        print("启用详细日志输出...")
        logging.basicConfig(
            level="INFO",
            format=FORMAT,
            datefmt="[%X]",
            handlers=[RichHandler(show_level=True, show_time=False, markup=True, show_path=False)]
        )
    else:
        logging.basicConfig(
            level="WARNING",
            format=FORMAT,
            datefmt="[%X]",
            handlers=[RichHandler(show_level=True, show_time=False, markup=True, show_path=False)]
        )

    # 获取名为'MangaPDF Maker'的日志记录器实例
    logger = logging.getLogger('MangaPDF Maker')

    return logger

