"""Unit definitions package for PyEurisko."""

from .core import initialize_core_units
from .math import initialize_math_units
from .operations import initialize_operation_units
from .structures import initialize_structure_units
from .predicates import initialize_predicate_units
from .slots import initialize_slot_units
from .categories import initialize_category_units

def initialize_all_units(registry) -> None:
    """Initialize all unit definitions in the correct order."""
    # Initialize in dependency order
    initialize_core_units(registry)        # Core units first (ANYTHING etc)
    initialize_category_units(registry)    # Categories next
    initialize_slot_units(registry)        # Slots before domain-specific units
    initialize_math_units(registry)        # Domain specific units
    initialize_operation_units(registry)
    initialize_structure_units(registry)
    initialize_predicate_units(registry)
