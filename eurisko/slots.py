from typing import Any, List, Dict, Set, Optional, Callable
from dataclasses import dataclass
from .unit import Unit, UnitRegistry

@dataclass
class Slot:
    """Base class for all slots/properties in Eurisko."""
    name: str
    is_criterial: bool = False  # Whether this is a criterial slot
    data_type: str = 'any'  # The type of data this slot holds
    dont_copy: bool = False  # Whether this slot should be copied during unit creation
    double_check: bool = False  # Whether values should be validated
    super_slots: List[str] = None  # Parent slots
    sub_slots: List[str] = None  # Child slots
    inverse: str = None  # Inverse relationship slot

    def __post_init__(self):
        self.super_slots = self.super_slots or []
        self.sub_slots = self.sub_slots or []

    def validate_value(self, value: Any) -> bool:
        """Validate a value for this slot."""
        # Basic type checking - could be extended
        if self.data_type == 'unit':
            return isinstance(value, (str, Unit))
        elif self.data_type == 'number':
            return isinstance(value, (int, float))
        elif self.data_type == 'text':
            return isinstance(value, str)
        elif self.data_type == 'bit':
            return value in (True, False, 0, 1)
        elif self.data_type == 'lisp_fn':
            return callable(value)
        return True  # 'any' type

class SlotRegistry:
    """Global registry of all slots in the system."""
    _instance = None
    _slots: Dict[str, Slot] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_core_slots()
        return cls._instance

    def _init_core_slots(self):
        """Initialize the core system slots."""
        # Basic properties
        self.register(Slot('worth', False, 'number'))
        self.register(Slot('isa', False, 'unit'))
        self.register(Slot('examples', False, 'unit', dont_copy=True))
        self.register(Slot('generalizations', False, 'unit'))
        self.register(Slot('specializations', False, 'unit'))
        self.register(Slot('domain', True, 'unit'))
        self.register(Slot('range', True, 'unit'))

        # Algorithm slots
        self.register(Slot('alg', True, 'lisp_fn', sub_slots=['fast_alg', 'iterative_alg', 
                                                             'recursive_alg', 'unitized_alg']))
        self.register(Slot('fast_alg', True, 'lisp_fn'))
        self.register(Slot('iterative_alg', True, 'lisp_fn'))
        self.register(Slot('recursive_alg', True, 'lisp_fn'))
        self.register(Slot('unitized_alg', True, 'lisp_fn'))

        # Definition slots  
        self.register(Slot('defn', True, 'lisp_fn', sub_slots=['fast_defn', 'recursive_defn',
                                                              'unitized_defn', 'iterative_defn']))
        self.register(Slot('fast_defn', True, 'lisp_fn'))
        self.register(Slot('recursive_defn', True, 'lisp_fn'))
        self.register(Slot('unitized_defn', True, 'lisp_fn'))
        self.register(Slot('iterative_defn', True, 'lisp_fn'))

        # Task execution slots
        self.register(Slot('if_parts', True, 'lisp_fn'))
        self.register(Slot('then_parts', True, 'lisp_fn'))
        self.register(Slot('if_working_on_task', True, 'lisp_fn'))
        self.register(Slot('if_about_to_work_on_task', True, 'lisp_fn'))
        self.register(Slot('if_finished_working_on_task', True, 'lisp_fn'))

        # Record keeping
        self.register(Slot('record', False, 'any', dont_copy=True))
        self.register(Slot('failed_record', False, 'any', dont_copy=True))
        self.register(Slot('overall_record', False, 'any', dont_copy=True))

    def register(self, slot: Slot) -> None:
        """Register a new slot type."""
        self._slots[slot.name] = slot

    def get_slot(self, name: str) -> Optional[Slot]:
        """Get a slot by name."""
        return self._slots.get(name)

    def exists(self, name: str) -> bool:
        """Check if a slot exists."""
        return name in self._slots

    def all_slots(self) -> Dict[str, Slot]:
        """Get all registered slots."""
        return self._slots.copy()

    def criterial_slots(self) -> List[str]:
        """Get all criterial slots."""
        return [name for name, slot in self._slots.items() if slot.is_criterial]

    def non_criterial_slots(self) -> List[str]:
        """Get all non-criterial slots."""
        return [name for name, slot in self._slots.items() if not slot.is_criterial]
