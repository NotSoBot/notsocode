import asyncio
import random
import string

from concurrent.futures import ProcessPoolExecutor
from functools import partial, wraps
from typing import Callable, Union



original_functions: dict[str, Callable] = {}
pool: Union[ProcessPoolExecutor, None] = None

def _generate_function_name():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))

def _run_function(name, *args, **kwargs):
    return original_functions[name](*args, **kwargs)

def asyncify(loop=None, executor=None, cpu_bound=False):
    global pool
    if cpu_bound:
        executor = pool = pool or ProcessPoolExecutor()

    def decorator(func: Callable):
        function_name =_generate_function_name()
        if cpu_bound:
            original_functions[function_name] = func

        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_loop = loop
            if current_loop is None:
                current_loop = asyncio.get_event_loop()

            if cpu_bound:
                pfunc = partial(_run_function, function_name, *args, **kwargs)
            else:
                pfunc = partial(func, *args, **kwargs)
            return await current_loop.run_in_executor(executor, pfunc)
        return wrapper
    return decorator
