"""Core concept definitions for PyEurisko."""

from typing import Dict, Any, List
from ..units import Unit, UnitRegistry

def add_algorithm(a: float, b: float) -> float:
    """Basic addition algorithm."""
    return a + b

def multiply_algorithm(a: float, b: float) -> float:
    """Basic multiplication algorithm."""
    return a * b
    
def compose_algorithm(f, g):
    """Function composition algorithm."""
    return lambda x: f(g(x))
    
def restrict_algorithm(f, domain):
    """Domain restriction algorithm."""
    return lambda x: f(x) if x in domain else None
    
def set_union_algorithm(a: set, b: set) -> set:
    """Set union algorithm."""
    return a.union(b)
    
def set_intersect_algorithm(a: set, b: set) -> set:
    """Set intersection algorithm."""
    return a.intersection(b)
    
def list_union_algorithm(a: list, b: list) -> list:
    """List union algorithm."""
    return list(set(a).union(set(b)))
    
def bag_union_algorithm(a: dict, b: dict) -> dict:
    """Bag union algorithm (multiset)."""
    result = a.copy()
    for item, count in b.items():
        result[item] = result.get(item, 0) + count
    return result

def initialize_math_operations(registry: UnitRegistry) -> None:
    """Initialize core mathematical operations."""
    math_ops = {
        'add': {
            'arity': 2, 
            'domain': ['nnumber', 'nnumber'], 
            'range': ['nnumber'],
            'fast_alg': add_algorithm,
            'elim-slots': ['applics']
        },
        'multiply': {
            'arity': 2, 
            'domain': ['nnumber', 'nnumber'], 
            'range': ['nnumber'],
            'fast_alg': multiply_algorithm,
            'elim-slots': ['applics']
        },
        'compose': {
            'arity': 2,
            'domain': ['op', 'op'],
            'range': ['op'],
            'fast_alg': compose_algorithm,
            'elim-slots': ['applics']
        },
        'restrict': {
            'arity': 2, 
            'domain': ['op', 'set'], 
            'range': ['op'],
            'fast_alg': restrict_algorithm,
            'elim-slots': ['applics']
        },
        'set-union': {
            'arity': 2, 
            'domain': ['set', 'set'],
            'range': ['set'],
            'fast_alg': set_union_algorithm,
            'elim-slots': ['applics']
        },
        'set-intersect': {
            'arity': 2, 
            'domain': ['set', 'set'], 
            'range': ['set'],
            'fast_alg': set_intersect_algorithm,
            'elim-slots': ['applics']
        },
        'list-union': {
            'arity': 2, 
            'domain': ['list', 'list'], 
            'range': ['list'],
            'fast_alg': list_union_algorithm,
            'elim-slots': ['applics']
        },
        'bag-union': {
            'arity': 2, 
            'domain': ['bag', 'bag'], 
            'range': ['bag'],
            'fast_alg': bag_union_algorithm,
            'elim-slots': ['applics']
        }
    }
    
    op_categories = ['math-concept', 'math-op', 'op', 'anything', 'binary-op']
    
    for op_name, props in math_ops.items():
        unit = registry.create_unit(op_name, worth=500)
        unit.set_prop('isa', op_categories)
        for prop_name, value in props.items():
            unit.set_prop(prop_name, value)
            
        # Add some sample applications for each op
        if op_name == 'add':
            applications = [
                {'args': [1, 2], 'result': 3, 'worth': 800},
                {'args': [2, 3], 'result': 5, 'worth': 600},
                {'args': [3, 4], 'result': 7, 'worth': 400}
            ]
            unit.set_prop('applications', applications)
        elif op_name == 'multiply':
            applications = [
                {'args': [2, 3], 'result': 6, 'worth': 900},
                {'args': [3, 4], 'result': 12, 'worth': 500},
                {'args': [4, 5], 'result': 20, 'worth': 300}
            ]
            unit.set_prop('applications', applications)

def initialize_math_objects(registry: UnitRegistry) -> None:
    """Initialize core mathematical objects."""
    math_objs = {
        'set': {
            'empty_value': set(), 
            'properties': ['unordered', 'unique'],
            'isa': ['math-obj', 'anything', 'structure']
        },
        'list': {
            'empty_value': list(), 
            'properties': ['ordered'],
            'isa': ['math-obj', 'anything', 'structure']
        },
        'bag': {
            'empty_value': dict(), 
            'properties': ['unordered', 'counted'],
            'isa': ['math-obj', 'anything', 'structure']
        },
        'structure': {
            'empty_value': dict(), 
            'properties': ['composite'],
            'isa': ['math-obj', 'anything']
        }
    }
    
    for obj_name, props in math_objs.items():
        unit = registry.create_unit(obj_name, worth=500)
        for prop_name, value in props.items():
            unit.set_prop(prop_name, value)

def initialize_repr_concepts(registry: UnitRegistry) -> None:
    """Initialize core representational concepts."""
    repr_concepts = {
        'slot': {
            'role': 'property-container', 
            'properties': ['named', 'typed'],
            'isa': ['REPR-CONCEPT', 'anything']
        },
        'category': {
            'role': 'classification', 
            'properties': ['hierarchical'],
            'isa': ['REPR-CONCEPT', 'anything']
        },
        'task': {
            'role': 'action', 
            'properties': ['executable', 'scheduled'],
            'isa': ['REPR-CONCEPT', 'anything']
        },
        'record': {
            'role': 'history', 
            'properties': ['temporal', 'factual'],
            'isa': ['REPR-CONCEPT', 'anything']
        }
    }
    
    for concept_name, props in repr_concepts.items():
        unit = registry.create_unit(concept_name, worth=500)
        for prop_name, value in props.items():
            unit.set_prop(prop_name, value)

def initialize_core_concepts(registry: UnitRegistry) -> None:
    """Initialize all core concepts in the system."""
    initialize_repr_concepts(registry)
    initialize_math_objects(registry)
    initialize_math_operations(registry)