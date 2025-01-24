"""Core slots implementation for PyEurisko."""
from typing import Any, List, Dict, Set, Optional, Callable
from dataclasses import dataclass, field
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
    description: str = ''  # Documentation

    def __post_init__(self):
        """Initialize list fields."""
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
        """Initialize the core system slots from Eurisko."""
        # Identity slots
        self.register(Slot('worth', data_type='number', 
                          description='Base value/importance of the unit'))
        self.register(Slot('isa', data_type='unit',
                          description='Categories this unit belongs to'))
        self.register(Slot('abbrev', data_type='text',
                          description='Short description of the unit'))
        
        # Structural relation slots
        self.register(Slot('examples', data_type='unit', dont_copy=True,
                          description='Known instances/examples of this unit'))
        self.register(Slot('non_examples', data_type='unit', dont_copy=True,
                          description='Known non-instances of this unit'))
        self.register(Slot('generalizations', data_type='unit',
                          description='More general forms of this unit'))
        self.register(Slot('specializations', data_type='unit',
                          description='More specific forms of this unit'))
        self.register(Slot('domain', is_criterial=True, data_type='unit',
                          description='Input types this unit accepts'))
        self.register(Slot('range', is_criterial=True, data_type='unit',
                          description='Output types this unit produces'))
        self.register(Slot('inverse', data_type='unit',
                          description='Inverse relationship to this unit'))

        # Algorithm slots
        alg_slots = [
            ('alg', True, ['fast_alg', 'recursive_alg', 'iterative_alg', 'unitized_alg']),
            ('fast_alg', True, []),
            ('recursive_alg', True, []),
            ('iterative_alg', True, []),
            ('unitized_alg', True, [])
        ]
        for name, is_criterial, sub_slots in alg_slots:
            self.register(Slot(name, is_criterial=is_criterial, data_type='lisp_fn',
                             sub_slots=sub_slots,
                             description=f'{name} implementation'))

        # Definition slots  
        defn_slots = [
            ('defn', True, ['fast_defn', 'recursive_defn', 'unitized_defn', 'iterative_defn']),
            ('fast_defn', True, []),
            ('recursive_defn', True, []),
            ('unitized_defn', True, []),
            ('iterative_defn', True, [])
        ]
        for name, is_criterial, sub_slots in defn_slots:
            self.register(Slot(name, is_criterial=is_criterial, data_type='lisp_fn',
                             sub_slots=sub_slots,
                             description=f'{name} implementation'))

        # Task execution slots
        task_slots = [
            'if_parts', 'then_parts', 
            'if_working_on_task', 'if_about_to_work_on_task', 
            'if_finished_working_on_task'
        ]
        for name in task_slots:
            self.register(Slot(name, is_criterial=True, data_type='lisp_fn',
                             description=f'{name} handler for task execution'))

        # Record keeping slots
        record_slots = [
            'record', 'failed_record', 'overall_record',
            'then_compute_record', 'then_print_to_user_record',
            'then_conjecture_record', 'then_define_new_concepts_record',
            'failed_record_for', 'record_for'
        ]
        for name in record_slots:
            self.register(Slot(name, dont_copy=True,
                             description=f'{name} history'))

        # Application slots
        self.register(Slot('applics', data_type='any', dont_copy=True,
                          description='Known applications of this unit'))
        self.register(Slot('direct_applics', data_type='any',
                          description='Direct applications of this unit'))
        self.register(Slot('indirect_applics', data_type='any',
                          description='Indirect applications of this unit'))
        self.register(Slot('applic_generator', data_type='any',
                          description='Generator for finding applications'))

        # Property validation slots
        self.register(Slot('double_check', data_type='bit',
                          description='Whether to validate values'))
        self.register(Slot('dont_copy', data_type='bit',  
                          description='Whether to copy during inheritance'))
        self.register(Slot('data_type', data_type='text',
                          description='Expected type for values'))

        # Structural slots
        self.register(Slot('sib_slots', data_type='unit',
                          description='Related peer slots'))
        self.register(Slot('sub_slots', data_type='unit',
                          description='Child slots'))
        self.register(Slot('super_slots', data_type='unit',
                          description='Parent slots'))

        # Interestingness/importance slots
        self.register(Slot('interestingness', data_type='lisp_fn',
                          description='Function determining interest level'))
        self.register(Slot('int_examples', data_type='unit',
                          description='Particularly interesting examples'))
        self.register(Slot('less_interesting', data_type='unit',
                          description='Less interesting similar units'))
        self.register(Slot('more_interesting', data_type='unit',
                          description='More interesting similar units'))
        self.register(Slot('why_int', data_type='any',
                          description='Explanation of interestingness'))

        # Heuristic-specific slots
        self.register(Slot('creditors', data_type='unit', dont_copy=True,
                          description='Units that helped create this'))
        self.register(Slot('english', data_type='text',
                          description='English description of the unit'))
        self.register(Slot('if_potentially_relevant', data_type='lisp_fn',
                          description='Initial relevance check'))
        self.register(Slot('if_truly_relevant', data_type='lisp_fn',
                          description='Deeper relevance check'))

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
