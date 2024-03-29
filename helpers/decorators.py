import functools
from pathlib import Path
from timeit import default_timer as timer
from functools import wraps

from line_profiler import LineProfiler
from loguru import logger
from pyinstrument import Profiler

from .files import get_file_age_in_days

__all__ = ["profile", "execute_if_older"]


def profile(func):
    """
    Profiles the decorated function or method and renders the results as foldable HTML in the browser.
    The decorator uses statistical profiling, not tracing, therefore has much lower overhead.
    It is meant to be used to identify the slowest part in a piece of code, not for accurate tracing of every call.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        profiler = Profiler()
        profiler.start()
        try:
            result = func(*args, **kwargs)
            profiler.stop()
            profiler.open_in_browser()
        except KeyboardInterrupt:
            profiler.stop()
            profiler.open_in_browser()
            result = None
        except Exception as e:
            profiler.stop()
            raise e

        return result

    return wrapper


def execute_if_older(file_to_check: Path, days: int = 1):
    """
    The decorated function or method will only be executed if the file specified in 'file_to_check'
    is older than 'days' days.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            file_age = get_file_age_in_days(file_to_check)

            if file_age is None:
                return func(*args, **kwargs)

            if file_age > days:
                return func(*args, **kwargs)

            logger.info(
                f"Not executing function {func.__name__}, as file {file_to_check} was found with age of {file_age} days."
            )

            return None

        return wrapper

    return decorator


def line_profile(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        try:
            profiler = LineProfiler(function)
            profiler.enable_by_count()
            result = function(*args, **kwargs)
        finally:
            profiler.disable_by_count()
            profiler.print_stats(output_unit=1)

        return result

    return wrapper


def time_execution(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        start = timer()
        result = function(*args, **kwargs)
        end = timer()

        print(f"'{function.__name__}' took {round(end - start, 3)}s to execute.")
