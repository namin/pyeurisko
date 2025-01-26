"""Structure units for PyEurisko."""

from typing import Dict, Any
from ..unit import Unit, UnitRegistry

def initialize_structure_units(registry: UnitRegistry) -> None:
    """Initialize structure-related units."""
    
    structures = {
        'STRUCTURE': {
            'worth': 500,
            'isa': ['math-concept', 'math-obj', 'anything'],
            'specializations': ['SET', 'LIST', 'BAG', 'MULT-ELE-STRUC', 'O-SET'],
            'examples': []
        },
        'SET': {
            'worth': 500,
            'isa': ['structure', 'math-concept', 'math-obj', 'anything'],
            'fast_defn': lambda s: isinstance(s, set),
            'in_domain_of': ['SET-INSERT', 'SET-DELETE', 'SET-UNION', 'SET-INTERSECT'],
            'examples': []
        },
        'LIST': {
            'worth': 500,
            'isa': ['structure', 'math-concept', 'math-obj', 'anything'],
            'fast_defn': lambda s: isinstance(s, list),
            'in_domain_of': ['LIST-INSERT', 'LIST-DELETE', 'LIST-UNION', 'LIST-INTERSECT'],
            'examples': []
        },
        'BAG': {  # Multiset implementation
            'worth': 500,
            'isa': ['structure', 'math-concept', 'math-obj', 'anything'],
            'fast_defn': lambda s: isinstance(s, dict),
            'in_domain_of': ['BAG-INSERT', 'BAG-DELETE', 'BAG-UNION', 'BAG-INTERSECT'],
            'examples': []
        },
        'O-SET': {  # Ordered set
            'worth': 500,
            'isa': ['structure', 'set', 'math-concept', 'math-obj', 'anything'],
            'fast_defn': lambda s: isinstance(s, list) and len(s) == len(set(s)),
            'in_domain_of': ['O-SET-INSERT', 'O-SET-DELETE', 'O-SET-UNION', 'O-SET-INTERSECT'],
            'examples': []
        }
    }

    # Structure operations
    structure_ops = {
        'SET-INSERT': {
            'worth': 500,
            'isa': ['math-concept', 'math-op', 'struc-op', 'binary-op', 'anything'],
            'arity': 2,
            'domain': ['anything', 'set'],
            'range': 'set',
            'fast_alg': lambda x, s: s.union({x})
        },
        'LIST-INSERT': {
            'worth': 500,
            'isa': ['math-concept', 'math-op', 'struc-op', 'binary-op', 'anything'],
            'arity': 2,
            'domain': ['anything', 'list'],
            'range': 'list',
            'fast_alg': lambda x, l: l + [x]
        },
        'BAG-INSERT': {
            'worth': 500,
            'isa': ['math-concept', 'math-op', 'struc-op', 'binary-op', 'anything'],
            'arity': 2,
            'domain': ['anything', 'bag'],
            'range': 'bag',
            'fast_alg': lambda x, b: {k: v + (1 if k == x else 0) for k, v in b.items()}
        }
    }

    # Create structure units
    for name, props in structures.items():
        unit = registry.create_unit(name, worth=props['worth'])
        for prop, value in props.items():
            if prop != 'worth':
                unit.set_prop(prop, value)

    # Create structure operation units
    for name, props in structure_ops.items():
        unit = registry.create_unit(name, worth=props['worth'])
        for prop, value in props.items():
            if prop != 'worth':
                unit.set_prop(prop, value)
