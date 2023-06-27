import time

from common.Dates import get_time_tuple


def exception_decorator(step_name=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                source = getattr(func, '__qualname__', None)
                if source is None:
                    source = f"{func.__module__}.{func.__name__}"
                step = step_name or source
                error_msg = f'[{step}] {str(e)}'
                raise Exception(error_msg)
        return wrapper
    return decorator


def step_logger_decorator(step_name=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            source = getattr(func, '__qualname__', None)
            if source is None:
                source = f"{func.__module__}.{func.__name__}"
            step = step_name or source
            start_time = time.time()
            print(f"Start: [{step}]")
            result = func(*args, **kwargs)
            end_time = time.time()
            elapsed_time = end_time - start_time
            m, s, ms = get_time_tuple(elapsed_time)
            print(
                f"End: [{step}] Execution time - {m}m:{s}s:{ms}ms")
            return result
        return wrapper
    return decorator
