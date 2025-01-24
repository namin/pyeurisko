"""H8 heuristic implementation: Find applications by looking at generalizations."""
from typing import Any, Dict, List, Set
from ..unit import Unit
import logging

logger = logging.getLogger(__name__)

def setup_h8(heuristic) -> None:
    """Configure H8: Find applications by examining generalizations."""
    def check_task(context: Dict[str, Any]) -> bool:
        """Check if we're looking for applications and unit has algorithm."""
        unit = context.get('unit')
        task = context.get('task')
        if not unit or not task:
            return False
            
        if task.get('task_type') != 'find_applications':
            return False
            
        # Check for algorithm existence
        if not unit.get_prop('algorithm'):
            return False
            
        # Check for generalizations to examine
        generalizations = unit.get_prop('generalizations') or []
        if not generalizations:
            # Check isa relationships for examples if no direct generalizations
            isa_types = unit.get_prop('isa') or []
            found = False
            for typ in isa_types:
                type_unit = heuristic.unit_registry.get_unit(typ)
                if type_unit and type_unit.get_prop('examples'):
                    found = True
                    break
            if not found:
                return False
                
        return True

    def compute_action(context: Dict[str, Any]) -> bool:
        """Find applications by examining generalizations."""
        unit = context.get('unit')
        if not unit:
            return False
            
        algorithm = unit.get_prop('algorithm')
        if not algorithm:
            return False
            
        # Collect potential spaces to examine
        spaces_to_use = set()
        
        # Direct generalizations
        generalizations = unit.get_prop('generalizations') or []
        spaces_to_use.update(generalizations)
        
        # Add examples from isa types
        isa_types = unit.get_prop('isa') or []
        for typ in isa_types:
            type_unit = heuristic.unit_registry.get_unit(typ)
            if type_unit:
                examples = type_unit.get_prop('examples') or []
                spaces_to_use.update(examples)
        
        # Remove unit itself and its specializations
        specializations = unit.get_prop('specializations') or []
        spaces_to_use.discard(unit.name)
        for spec in specializations:
            spaces_to_use.discard(spec)
            
        # Filter by matching arity
        unit_arity = unit.get_prop('arity')
        if unit_arity:
            spaces_to_use = {name for name in spaces_to_use 
                           if heuristic.unit_registry.get_unit(name) and
                           heuristic.unit_registry.get_unit(name).get_prop('arity') == unit_arity}
            
        if not spaces_to_use:
            return False
            
        # For each space, examine its applications
        new_applications = []
        domain_tests = []
        for domain_unit in (unit.get_prop('domain') or []):
            domain_test = heuristic.unit_registry.get_unit(domain_unit)
            if domain_test and domain_test.get_prop('definition'):
                domain_tests.append(domain_test.get_prop('definition'))
                
        for space_name in spaces_to_use:
            space_unit = heuristic.unit_registry.get_unit(space_name)
            if not space_unit:
                continue
                
            # Look through existing applications
            applications = space_unit.get_prop('applications') or []
            for application in applications:
                args = application.get('args', [])
                
                # Skip if we already know this application
                if unit.has_application(args):
                    continue
                    
                # Verify domain constraints
                valid = True
                for test, arg in zip(domain_tests, args):
                    if not test(arg):
                        valid = False
                        break
                        
                if valid:
                    # Try applying algorithm to arguments
                    try:
                        result = algorithm(*args)
                        new_applications.append({
                            'args': args,
                            'result': result
                        })
                    except Exception as e:
                        logger.warning(f"Failed to apply algorithm: {e}")
                        
        if new_applications:
            # Add new applications to unit
            current_applications = unit.get_prop('applications') or []
            unit.set_prop('applications', current_applications + new_applications)
            
            # Update task results
            task_results = context.get('task_results', {})
            task_results['new_values'] = new_applications
            task_results['source_spaces'] = list(spaces_to_use)
            return True
            
        return False

    # Set up heuristic properties
    heuristic.set_prop('if_working_on_task', check_task)
    heuristic.set_prop('then_compute', compute_action)