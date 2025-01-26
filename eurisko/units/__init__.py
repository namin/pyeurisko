"""Unit definitions package for PyEurisko."""

from typing import Any, Dict, List, Optional, Set, Union, Callable
import random
from copy import deepcopy
from ..interfaces import EuriskoObject
from ..slots import SlotRegistry

class Unit(EuriskoObject):
    """Base class for all Eurisko concepts/units."""
    def __post_init__(self):
        """Initialize unit properties."""
        super().__post_init__()

    def get_algorithm(self) -> Optional[Callable]:
        """Get the best available algorithm implementation."""
        for alg_type in ['fast_alg', 'alg', 'recursive_alg', 'iterative_alg', 'unitized_alg']:
            alg = self.get_prop(alg_type)
            if callable(alg):
                return alg
        return None

    def apply_algorithm(self, args: List[Any]) -> Any:
        """Apply the unit's algorithm to arguments."""
        alg = self.get_algorithm()
        if alg:
            try:
                return alg(*args)
            except Exception as e:
                logger.error(f"Algorithm execution failed: {e}")
                return None
        return None
        
    # Alias for compatibility with tests
    apply_alg = apply_algorithm

    def get_definition(self) -> Optional[Callable]:
        """Get the best available definition implementation."""
        for defn_type in ['fast_defn', 'defn', 'recursive_defn', 'unitized_defn', 'iterative_defn']:
            defn = self.get_prop(defn_type)
            if callable(defn):
                return defn
        return None

    def merge_props(self, other_unit: 'Unit', criterial_only: bool = False) -> None:
        """Merge properties from another unit."""
        registry = SlotRegistry()
        for prop_name, value in other_unit.properties.items():
            # Skip system properties
            if prop_name in ['worth', 'name']:
                continue
                
            # Check if we should only copy criterial slots
            if criterial_only:
                slot = registry.get_slot(prop_name)
                if not slot or not slot.get_prop('is_criterial'):
                    continue
                    
            # Don't copy certain slots
            slot = registry.get_slot(prop_name)
            if slot and slot.get_prop('dont_copy'):
                continue
                
            # Merge lists, replace non-lists
            current = self.get_prop(prop_name)
            if isinstance(current, list) and isinstance(value, list):
                merged = list(set(current + value))  # Remove duplicates
                self.set_prop(prop_name, merged)
            else:
                self.set_prop(prop_name, deepcopy(value))

    def copy_unit(self, new_name: str) -> 'Unit':
        """Create a copy of this unit with a new name."""
        new_unit = Unit(new_name, self.worth)
        new_unit.merge_props(self)
        return new_unit

    def isa(self) -> List[str]:
        """Get categories this unit belongs to."""
        return self.get_prop('isa') or []

    def is_a(self, category: str) -> bool:
        """Check if unit belongs to category."""
        return category in self.isa()

    def examples(self) -> List[str]:
        """Get examples of this unit."""
        return self.get_prop('examples') or []

    def add_example(self, example: str) -> None:
        """Add a new example."""
        self.add_prop('examples', example)

    def specializations(self) -> List[str]:
        """Get specializations of this unit."""
        return self.get_prop('specializations') or []

    def add_specialization(self, spec: str) -> None:
        """Add a specialization relationship."""
        self.add_prop('specializations', spec)

    def generalizations(self) -> List[str]:
        """Get generalizations of this unit."""
        return self.get_prop('generalizations') or []

    def add_generalization(self, gen: str) -> None:
        """Add a generalization relationship."""
        self.add_prop('generalizations', gen)

    # Equality operations
    def __eq__(self, other: 'Unit') -> bool:
        """Units are equal if they have the same name."""
        return isinstance(other, Unit) and self.name == other.name

    def __hash__(self) -> int:
        """Hash based on unit name."""
        return hash(self.name)

    def has_application(self, args: List[Any]) -> bool:
        """Check if this unit has a recorded application with given args."""
        applications = self.get_prop('applications') or []
        for app in applications:
            if isinstance(app, dict):
                if app.get('args') == args:
                    return True
            elif isinstance(app, (list, tuple)) and len(app) >= 1:
                if app[0] == args:
                    return True
        return False

    def add_application(self, args: List[Any], result: Any, worth: int = 500) -> None:
        """Record a new application of this unit."""
        app = {'args': args, 'result': result, 'worth': worth}
        applications = self.get_prop('applications', [])
        if not isinstance(applications, list):
            applications = []
        applications.append(app)
        self.set_prop('applications', applications)

    def add_to_prop(self, prop_name: str, value: Any) -> None:
        """Add a value to a property, creating a list if needed."""
        current = self.get_prop(prop_name)
        if current is None:
            self.set_prop(prop_name, [value])
        elif isinstance(current, list):
            if value not in current:  # Avoid duplicates
                current.append(value)
                self.set_prop(prop_name, current)
        else:  # Convert to list
            self.set_prop(prop_name, [current, value])

    def copy_slots_from(self, other_unit: 'Unit') -> None:
        """Copy all slots from another unit except name/system properties."""
        for slot_name, value in other_unit.properties.items():
            if slot_name not in ['name', 'worth', 'isa']:
                self.set_prop(slot_name, deepcopy(value))

class UnitRegistry:
    """Global registry of all units in the system."""
    _instance = None
    _units: Dict[str, Unit] = {}
    _units_by_category: Dict[str, Set[str]] = {}
    _deleted_units: Set[str] = set()

    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def register(self, unit: Unit) -> None:
        """Register a unit in the system."""
        if unit.name in self._deleted_units:
            logger.warning(f"Attempting to register previously deleted unit: {unit.name}")
            return
            
        self._units[unit.name] = unit
        # Update category index
        for category in unit.isa():
            if category not in self._units_by_category:
                self._units_by_category[category] = set()
            self._units_by_category[category].add(unit.name)

    def unregister(self, unit_name: str) -> None:
        """Remove a unit from the system."""
        if unit_name in self._units:
            unit = self._units[unit_name]
            # Remove from category index
            for category in unit.isa():
                if category in self._units_by_category:
                    self._units_by_category[category].discard(unit_name)
            del self._units[unit_name]
            self._deleted_units.add(unit_name)

    def get_unit(self, name: str) -> Optional[Unit]:
        """Get a unit by name."""
        return self._units.get(name)

    def get_units_by_category(self, category: str) -> Set[str]:
        """Get all units in a category."""
        return self._units_by_category.get(category, set())

    def all_units(self) -> Dict[str, Unit]:
        """Get all registered units."""
        return self._units.copy()

    def create_unit(self, name: str, worth: int = 500, isa: List[str] = None) -> Unit:
        """Create and register a new unit."""
        if name in self._units:
            logger.warning(f"Unit {name} already exists")
            return self._units[name]
            
        unit = Unit(name, worth)
        if isa:
            unit.set_prop('isa', isa)
        self.register(unit)
        return unit

def initialize_all_units(registry) -> None:
    pass
