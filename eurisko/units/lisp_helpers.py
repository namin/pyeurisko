"""Helper functions for LISP-like operations."""

import operator
import random
import logging
from typing import Any, List, Set, TypeVar, Union, Optional, Dict, Callable
from functools import reduce
import math

T = TypeVar('T')

# Basic types
BIT = bool
STRING = str 
IO_PAIR = tuple
DataType = Union[str, bool, int, float, list, tuple, None]

# Global registry for predicates and functions
_defn_registry: Dict[str, Callable] = {}
_alg_registry: Dict[str, Callable] = {}

def register_defn(name: str, fn: Callable) -> None:
    """Register a predicate."""
    _defn_registry[name] = fn

def register_alg(name: str, fn: Callable) -> None:
    """Register an algorithm."""
    _alg_registry[name] = fn

def run_defn(name: str, *args: Any) -> bool:
    """Run a registered predicate."""
    if name not in _defn_registry:
        logging.warning(f"No predicate registered for {name}")
        return False
    return _defn_registry[name](*args)

def run_alg(name: str, *args: Any) -> Any:
    """Run a registered algorithm."""
    if name not in _alg_registry:
        logging.warning(f"No algorithm registered for {name}")
        return None
    return _alg_registry[name](*args)

def is_sequence(x: Any) -> bool:
    """Test if x is a sequence."""
    return isinstance(x, (list, tuple))

def equals(x: Any, y: Any) -> bool:
    """Equal predicate."""
    if is_sequence(x) and is_sequence(y):
        if len(x) != len(y):
            return False
        return all(equals(a, b) for a, b in zip(x, y))
    return x == y

def eq(x: Any, y: Any) -> bool:
    """Identity comparison."""
    return x is y

def set_difference(s1: List[T], s2: List[T]) -> List[T]:
    """Set difference operation."""
    return list(set(s1) - set(s2))

def set_union(s1: List[T], s2: List[T]) -> List[T]:
    """Set union operation."""
    return list(set(s1) | set(s2))

def set_intersect(s1: List[T], s2: List[T]) -> List[T]:
    """Set intersection operation."""
    return list(set(s1) & set(s2))

def append_(x: List[T], y: List[T]) -> List[T]:
    """Append lists."""
    return x + y

def remove_(x: T, lst: List[T]) -> List[T]:
    """Remove item from list."""
    return [item for item in lst if item != x]

def equals_num(x: Union[int, float], y: Union[int, float]) -> bool:
    """Numeric equality."""
    return x == y

def greater_equal(x: Union[int, float], y: Union[int, float]) -> bool:
    """Greater than or equal."""
    return x >= y

def greater(x: Union[int, float], y: Union[int, float]) -> bool:
    """Greater than."""
    return x > y

def less_equal(x: Union[int, float], y: Union[int, float]) -> bool:
    """Less than or equal."""
    return x <= y

def less(x: Union[int, float], y: Union[int, float]) -> bool:
    """Less than."""
    return x < y

def divides(x: int, y: int) -> bool:
    """Test if x divides y evenly."""
    return y % x == 0 if x != 0 else False

def fixp(x: Any) -> bool:
    """Test if x is a fixed-point number (integer)."""
    return isinstance(x, int)

def oddp(x: int) -> bool:
    """Test if x is odd."""
    return x % 2 == 1

def is_subset_of(s1: List[T], s2: List[T]) -> bool:
    """Test if s1 is a subset of s2."""
    return set(s1).issubset(set(s2))

def successor(x: int) -> int:
    """Return x + 1."""
    return x + 1

def last(x: List[T]) -> T:
    """Return last element of list."""
    return x[-1]

def no_repeats_in(x: List[T]) -> bool:
    """Test if list has no repeated elements."""
    return len(x) == len(set(x))

def repeats_in(x: List[T]) -> bool:
    """Test if list has repeated elements."""
    return len(x) != len(set(x))

def add_inv(x: Any) -> None:
    """Add inverse - placeholder."""
    pass

def average_worths(*args: Any) -> int:
    """Average worths - placeholder."""
    return 500

