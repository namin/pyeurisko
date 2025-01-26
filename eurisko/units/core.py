"""Core unit definitions for PyEurisko."""

from typing import Dict, Any, List
from ..units import Unit, UnitRegistry

def initialize_core_units(registry: UnitRegistry) -> None:
    """initialize the core foundational units."""
    
    # anything is the root of all concepts
    anything = registry.create_unit('anything', worth=550)
    anything.set_prop('isa', ['category'])
    anything.set_prop('examples', [
        'and', 'or', 'the-first-of', 'the-second-of', 'square',
        'divisors-of', 'multiply', 'add', 'successor'
    ])

    # Core representational units
    repr_units = {
        'category': {
            'worth': 500,
            'isa': ['category', 'anything'],
            'examples': [
                'set', 'heuristic', 'slot', 'math-obj', 'nnumber',
                'unit', 'prime-num', 'conjecture', 'repr-concept'
            ]
        },
        'slot': {
            'worth': 500,
            'isa': ['category', 'anything'],
            'examples': [
                'alg', 'applic-generator', 'data-type', 'defn',
                'domain', 'elim-slots', 'fast-alg', 'fast-defn'
            ]
        },
        'math-concept': {
            'worth': 500,
            'isa': ['category', 'anything'],
            'examples': [
                'nnumber', 'prime-num', 'perf-num', 'perf-square',
                'odd-num', 'even-num', 'square', 'divisors-of'
            ]
        },
        'heuristic': {
            'worth': 900,
            'isa': ['category', 'anything', 'op'],
            'examples': [
                'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'h8', 'h9', 'h10',
                'h11', 'h12', 'h13', 'h14', 'h15', 'h16', 'h17', 'h18', 'h19'
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
        'isa': {
            'worth': 300,
            'isa': ['slot', 'non-criterial-slot', 'anything'],
            'inverse': 'examples',
            'data_type': 'unit',
            'double_check': True
        },
        'worth': {
            'worth': 300,
            'isa': ['slot', 'non-criterial-slot', 'anything'],
            'data_type': 'number'
        },
        'english': {
            'worth': 300,
            'isa': ['slot', 'non-criterial-slot', 'anything'],
            'data_type': 'text'
        },
        'domain': {
            'worth': 600,
            'isa': ['slot', 'criterial-slot', 'anything'],
            'data_type': 'unit',
            'inverse': 'in_domain_of'
        },
        'range': {
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

