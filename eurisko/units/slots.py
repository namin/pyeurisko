"""Slot units for PyEurisko."""

from typing import Dict, Any
from ..unit import Unit, UnitRegistry

def initialize_slot_units(registry: UnitRegistry) -> None:
    """Initialize slot-related units."""
    
    slots = {
        'ISA': {
            'worth': 300,
            'isa': ['slot', 'non-criterial-slot', 'anything'],
            'inverse': 'EXAMPLES',
            'data_type': 'unit',
            'double_check': True
        },
        'EXAMPLES': {
            'worth': 300,
            'isa': ['slot', 'non-criterial-slot', 'anything'],
            'inverse': 'ISA',
            'data_type': 'unit',
            'double_check': True,
            'dont_copy': True,
            'sub_slots': ['INT-EXAMPLES'],
            'more_interesting': ['INT-EXAMPLES']
        },
        'WORTH': {
            'worth': 300,
            'isa': ['slot', 'non-criterial-slot', 'anything'],
            'data_type': 'number'
        },
        'GENERALIZATIONS': {
            'worth': 306,
            'isa': ['slot', 'non-criterial-slot', 'anything'],
            'inverse': 'SPECIALIZATIONS',
            'data_type': 'unit',
            'double_check': True,
            'sub_slots': ['SUPER-SLOTS', 'EXTENSIONS']
        },
        'SPECIALIZATIONS': {
            'worth': 300,
            'isa': ['slot', 'non-criterial-slot', 'anything'],
            'inverse': 'GENERALIZATIONS',
            'data_type': 'unit',
            'double_check': True
        },
        'DOMAIN': {
            'worth': 600,
            'isa': ['slot', 'criterial-slot', 'anything'],
            'data_type': 'unit',
            'inverse': 'IN-DOMAIN-OF'
        },
        'RANGE': {
            'worth': 600,
            'isa': ['slot', 'criterial-slot', 'anything'],
            'data_type': 'unit',
            'inverse': 'IS-RANGE-OF'
        },
        'FAST-ALG': {
            'worth': 600,
            'isa': ['slot', 'criterial-slot', 'anything'],
            'data_type': 'lisp-fn',
            'super_slots': ['ALG'],
            'dont_copy': True
        },
        'RECURSIVE-ALG': {
            'worth': 600,
            'isa': ['slot', 'criterial-slot', 'anything'],
            'data_type': 'lisp-fn',
            'super_slots': ['ALG']
        },
        'ARITY': {
            'worth': 300,
            'isa': ['slot', 'non-criterial-slot', 'anything'],
            'data_type': 'number'
        }
    }

    for name, props in slots.items():
        unit = registry.create_unit(name, worth=props['worth'])
        for prop, value in props.items():
            if prop != 'worth':
                unit.set_prop(prop, value)
