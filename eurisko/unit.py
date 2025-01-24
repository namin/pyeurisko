from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Union, Callable
import random

@dataclass
class Unit:
    """Base class for all Eurisko concepts/units."""
    name: str
    worth: int = 500
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize any default properties."""
        if 'worth' not in self.properties:
            self.properties['worth'] = self.worth
            
    def get_prop(self, prop_name: str) -> Any:
        """Get a property value."""
        return self.properties.get(prop_name)
        
    def set_prop(self, prop_name: str, value: Any) -> None:
        """Set a property value."""
        self.properties[prop_name] = value
        
    def add_prop(self, prop_name: str, value: Any, to_head: bool = False) -> None:
        """Add a value to a list property."""
        current = self.properties.get(prop_name, [])
        if not isinstance(current, list):
            current = []
        if to_head:
            current.insert(0, value)
        else:
            current.append(value)
        self.properties[prop_name] = current

    def remove_prop(self, prop_name: str, value: Any = None) -> None:
        """Remove a property or a specific value from a list property."""
        if value is None:
            self.properties.pop(prop_name, None)
        else:
            current = self.properties.get(prop_name, [])
            if isinstance(current, list) and value in current:
                current.remove(value)

    def has_prop(self, prop_name: str) -> bool:
        """Check if a property exists."""
        return prop_name in self.properties

    def isa(self) -> List[str]:
        """Get the categories this unit belongs to."""
        return self.properties.get('isa', [])

    def worth_value(self) -> int:
        """Get the worth value."""
        return self.properties.get('worth', 500)

    def examples(self) -> List[str]:
        """Get examples of this unit."""
        return self.properties.get('examples', [])

    def specializations(self) -> List[str]:
        """Get specializations of this unit."""
        return self.properties.get('specializations', [])

    def generalizations(self) -> List[str]:
        """Get generalizations of this unit."""
        return self.properties.get('generalizations', [])

    def apply_alg(self, args: List[Any]) -> Any:
        """Apply the algorithm defined by this unit."""
        alg = self.properties.get('fast_alg')
        if alg and callable(alg):
            return alg(*args)
        return None

    def __eq__(self, other: 'Unit') -> bool:
        """Units are equal if they have the same name."""
        return isinstance(other, Unit) and self.name == other.name

    def __hash__(self) -> int:
        """Hash based on unit name."""
        return hash(self.name)

class UnitRegistry:
    """Global registry of all units in the system."""
    _instance = None
    _units: Dict[str, Unit] = {}
    _units_by_category: Dict[str, Set[str]] = {}

    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def register(self, unit: Unit) -> None:
        """Register a unit in the system."""
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

    def get_unit(self, name: str) -> Optional[Unit]:
        """Get a unit by name."""
        return self._units.get(name)

    def get_units_by_category(self, category: str) -> Set[str]:
        """Get all units in a category."""
        return self._units_by_category.get(category, set())

    def all_units(self) -> Dict[str, Unit]:
        """Get all registered units."""
        return self._units.copy()
