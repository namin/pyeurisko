"""Function slots implementation for PyEurisko."""

import logging
from typing import Any, Dict, List, Set, Optional, Callable, Union
from ..units import Unit

logger = logging.getLogger(__name__)

def specializations_func(unit: Unit) -> List[str]:
    """Get/create specializations by analyzing unit's applications."""
    applications = unit.get_prop('applications', [])
    if not applications:
        return []
        
    # Look for patterns in successful vs failed applications
    successes = [app for app in applications if app.get('success', True)]  # Default to True
    failures = [app for app in applications if not app.get('success', True)]
    
    # Need both success and failure patterns
    if not successes or not failures:
        return []
        
    # Track created units
    new_units = []
    registry = unit.unit_registry
    
    # Look for patterns in successes vs failures
    for i, succ_app in enumerate(successes):
        if not isinstance(succ_app, dict):
            continue
            
        # Check argument patterns
        args = succ_app.get('args', [])
        if not args:
            continue
            
        # Track successful argument types/patterns for this position
        for arg_pos, arg in enumerate(args):
            # Get corresponding argument types in failures
            fail_args = [app.get('args', [])[arg_pos] 
                        for app in failures 
                        if isinstance(app, dict) and len(app.get('args', [])) > arg_pos]
            
            if not fail_args:
                continue
                
            # Look for type specialization opportunities
            succ_type = type(arg).__name__
            fail_types = {type(fa).__name__ for fa in fail_args}
            
            if succ_type not in fail_types:
                # Create specialized version for this argument type
                spec_name = f"{unit.name}_for_{succ_type}_{arg_pos}"
                
                if not registry.exists(spec_name):
                    specialized = registry.create_unit(spec_name)
                    specialized.copy_slots_from(unit)
                    
                    # Modify domain to enforce type
                    domain = unit.get_prop('domain', [])
                    new_domain = domain.copy()
                    if len(new_domain) > arg_pos:
                        new_domain[arg_pos] = succ_type
                    specialized.set_prop('domain', new_domain)
                    
                    # Link to parent
                    specialized.add_generalization(unit.name)
                    new_units.append(specialized.name)
                    
                    logger.info(f"Created specialized unit {spec_name} based on {succ_type} argument at position {arg_pos}")
    
    # Store references to new specializations
    existing = unit.get_prop('specializations', [])
    unit.set_prop('specializations', list(set(existing + new_units)))
    
    return new_units

def generalizations_func(unit: Unit) -> List[str]:
    """Get/create generalizations by analyzing unit's applications."""
    # Similar to specializations but looking for opportunities to generalize
    # Example: If a numeric operation works on both ints and floats, generalize to number
    return []

def applications_func(unit: Unit) -> List[Dict[str, Any]]:
    """Generate new applications by trying the unit on examples of its domain types."""
    domain = unit.get_prop('domain', [])
    if not domain:
        return []

    # Get example values for each domain type
    registry = unit.unit_registry
    new_applications = []
    
    # Try to find example values
    for domain_type in domain:
        type_unit = registry.get_unit(domain_type)
        if not type_unit:
            continue
            
        examples = type_unit.get_prop('examples', [])
        if not examples:
            continue
            
        # Try applying unit to examples
        alg = unit.get_algorithm()
        if not alg:
            continue
            
        for ex in examples:
            try:
                result = alg(ex)
                new_applications.append({
                    'args': [ex],
                    'result': result,
                    'success': True if result is not None else False
                })
            except Exception as e:
                new_applications.append({
                    'args': [ex],
                    'result': None,
                    'success': False
                })
                
    # Store new applications
    existing = unit.get_prop('applications', [])
    unit.set_prop('applications', existing + new_applications)
    
    return new_applications

def initialize_slot_functions(registry):
    """Initialize function slots in the registry."""
    
    # Specializations slot
    spec_slot = registry.get_slot('specializations')
    if spec_slot:
        spec_slot.set_prop('function', specializations_func)
        
    # Generalizations slot    
    gen_slot = registry.get_slot('generalizations')
    if gen_slot:
        gen_slot.set_prop('function', generalizations_func)
        
    # Applications slot
    app_slot = registry.get_slot('applications') 
    if app_slot:
        app_slot.set_prop('function', applications_func)