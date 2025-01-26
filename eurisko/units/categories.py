"""Category units for PyEurisko."""

from typing import Dict, Any
from ..unit import Unit, UnitRegistry

def initialize_category_units(registry: UnitRegistry) -> None:
    """Initialize category-related units."""
    
    categories = {
        'HEURISTIC': {
            'worth': 900,
            'isa': ['category', 'anything'],
            'examples': [
                'H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'H7', 'H8', 'H9', 'H10',
                'H11', 'H12', 'H13', 'H14', 'H15', 'H16', 'H17', 'H18', 'H19', 'H20'
            ],
            'generalizations': ['OP', 'ANYTHING'],
            'specializations': ['HIND-SIGHT-RULE']
        },
        'MATH-OBJ': {
            'worth': 500,
            'isa': ['category', 'math-concept', 'anything'],
            'examples': [
                'NNUMBER', 'PRIME-NUM', 'PERF-NUM', 'PERF-SQUARE', 'ODD-NUM',
                'EVEN-NUM', 'SET', 'SET-OF-NUMBERS', 'BIT'
            ],
            'generalizations': ['MATH-CONCEPT', 'ANYTHING']
        },
        'MATH-OP': {
            'worth': 500,
            'isa': ['category', 'math-concept', 'anything'],
            'examples': [
                'ADD', 'MULTIPLY', 'SQUARE', 'DIVISORS-OF', 'SUCCESSOR',
                'SET-UNION', 'SET-INTERSECT', 'LIST-UNION', 'BAG-UNION'
            ],
            'generalizations': ['MATH-CONCEPT', 'OP', 'ANYTHING']
        },
        'BINARY-OP': {
            'worth': 500,
            'isa': ['category', 'anything'],
            'examples': [
                'ADD', 'MULTIPLY', 'SET-UNION', 'SET-INTERSECT',
                'AND', 'OR', 'IMPLIES'
            ],
            'generalizations': ['OP', 'ANYTHING'],
            'specializations': ['BINARY-PRED']
        },
        'UNARY-OP': {
            'worth': 500,
            'isa': ['category', 'anything'],
            'examples': [
                'SQUARE', 'SUCCESSOR', 'NOT', 'DIVISORS-OF'
            ],
            'generalizations': ['OP', 'ANYTHING'],
            'specializations': ['UNARY-PRED']
        },
        'BINARY-PRED': {
            'worth': 500,
            'isa': ['category', 'anything'],
            'examples': [
                'EQUAL', 'IMPLIES', 'AND', 'OR', 'IEQP', 'ILESSP', 'IGREATERP'
            ],
            'generalizations': ['BINARY-OP', 'PRED', 'ANYTHING']
        },
        'UNARY-PRED': {
            'worth': 500,
            'isa': ['category', 'anything'],
            'examples': ['NOT'],
            'generalizations': ['UNARY-OP', 'PRED', 'ANYTHING']
        }
    }

    for name, props in categories.items():
        unit = registry.create_unit(name, worth=props['worth'])
        for prop, value in props.items():
            if prop != 'worth':
                unit.set_prop(prop, value)
