"""Core concept definitions for PyEurisko."""

from typing import Dict, Any
from ..units import Unit, UnitRegistry

def initialize_math_operations(registry: UnitRegistry) -> None:
    """Initialize core mathematical operations."""
    math_ops = {
        'add': {'arity': 2, 'domain': ['number'], 'range': 'number'},
        'multiply': {'arity': 2, 'domain': ['number'], 'range': 'number'},
        'compose': {'arity': 2, 'domain': ['function'], 'range': 'function'},
        'restrict': {'arity': 2, 'domain': ['function', 'set'], 'range': 'function'},
        'set-union': {'arity': 2, 'domain': ['set'], 'range': 'set'},
        'set-intersect': {'arity': 2, 'domain': ['set'], 'range': 'set'},
        'list-union': {'arity': 2, 'domain': ['list'], 'range': 'list'},
        'bag-union': {'arity': 2, 'domain': ['bag'], 'range': 'bag'}
    }
    
    for op_name, props in math_ops.items():
        unit = registry.create_unit(op_name, worth=500, isa=['math-op'])
        for prop_name, value in props.items():
            unit.set_prop(prop_name, value)

def initialize_math_objects(registry: UnitRegistry) -> None:
    """Initialize core mathematical objects."""
    math_objs = {
        'set': {'empty_value': set(), 'properties': ['unordered', 'unique']},
        'list': {'empty_value': list(), 'properties': ['ordered']},
        'bag': {'empty_value': dict(), 'properties': ['unordered', 'counted']},
        'structure': {'empty_value': dict(), 'properties': ['composite']}
    }
    
    for obj_name, props in math_objs.items():
        unit = registry.create_unit(obj_name, worth=500, isa=['math-obj'])
        for prop_name, value in props.items():
            unit.set_prop(prop_name, value)

def initialize_repr_concepts(registry: UnitRegistry) -> None:
    """Initialize core representational concepts."""
    repr_concepts = {
        'slot': {'role': 'property-container', 'properties': ['named', 'typed']},
        'category': {'role': 'classification', 'properties': ['hierarchical']},
        'task': {'role': 'action', 'properties': ['executable', 'scheduled']},
        'record': {'role': 'history', 'properties': ['temporal', 'factual']}
    }
    
    for concept_name, props in repr_concepts.items():
        unit = registry.create_unit(concept_name, worth=500, isa=['REPR-CONCEPT'])
        for prop_name, value in props.items():
            unit.set_prop(prop_name, value)

def initialize_core_concepts(registry: UnitRegistry) -> None:
    """Initialize all core concepts in the system."""
    initialize_repr_concepts(registry)
    initialize_math_objects(registry)
    initialize_math_operations(registry)
