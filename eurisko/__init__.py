"""
PyEurisko - A Python implementation of Douglas Lenat's Eurisko system.

This package provides a framework for implementing self-modifying heuristics
and machine learning through an extensible unit-based knowledge representation system.
"""

from .units import Unit, UnitRegistry
from .slots import Slot, SlotRegistry
from .tasks import Task, TaskManager

__version__ = '0.2.0'
