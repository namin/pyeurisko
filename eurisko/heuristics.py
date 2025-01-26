"""Core heuristic implementation for PyEurisko."""
from typing import Any, Dict, List, Optional
import random
import time
from .unit import Unit, UnitRegistry
from .heuristic import Heuristic

class HeuristicsManager:
    """Manages application of heuristics."""
    
    debug = True # Turn on debug logging

    def __init__(self, registry: UnitRegistry):
        """Initialize with registry."""
        self.unit_registry = registry

    def get_applicable_heuristics(self, context: Dict[str, Any]) -> List[Heuristic]:
        """Find all heuristics that could apply to a context."""
        heuristics = []
        for unit_name in self.unit_registry.get_units_by_category('heuristic'):
            unit = self.unit_registry.get_unit(unit_name)
            if isinstance(unit, Heuristic) and unit.is_potentially_relevant(context):
                heuristics.append(unit)
        return heuristics

    def apply_heuristics(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply all relevant heuristics to a context."""
        results = []
        for heuristic in self.get_applicable_heuristics(context):
            start_time = time.time()
            success = heuristic.apply(context)
            elapsed = time.time() - start_time
            
            results.append({
                'heuristic': heuristic.name,
                'success': success,
                'elapsed': elapsed
            })
            
        return results
