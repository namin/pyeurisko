"""Core heuristic implementation for PyEurisko."""

from typing import Any, Dict, List, Optional, Callable
import random
import time
import os
import importlib
import inspect
import logging
from ..units import Unit, UnitRegistry
from .enabled import enabled_heuristics
from .rule_factory import rule_factory

def discover_heuristics():
    logger = logging.getLogger(__name__)
    """Discover all available heuristics and their documentation."""
    heuristics = []
    directory = os.path.dirname(__file__)
    
    files = [f for f in os.listdir(directory) 
             if f.endswith('.py') 
             and f.startswith('h')]
    
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
    logger = logging.getLogger(__name__)
    heuristics = discover_heuristics()
    logger.info(f"Discovered heuristics: {[h['name'] for h in heuristics]}")
    
    for h in heuristics:
        if h['name'] not in enabled_heuristics:
            logger.debug(f"Skipping disabled heuristic {h['name']}")
            continue
            
        logger.info(f"Initializing heuristic {h['name']}")
        
        unit = unit_registry.create_unit(h['name'])
        unit.set_prop('isa', ['heuristic', 'anything', 'op'])
        if not unit.get_prop('english'):
            unit.set_prop('english', h['description'])
            
        setup_func = h['setup_func']
        setup_func(unit)
        
        unit.task_manager = unit_registry
        unit.unit_registry = unit_registry
        unit.worth_value = lambda: unit.get_prop('worth', 500)
        
        unit_registry.register(unit)