def random_subset(lst: List[T]) -> List[T]:
    """Return random subset."""
    if not lst:
        return []
    return random.sample(lst, random.randint(0, len(lst)))

def random_choose(lst: List[T]) -> Optional[T]:
    """Choose random element."""
    return random.choice(lst) if lst else None

def good_subset(lst: List[T]) -> List[T]:
    """Return "good" subset - currently just random."""
    return random_subset(lst)

def good_choose(lst: List[T]) -> Optional[T]:
    """Choose "good" element - currently just random."""
    return random_choose(lst)

def best_subset(lst: List[T]) -> List[T]:
    """Return "best" subset - currently just random."""
    return random_subset(lst)

def best_choose(lst: List[T]) -> Optional[T]:
    """Choose "best" element - currently just random.""" 
    return random_choose(lst)

def cons(x: T, lst: Optional[List[T]] = None) -> List[T]:
    """Cons operation."""
    if lst is None:
        return [x]
    if isinstance(lst, list):
        return [x] + lst
    return [x, lst]

def car(lst: List[T]) -> Optional[T]:
    """First element."""
    return lst[0] if lst else None

def cdr(lst: List[T]) -> List[T]:
    """Rest of list."""
    return lst[1:] if len(lst) > 1 else []

def cadr(lst: List[T]) -> Optional[T]:
    """Second element."""
    return lst[1] if len(lst) > 1 else None

def caddr(lst: List[T]) -> Optional[T]:
    """Third element."""
    return lst[2] if len(lst) > 2 else None

def memb(x: T, lst: List[T]) -> bool:
    """Member predicate."""
    return x in lst

def member(x: T, lst: List[T]) -> bool:
    """Member with equals."""
    return any(equals(x, item) for item in lst)

def not_(x: Any) -> bool:
    """Logical not."""
    return not x

def atom(x: Any) -> bool: 
    """Test if atomic (non-sequence)."""
    return not is_sequence(x)

def null(x: Any) -> bool:
    """Test if null/empty."""
    if is_sequence(x):
        return len(x) == 0
    return x is None

def consp(x: Any) -> bool:
    """Test if cons cell (non-empty sequence)."""
    return is_sequence(x) and len(x) > 0

def listp(x: Any) -> bool:
    """Test if list."""
    return is_sequence(x)

def cddr(lst: List[T]) -> List[T]:
    """Rest of rest of list."""
    return lst[2:] if len(lst) > 2 else []

def cdddr(lst: List[T]) -> List[T]:
    """Rest of rest of rest of list."""
    return lst[3:] if len(lst) > 3 else []

def every(pred: Callable[[T], bool], lst: List[T]) -> bool:
    """All elements satisfy predicate."""
    return all(pred(x) for x in lst)

def copy_list(lst: List[T]) -> List[T]:
    """Copy a list."""
    return lst.copy()

def copytree(x: Any) -> Any:
    """Deep copy."""
    if is_sequence(x):
        return [copytree(i) for i in x]
    return x

def getattr_(obj: Any, attr: str, default: Any = None) -> Any:
    """Get attribute with default."""
    return getattr(obj, attr, default)

__all__ = [
    'BIT', 'STRING', 'IO_PAIR', 'DataType',
    'register_defn', 'register_alg', 'run_defn', 'run_alg',
    'equals', 'eq', 'set_difference', 'set_union', 'set_intersect',
    'append_', 'remove_', 'equals_num', 'greater_equal', 'greater',
    'less_equal', 'less', 'divides', 'fixp', 'oddp', 'is_subset_of',
    'successor', 'last', 'no_repeats_in', 'repeats_in', 'add_inv',
    'average_worths', 'random_subset', 'random_choose', 'good_subset',
    'good_choose', 'best_subset', 'best_choose', 'cons', 'car', 'cdr',
    'cadr', 'caddr', 'cddr', 'cdddr', 'memb', 'member', 'not_', 'atom',
    'null', 'consp', 'listp', 'every', 'copy_list', 'copytree', 'getattr_'
]