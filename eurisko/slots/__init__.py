"""Slot definitions package for PyEurisko."""

"""Core slots implementation for PyEurisko."""
from typing import Any, List, Dict, Set, Optional, Callable
from ..interfaces import EuriskoObject

class Slot(EuriskoObject):
    """Base class for all slots/properties in Eurisko."""
    def __post_init__(self):
        """Initialize slot properties."""
        super().__post_init__()
        self.set_prop('isa', ['slot'])

        # Store data type info
        self.set_prop('data_type', self.data_type)
        self.set_prop('is_criterial', self.is_criterial)
        self.set_prop('dont_copy', self.dont_copy)

    def validate_value(self, value: Any) -> bool:
        """Validate a value for this slot."""
        data_type = self.data_type  # Use constructor param
        
        if not data_type or data_type == 'any':
            return True
            
        if data_type == 'number':
            return isinstance(value, (int, float))
        elif data_type == 'text':
            return isinstance(value, str)
        elif data_type == 'bit':
            return value in (True, False, 0, 1)
        elif data_type == 'unit':
            # Import here to avoid circular imports
            from ..units import Unit
            return isinstance(value, (str, Unit))
        elif data_type == 'lisp_fn':
            return callable(value)
            
        return False  # Unknown types should fail validation

    @property
    def inverse(self) -> Optional[str]:
        """Get the inverse slot name."""
        return self.get_prop('inverse')
    
    @inverse.setter 
    def inverse(self, value: Optional[str]) -> None:
        """Set the inverse slot name."""
        self.set_prop('inverse', value)


class SlotRegistry:
    """Global registry of all slots in the system."""
    _instance = None
    _slots: Dict[str, Slot] = {}

    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._slots = {}  # Reset slots on new instance
            cls._instance._init_core_slots()
        return cls._instance

    def _init_core_slots(self):
        """Initialize the core system slots from Eurisko."""
        # Identity slots
        core_slots = [
            # Basic properties
            ('worth', 'number', False, False, 'Base value/importance of the unit'),
            ('isa', 'unit', False, False, 'Categories this unit belongs to'),
            ('abbrev', 'text', False, False, 'Short description of the unit'),
            ('english', 'text', False, False, 'Longer description of the unit'),
            
            # Core relations
            ('examples', 'unit', False, True, 'Known instances/examples of this unit'),
            ('non_examples', 'unit', False, True, 'Known non-instances of this unit'),
            ('generalizations', 'unit', False, False, 'More general forms of this unit'),
            ('specializations', 'unit', False, False, 'More specific forms of this unit'),
            ('domain', 'unit', True, False, 'Input types this unit accepts'),
            ('range', 'unit', True, False, 'Output types this unit produces'),
            
            # Algorithm implementations
            ('alg', 'lisp_fn', True, False, 'Main algorithm implementation'),
            ('fast_alg', 'lisp_fn', True, False, 'Optimized algorithm implementation'),
            ('recursive_alg', 'lisp_fn', True, False, 'Recursive algorithm implementation'), 
            ('iterative_alg', 'lisp_fn', True, False, 'Iterative algorithm implementation'),
            ('unitized_alg', 'lisp_fn', True, False, 'Unit-based algorithm implementation'),
            
            # Definition implementations
            ('defn', 'lisp_fn', True, False, 'Main definition implementation'),
            ('fast_defn', 'lisp_fn', True, False, 'Optimized definition implementation'),
            ('recursive_defn', 'lisp_fn', True, False, 'Recursive definition implementation'),
            ('iterative_defn', 'lisp_fn', True, False, 'Iterative definition implementation'),
            ('unitized_defn', 'lisp_fn', True, False, 'Unit-based definition implementation'),
            
            # Task execution
            ('if_parts', 'lisp_fn', True, False, 'Conditions for task execution'),
            ('then_parts', 'lisp_fn', True, False, 'Actions for task execution'),
            ('if_working_on_task', 'lisp_fn', True, False, 'Active task conditions'),
            ('if_about_to_work_on_task', 'lisp_fn', True, False, 'Pre-task conditions'),
            ('if_finished_working_on_task', 'lisp_fn', True, False, 'Post-task conditions'),
            
            # Record keeping
            ('record', 'any', False, True, 'Execution history'),
            ('failed_record', 'any', False, True, 'Failed execution history'),
            ('overall_record', 'any', False, True, 'Aggregate execution statistics'),
        ]
        
        # Register each core slot
        for name, dtype, criterial, no_copy, desc in core_slots:
            self.register(Slot(name, 
                             data_type=dtype,
                             is_criterial=criterial,
                             dont_copy=no_copy,
                             description=desc))

        # Set up relationships between algorithm slots
        alg_slot = self.get_slot('alg')
        if alg_slot:
            alg_slot.set_prop('sub_slots', ['fast_alg', 'recursive_alg', 'iterative_alg', 'unitized_alg'])
            
        # Set up relationships between definition slots  
        defn_slot = self.get_slot('defn')
        if defn_slot:
            defn_slot.set_prop('sub_slots', ['fast_defn', 'recursive_defn', 'iterative_defn', 'unitized_defn'])
            
        # Set up inverse relationships
        self.get_slot('generalizations').set_prop('inverse', 'specializations')
        self.get_slot('specializations').set_prop('inverse', 'generalizations')
        self.get_slot('domain').set_prop('inverse', 'range')
        self.get_slot('range').set_prop('inverse', 'domain')

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
        return [name for name, slot in self._slots.items() 
                if slot.is_criterial]  # Use the constructor param

    def non_criterial_slots(self) -> List[str]:
        """Get all non-criterial slots."""
        return [name for name, slot in self._slots.items()
                if not slot.is_criterial]  # Use the constructor param

def initialize_all_slots(registry) -> None:
    pass
