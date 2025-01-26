"""Core heuristic implementation for PyEurisko."""

from typing import Any, Dict, List, Optional, Callable
import random
import time
import os
import importlib
import inspect
from ..units import Unit, UnitRegistry

def rule_factory(func: Callable):
    """Create a factory decorator for rule functions.
    The property name is exactly the function name.
    """
    def make_factory(heuristic):
        property_name = func.__name__
        def factory(rule):
            def wrapper(context):
                return func(rule, context)
            return wrapper
        heuristic.set_prop(property_name, factory)
    return make_factory

def discover_heuristics():
    """Discover all available heuristics and their documentation."""
    heuristics = []
    directory = os.path.dirname(__file__)
    
    files = [f for f in os.listdir(directory) 
             if f.endswith('.py') 
             and f.startswith('h')
             and not any(x in f for x in ['criterial', 'good'])]  # Skip special cases
    
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

def initialize_all_heuristics(unit_registry) -> None:
    heuristics = discover_heuristics()
    for h in heuristics:
        try:
            h_num = int(h['name'][1:])  # Extract number from hX
            if h_num not in range(1, 13):  # Updated to include h11
                continue
            unit = unit_registry.create_unit(h['name'])
            unit.set_prop('isa', ['heuristic', 'anything'])
            if not unit.get_prop('english'):
                unit.set_prop('english', h['description'])
            setup_func = h['setup_func']
            setup_func(unit)
            unit_registry.register(unit)
        except ValueError:
            continue  # Skip any malformed heuristic names
