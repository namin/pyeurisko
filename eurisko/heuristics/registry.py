"""Registry of available heuristics."""
from typing import Any, Dict, List, Optional
from .base import Heuristic
from ..unit import UnitRegistry
from . import (
    h1, h2, h3, h4, h5, h5_criterial, h5_good, h6, h7, h8, h9, h10,
    h11, h12, h13, h14, h15, h16, h17, h18, h19, h20, h21, h22, h23
)

class HeuristicRegistry:
    """Manages registration and access to heuristics."""
    
    def __init__(self, unit_registry=None):
        """Initialize registry with unit registry and setup functions."""
        self.unit_registry = unit_registry or UnitRegistry()
        self._setup_functions = {
            'h1': h1.setup_h1,
            'h2': h2.setup_h2,
            'h3': h3.setup_h3,
            'h4': h4.setup_h4,
            'h5': h5.setup_h5,
            'h5_criterial': h5_criterial.setup_h5_criterial,
            'h5_good': h5_good.setup_h5_good,
            'h6': h6.setup_h6,
            'h7': h7.setup_h7,
            'h8': h8.setup_h8,
            'h9': h9.setup_h9,
            'h10': h10.setup_h10,
            'h11': h11.setup_h11,
            'h12': h12.setup_h12,
            'h13': h13.setup_h13,
            'h14': h14.setup_h14,
            'h15': h15.setup_h15,
            'h16': h16.setup_h16,
            'h17': h17.setup_h17,
            'h18': h18.setup_h18,
            'h19': h19.setup_h19,
            'h20': h20.setup_h20,
            'h21': h21.setup_h21,
            'h22': h22.setup_h22,
            'h23': h23.setup_h23
        }
        self._initialize_heuristics()

    def _initialize_heuristics(self) -> None:
        """Initialize all registered heuristics."""
        for name, setup_fn in self._setup_functions.items():
            heuristic = Heuristic(name, registry=self.unit_registry)
            setup_fn(heuristic)
            # Ensure registry is still set after setup
            heuristic.unit_registry = self.unit_registry
            self.unit_registry.register(heuristic)

    def register_heuristic(
        self,
        name: str,
        setup_fn: Any
    ) -> None:
        """Register a new heuristic setup function."""
        self._setup_functions[name] = setup_fn
        heuristic = Heuristic(name, self.unit_registry)
        setup_fn(heuristic)
        self.unit_registry.register(heuristic)

    def get_heuristic(self, name: str) -> Optional[Heuristic]:
        """Get a heuristic by name."""
        return self.unit_registry.get_unit(name)

    def get_applicable_heuristics(self, context: Dict[str, Any]) -> List[Heuristic]:
        """Find all heuristics that could apply to a context."""
        applicable = []
        for unit_name in self.unit_registry.get_units_by_category('heuristic'):
            unit = self.unit_registry.get_unit(unit_name)
            if isinstance(unit, Heuristic) and unit.is_potentially_relevant(context):
                applicable.append(unit)
        return applicable