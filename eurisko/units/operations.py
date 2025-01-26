"""Operation units for PyEurisko."""

from typing import Dict, Any
from ..unit import Unit, UnitRegistry

def initialize_operation_units(registry: UnitRegistry) -> None:
    """Initialize operation units."""
    
    operations = {
        'ADD': {
            'worth': 500,
            'isa': ['math-concept', 'math-op', 'binary-op', 'anything'],
            'arity': 2,
            'domain': ['nnumber', 'nnumber'],
            'range': 'nnumber',
            'fast_alg': lambda x, y: x + y,
            'recursive_alg': lambda x, y: y if x == 0 else registry.run_alg('SUCCESSOR', 
                                                                          registry.run_alg('ADD', x-1, y))
        },
        'MULTIPLY': {
            'worth': 500,
            'isa': ['math-concept', 'math-op', 'binary-op', 'anything'],
            'arity': 2,
            'domain': ['nnumber', 'nnumber'],
            'range': 'nnumber',
            'fast_alg': lambda x, y: x * y,
            'recursive_alg': lambda x, y: 0 if x == 0 else registry.run_alg('ADD', y, 
                                                                          registry.run_alg('MULTIPLY', x-1, y))
        },
        'SQUARE': {
            'worth': 500,
            'isa': ['math-concept', 'math-op', 'unary-op', 'anything'],
            'arity': 1,
            'domain': ['nnumber'],
            'range': 'nnumber',
            'fast_alg': lambda x: x * x
        },
        'SUCCESSOR': {
            'worth': 500,
            'isa': ['math-concept', 'math-op', 'unary-op', 'anything'],
            'arity': 1,
            'domain': ['nnumber'],
            'range': 'nnumber',
            'fast_alg': lambda x: x + 1
        },
        'DIVISORS-OF': {
            'worth': 500,
            'isa': ['math-concept', 'math-op', 'unary-op', 'anything'],
            'arity': 1,
            'domain': ['nnumber'],
            'range': 'set-of-numbers',
            'fast_alg': lambda n: [i for i in range(1, n + 1) if n % i == 0]
        }
    }

    for name, props in operations.items():
        unit = registry.create_unit(name, worth=props['worth'])
        for prop, value in props.items():
            if prop != 'worth':
                unit.set_prop(prop, value)
