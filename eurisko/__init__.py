"""
PyEurisko - A Python implementation of Douglas Lenat's Eurisko system.

This package provides a framework for implementing self-modifying heuristics
and machine learning through an extensible unit-based knowledge representation system.
"""

from .system import System
from .tasks.task_manager import TaskManager
from .units import Unit, UnitRegistry
from .slots import SlotRegistry

__all__ = ['System', 'TaskManager', 'Unit', 'UnitRegistry', 'SlotRegistry']