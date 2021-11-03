from loguru import logger


def isnotebook():
    try:
        shell = get_ipython().__class__.__name__
        return shell == "ZMQInteractiveShell"
    except NameError:
        return False  # Probably standard Python interpreter


if isnotebook():
    from tqdm.notebook import tqdm
else:
    from tqdm import tqdm

logger.remove()
logger.add(
    lambda msg: tqdm.write(msg, end=""), colorize=True, enqueue=True, level="INFO", backtrace=True
)
