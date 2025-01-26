"""Initialize all heuristics."""
from typing import Dict, Any
from .heuristics import HeuristicRegistry
from .unit import UnitRegistry

def initialize_all_heuristics(unit_registry: UnitRegistry) -> None:
    """Initialize all registered heuristics."""
    heuristic_registry = HeuristicRegistry()
    # The HeuristicRegistry already sets up all heuristics in its __init__
    # We just need to copy them over to the main unit registry
    for unit_name in heuristic_registry.unit_registry.get_units_by_category('heuristic'):
        unit = heuristic_registry.unit_registry.get_unit(unit_name)
        if unit and not unit_registry.get_unit(unit_name):
            unit_registry.register(unit)
