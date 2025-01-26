"""Core concept definitions for PyEurisko."""

from typing import Dict, Any
import os
import importlib
import inspect
from .unit import Unit, UnitRegistry
from .heuristics import Heuristic
from .heuristics.h1 import setup_h1

def discover_heuristics():
    """Discover all available heuristics and their documentation."""
    heuristics = []
    directory = os.path.join(os.path.dirname(__file__), 'heuristics')
    
    files = [f for f in os.listdir(directory) 
             if f.endswith('.py') 
             and f not in ['__init__.py', 'base.py', 'registry.py']]
    
    for file in sorted(files):
        module_name = file[:-3]  # Remove .py extension
        
        # Import the module
        module = importlib.import_module(f'eurisko.heuristics.{module_name}')
        
        # Look for setup function (they follow pattern setup_h*)
        setup_func = None
        for name, obj in inspect.getmembers(module):
            if name.startswith('setup_') and inspect.isfunction(obj):
                setup_func = obj
                break
        
        if setup_func:
            docstring = inspect.getdoc(setup_func) or "No documentation available"
            description = docstring.split('\n')[0]  # Get first line of docstring
            
            heuristics.append({
                'name': module_name,
                'description': description,
                'setup_func': setup_func
            })
    
    return heuristics

def initialize_heuristics(registry: UnitRegistry) -> None:
    heuristics = discover_heuristics()
    for h in heuristics:
        unit = registry.create_unit(h['name'])
        if not unit.get_prop('english'):
            unit.set_prop('english', h['description'])
        setup_func = h['setup_func']
        setup_func(unit)

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
