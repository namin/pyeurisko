"""Registry for managing Eurisko heuristics."""
from typing import Any, Dict, List
import time
from ..unit import Unit, UnitRegistry
from .base import Heuristic
from .h1 import setup_h1
from .h2 import setup_h2
from .h3 import setup_h3
from .h4 import setup_h4
from .h5 import setup_h5

class HeuristicRegistry:
    """Global registry for managing heuristic rules."""
    _instance = None
    
    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.unit_registry = UnitRegistry()
            cls._instance.initialize_core_heuristics()
        return cls._instance

    def initialize_core_heuristics(self) -> None:
        """Initialize the core set of heuristic rules."""
        core_rules = [
            # H1: Specialize sometimes-useful actions
            ('h1', "IF an op F has had some good applications, but over 4/5 are bad, "
                  "THEN conjecture that some specializations of F may be superior to F",
             724),
             
            # H2: Kill concepts that produce garbage
            ('h2', "IF you have just finished a task and some units were created, "
                  "AND one of the creators has a property of spewing garbage, "
                  "THEN reduce that creator's worth",
             700),
             
            # H3: Choose slot to specialize
            ('h3', "IF the current task is to specialize a unit, but no specific slot "
                  "to specialize is yet known, THEN randomly choose one",
             101),
             
            # H4: Gather data about new units
            ('h4', "IF a new unit has been synthesized, THEN place a task on the "
                  "agenda to gather new empirical data about it",
             703),
             
            # H5: Choose multiple slots to specialize
            ('h5', "IF the current task is to specialize a unit and no specific slot "
                  "has been chosen, THEN randomly select which slots to specialize",
             151)
        ]
        
        for name, desc, worth in core_rules:
            heuristic = Heuristic(name, desc, worth)
            self.unit_registry.register(heuristic)
            self._setup_heuristic(heuristic)

    def _setup_heuristic(self, heuristic: Heuristic) -> None:
        """Configure a specific heuristic's behavior."""
        setup_funcs = {
            'h1': setup_h1,
            'h2': setup_h2,
            'h3': setup_h3,
            'h4': setup_h4,
            'h5': setup_h5
        }
        
        if heuristic.name in setup_funcs:
            setup_funcs[heuristic.name](heuristic)

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