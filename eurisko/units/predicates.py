"""Predicate units for PyEurisko."""

from typing import Dict, Any
from ..unit import Unit, UnitRegistry

def initialize_predicate_units(registry: UnitRegistry) -> None:
    """Initialize predicate units."""
    
    predicates = {
        'EQUAL': {
            'worth': 502,
            'isa': ['math-concept', 'math-op', 'math-pred', 'binary-pred', 'anything'],
            'arity': 2,
            'domain': ['anything', 'anything'],
            'range': 'bit',
            'fast_alg': lambda x, y: x == y
        },
        'IMPLIES': {
            'worth': 500,
            'isa': ['math-concept', 'math-op', 'math-pred', 'binary-pred', 'anything'],
            'arity': 2,
            'domain': ['anything', 'anything'],
            'range': 'bit',
            'fast_alg': lambda x, y: (not x) or y
        },
        'AND': {
            'worth': 569,
            'isa': ['math-concept', 'math-op', 'math-pred', 'binary-pred', 'anything'],
            'arity': 2,
            'domain': ['anything', 'anything'],
            'range': 'anything',
            'fast_alg': lambda x, y: x and y
        },
        'OR': {
            'worth': 500,
            'isa': ['math-concept', 'math-op', 'math-pred', 'binary-pred', 'anything'],
            'arity': 2,
            'domain': ['anything', 'anything'],
            'range': 'anything',
            'fast_alg': lambda x, y: x or y
        },
        'NOT': {
            'worth': 500,
            'isa': ['math-concept', 'math-op', 'math-pred', 'unary-pred', 'anything'],
            'arity': 1,
            'domain': ['anything'],
            'range': 'bit',
            'fast_alg': lambda x: not x
        },
        'IEQP': {  # Integer equality
            'worth': 500,
            'isa': ['math-concept', 'math-op', 'math-pred', 'binary-pred', 'anything'],
            'arity': 2,
            'domain': ['nnumber', 'nnumber'],
            'range': 'bit',
            'fast_alg': lambda x, y: x == y,
            'generalizations': ['EQUAL', 'ILEQ', 'IGEQ']
        },
        'ILESSP': {  # Integer less than
            'worth': 500,
            'isa': ['math-concept', 'math-op', 'math-pred', 'binary-pred', 'anything'],
            'arity': 2,
            'domain': ['nnumber', 'nnumber'],
            'range': 'bit',
            'fast_alg': lambda x, y: x < y,
            'generalizations': ['ILEQ']
        },
        'IGREATERP': {  # Integer greater than
            'worth': 501,
            'isa': ['math-concept', 'math-op', 'math-pred', 'binary-pred', 'anything'],
            'arity': 2,
            'domain': ['nnumber', 'nnumber'],
            'range': 'bit',
            'fast_alg': lambda x, y: x > y,
            'generalizations': ['IGEQ']
        },
        'ILEQ': {  # Integer less than or equal
            'worth': 500,
            'isa': ['math-concept', 'math-op', 'math-pred', 'binary-pred', 'anything'],
            'arity': 2,
            'domain': ['nnumber', 'nnumber'],
            'range': 'bit',
            'fast_alg': lambda x, y: x <= y,
            'specializations': ['IEQP', 'ILESSP']
        },
        'IGEQ': {  # Integer greater than or equal
            'worth': 509,
            'isa': ['math-concept', 'math-op', 'math-pred', 'binary-pred', 'anything'],
            'arity': 2,
            'domain': ['nnumber', 'nnumber'],
            'range': 'bit',
            'fast_alg': lambda x, y: x >= y,
            'specializations': ['IEQP', 'IGREATERP']
        }
    }

    for name, props in predicates.items():
        unit = registry.create_unit(name, worth=props['worth'])
        for prop, value in props.items():
            if prop != 'worth':
                unit.set_prop(prop, value)
