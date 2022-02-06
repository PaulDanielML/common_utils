from typing import Dict, List, Callable
from threading import Thread
import queue
import asyncio
import inspect

__all__ = ["execute_all_with_results"]


def execute_all_with_results(funcs: List[Callable], args: Dict[str, Dict] = {}):
    """
    Provide a list of functions to execute in seperate threads.
    Useful if there are multiple IO-bound functions that need to be executed (e.g. for class init).
    If one or multiple of the function require arguments, provide them like so:
    args = {'func_name_1': {arg1: 4, arg2: 'test'}}.
    Returns dictionary with key-value pairs function_name: function_return_value. Therefore, unique function
    names should be provided in funcs.  Can handle coroutines.
    """

    res_queue = queue.Queue()

    def _exc_and_put_result(f: Callable, args: Dict):
        if inspect.iscoroutinefunction(f):
            res_queue.put({f.__name__: asyncio.run(f(**args))})
        else:
            res_queue.put({f.__name__: f(**args)})

    threads = []
    for f in funcs:
        thread = Thread(target=_exc_and_put_result, args=(f, args.get(f.__name__, {})))
        thread.start()
        threads.append(thread)

    for t in threads:
        t.join()

    results = {}
    while not res_queue.empty():
        results.update(res_queue.get())
    return results
