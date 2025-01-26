"""Mathematical units for PyEurisko."""

from typing import Dict, Any
from ..unit import Unit, UnitRegistry

def initialize_math_units(registry: UnitRegistry) -> None:
    """Initialize mathematical object units."""
    
    # Basic number types
    number_units = {
        'NNUMBER': {
            'worth': 500,
            'isa': ['math-concept', 'math-obj', 'anything'],
            'fast_defn': lambda n: isinstance(n, int) and n >= 0,
            'generator': lambda: (i for i in range(100)),  # First 100 natural numbers
            'in_domain_of': [
                'DIVISORS-OF', 'MULTIPLY', 'ADD', 'SUCCESSOR',
                'SQUARE', 'IEQP', 'ILEQ', 'IGEQ', 'ILESSP', 'IGREATERP'
            ]
        },
        'PRIME-NUM': {
            'worth': 800,
            'isa': ['nnumber', 'anything'],
            'fast_defn': lambda n: n > 1 and all(n % i != 0 for i in range(2, int(n ** 0.5) + 1))
        },
        'EVEN-NUM': {
            'worth': 700,
            'isa': ['nnumber', 'anything'],
            'fast_defn': lambda n: isinstance(n, int) and n % 2 == 0,
            'unitized_defn': lambda n: n % 2 == 0
        },
        'ODD-NUM': {
            'worth': 700,
            'isa': ['nnumber', 'anything'],
            'fast_defn': lambda n: isinstance(n, int) and n % 2 == 1,
            'unitized_defn': lambda n: n % 2 == 1
        },
        'PERF-NUM': {  # Perfect numbers
            'worth': 800,
            'isa': ['nnumber', 'anything'],
            'unitized_defn': lambda n: sum(i for i in range(1, n) if n % i == 0) == n
        }
    }

    for name, props in number_units.items():
        unit = registry.create_unit(name, worth=props['worth'])
        for prop, value in props.items():
            if prop != 'worth':
                unit.set_prop(prop, value)
