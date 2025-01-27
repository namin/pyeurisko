"""Factory for creating rule functions with proper error handling and logging."""
import functools
import logging

logger = logging.getLogger(__name__)

def rule_factory(func):
    """Decorator to wrap rule functions with proper setup and error handling.
    
    This decorator ensures that rule functions:
    1. Are properly bound to their heuristic unit
    2. Have access to proper logging
    3. Handle errors gracefully
    4. Are properly registered with the heuristic
    """
    @functools.wraps(func)
    def wrapper(heuristic, context):
        try:
            logger.debug(f"Executing {func.__name__} for {heuristic.name}")
            result = func(heuristic, context)
            logger.debug(f"Result from {func.__name__}: {result}")
            return result
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            return False
            
    # Store original function name for property setting
    wrapper.rule_name = func.__name__
    return wrapper
