"""Rule factory and management."""
from typing import Any, Callable
from functools import wraps

def rule_factory(func: Callable) -> Callable:
    """Wraps a rule function to provide task manager access."""
    @wraps(func)
    def wrapper(rule, context):
        return func(rule, context)
    return wrapper
