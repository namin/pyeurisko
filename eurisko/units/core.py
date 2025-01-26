"""Core unit definitions for PyEurisko."""

from typing import Dict, Any, List
from ..unit import Unit, UnitRegistry

def initialize_core_units(registry: UnitRegistry) -> None:
    """Initialize the core foundational units."""
    
    # ANYTHING is the root of all concepts
    anything = registry.create_unit('ANYTHING', worth=550)
    anything.set_prop('isa', ['category'])
    anything.set_prop('examples', [
        'AND', 'OR', 'THE-FIRST-OF', 'THE-SECOND-OF', 'SQUARE',
        'DIVISORS-OF', 'MULTIPLY', 'ADD', 'SUCCESSOR'
    ])

    # Core representational units
    repr_units = {
        'CATEGORY': {
            'worth': 500,
            'isa': ['category', 'anything'],
            'examples': [
                'SET', 'HEURISTIC', 'SLOT', 'MATH-OBJ', 'NNUMBER',
                'UNIT', 'PRIME-NUM', 'CONJECTURE', 'REPR-CONCEPT'
            ]
        },
        'SLOT': {
            'worth': 500,
            'isa': ['category', 'anything'],
            'examples': [
                'ALG', 'APPLIC-GENERATOR', 'DATA-TYPE', 'DEFN',
                'DOMAIN', 'ELIM-SLOTS', 'FAST-ALG', 'FAST-DEFN'
            ]
        },
        'MATH-CONCEPT': {
            'worth': 500,
            'isa': ['category', 'anything'],
            'examples': [
                'NNUMBER', 'PRIME-NUM', 'PERF-NUM', 'PERF-SQUARE',
                'ODD-NUM', 'EVEN-NUM', 'SQUARE', 'DIVISORS-OF'
            ]
        },
        'HEURISTIC': {
            'worth': 900,
            'isa': ['category', 'anything', 'op'],
            'examples': [
                'H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'H7', 'H8', 'H9', 'H10',
                'H11', 'H12', 'H13', 'H14', 'H15', 'H16', 'H17', 'H18', 'H19'
            ],
            # Initialize task phase handlers as lists of functions
            'if_about_to_work_on_task': [],  # List of applicable heuristics
            'if_finished_working_on_task': [],
            'if_working_on_task': [],
            'if_potentially_relevant': [],
            'if_truly_relevant': [],
            'domain': ['anything'],
            'range': ['anything'],
            'fast_alg': [],  # Will be populated by specific heuristics
            'english': 'A rule for discovering or refining concepts and methods'
        }
    }

    # Create core units first
    for name, props in repr_units.items():
        unit = registry.create_unit(name.upper(), worth=props['worth'])  # Ensure uppercase
        for prop, value in props.items():
            if prop != 'worth':
                unit.set_prop(prop.lower(), value)  # Properties are lowercase

    # Now create essential slots that all units need
    essential_slots = {
        'ISA': {
            'worth': 300,
            'isa': ['slot', 'non-criterial-slot', 'anything'],
            'inverse': 'examples',
            'data_type': 'unit',
            'double_check': True
        },
        'WORTH': {
            'worth': 300,
            'isa': ['slot', 'non-criterial-slot', 'anything'],
            'data_type': 'number'
        },
        'ENGLISH': {
            'worth': 300,
            'isa': ['slot', 'non-criterial-slot', 'anything'],
            'data_type': 'text'
        },
        'DOMAIN': {
            'worth': 600,
            'isa': ['slot', 'criterial-slot', 'anything'],
            'data_type': 'unit',
            'inverse': 'in_domain_of'
        },
        'RANGE': {
            'worth': 600,
            'isa': ['slot', 'criterial-slot', 'anything'],
            'data_type': 'unit',
            'inverse': 'is_range_of'
        }
    }

    # Create slot units
    for name, props in essential_slots.items():
        unit = registry.create_unit(name.upper(), worth=props['worth'])
        for prop, value in props.items():
            if prop != 'worth':
                unit.set_prop(prop.lower(), value)

    # Add core behavioral properties to anything
    anything.set_prop('if_about_to_work_on_task', [])
    anything.set_prop('if_working_on_task', [])
    anything.set_prop('if_finished_working_on_task', [])
    anything.set_prop('if_potentially_relevant', [])
    anything.set_prop('if_truly_relevant', [])
    anything.set_prop('english', 'The root concept, parent of all concepts')
