"""Core concept definitions for PyEurisko."""

from typing import Dict, Any
from .unit import Unit, UnitRegistry
from .heuristics import Heuristic
from .heuristics.h1 import setup_h1

def initialize_heuristics(registry: UnitRegistry) -> None:
    """Initialize core heuristic rules."""
    descriptions = {
        'H1': "Specialize sometimes-useful actions",
        'H2': "Try to find examples of concepts with no known examples",
        'H3': "Try combining two concepts that have worked well together before",
        'H4': "Look for patterns in successful applications",
        'H5': "Choose multiple slots to specialize",
        'H6': "Look for common features in failed applications",
        'H7': "Instantiate concepts with no known instances",
        'H8': "Modify concepts that have both successes and failures",
        'H9': "Try to find alternative algorithms for concepts",
        'H10': "Look for ways to combine successful modifications",
        'H11': "Check applicability by running algorithms",
        'H12': "Try to find more efficient algorithms",
        'H13': "Look for opportunities to create new concepts",
        'H14': "Analyze relationships between concepts",
        'H15': "Monitor and improve heuristic performance"
    }
    
    # Create and configure heuristics
    for name, desc in descriptions.items():
        h = Heuristic(name, desc, registry=registry)
        registry.register(h)
        
        # Configure specific heuristics
        if name == 'H1':
            setup_h1(h)
        # Add more configuration calls as they're implemented

def initialize_math_operations(registry: UnitRegistry) -> None:
    """Initialize core mathematical operations."""
    math_ops = {
        'ADD': {'arity': 2, 'domain': ['number'], 'range': 'number'},
        'MULTIPLY': {'arity': 2, 'domain': ['number'], 'range': 'number'},
        'COMPOSE': {'arity': 2, 'domain': ['function'], 'range': 'function'},
        'RESTRICT': {'arity': 2, 'domain': ['function', 'set'], 'range': 'function'},
        'SET-UNION': {'arity': 2, 'domain': ['set'], 'range': 'set'},
        'SET-INTERSECT': {'arity': 2, 'domain': ['set'], 'range': 'set'},
        'LIST-UNION': {'arity': 2, 'domain': ['list'], 'range': 'list'},
        'BAG-UNION': {'arity': 2, 'domain': ['bag'], 'range': 'bag'}
    }
    
    for op_name, props in math_ops.items():
        unit = registry.create_unit(op_name, worth=500, isa=['MATH-OP'])
        for prop_name, value in props.items():
            unit.set_prop(prop_name, value)

def initialize_math_objects(registry: UnitRegistry) -> None:
    """Initialize core mathematical objects."""
    math_objs = {
        'SET': {'empty_value': set(), 'properties': ['unordered', 'unique']},
        'LIST': {'empty_value': list(), 'properties': ['ordered']},
        'BAG': {'empty_value': dict(), 'properties': ['unordered', 'counted']},
        'STRUCTURE': {'empty_value': dict(), 'properties': ['composite']}
    }
    
    for obj_name, props in math_objs.items():
        unit = registry.create_unit(obj_name, worth=500, isa=['MATH-OBJ'])
        for prop_name, value in props.items():
            unit.set_prop(prop_name, value)

def initialize_repr_concepts(registry: UnitRegistry) -> None:
    """Initialize core representational concepts."""
    repr_concepts = {
        'SLOT': {'role': 'property-container', 'properties': ['named', 'typed']},
        'CATEGORY': {'role': 'classification', 'properties': ['hierarchical']},
        'TASK': {'role': 'action', 'properties': ['executable', 'scheduled']},
        'RECORD': {'role': 'history', 'properties': ['temporal', 'factual']}
    }
    
    for concept_name, props in repr_concepts.items():
        unit = registry.create_unit(concept_name, worth=500, isa=['REPR-CONCEPT'])
        for prop_name, value in props.items():
            unit.set_prop(prop_name, value)

def initialize_core_concepts(registry: UnitRegistry) -> None:
    """Initialize all core concepts in the system."""
    # Initialize in order of dependency
    initialize_repr_concepts(registry)  # Basic concepts first
    initialize_math_objects(registry)   # Objects before operations
    initialize_math_operations(registry)
    initialize_heuristics(registry)     # Heuristics last as they may depend on other concepts