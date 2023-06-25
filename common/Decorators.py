import time

from common.Dates import get_time_tuple


def exception_decorator(step_name=None):
    """
    Decorator that wraps a function and handles exceptions raised during its execution.

    Args:
        `step_name (str, optional)`: Name of the step or function. If not provided, the decorator will try to use the function's qualified name. Defaults to None.

    Returns:
        `function`: Decorated function.

    Raises:
        Exception: If any exception occurs during the execution of the decorated function, it is caught, and a new exception is raised with an error message containing the step name and the original exception message.

    Example:
        ```
        @exception_decorator('Step 1')
        def divide(a, b):
            return a / b

        result = divide(10, 0)  # Raises an exception with the error message: '[Step 1] division by zero'
        ```
    """
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
    """
    A decorator that logs the start and end of a function execution along with its execution time.

    Args:
        `step_name (str)`: Optional. The name of the step or function. If not provided, the decorator will
        attempt to retrieve it from the function's __qualname__ attribute. If that is not available,
        it will use the fully qualified name of the function (module + function name).

    Returns:
        `function`: The decorated function.
    """
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
