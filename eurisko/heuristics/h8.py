"""H8 heuristic implementation: Find applications through generalizations.

This heuristic finds application instances for a unit by examining applications of its
generalizations. If the generalization's applications have arguments that satisfy the
current unit's domain constraints, they are added as applications of the current unit.
"""
from typing import Any, Dict, List
from ..unit import Unit
import logging

logger = logging.getLogger(__name__)

def setup_h8(heuristic) -> None:
    """Configure H8: Find applications through generalizations."""
    # Set properties from original LISP implementation
    heuristic.set_prop('worth', 700)
    heuristic.set_prop('english',
        "IF the current task is to find application-instances of a unit, and it "
        "has a algorithm, THEN look over instances of generalizations of the unit, "
        "and see if any of them are valid application-instances of this as well")
    heuristic.set_prop('abbrev', "Find applications through generalizations")
    heuristic.set_prop('arity', 1)
    
    # Set record counts from original
    heuristic.set_prop('then_compute_failed_record', (635979, 66))
    heuristic.set_prop('then_compute_record', (368382, 10))
    heuristic.set_prop('then_print_to_user_record', (3893, 10))
    heuristic.set_prop('overall_record', (375388, 10))

    def check_task(context: Dict[str, Any]) -> bool:
        """Check if we're working on an applications task."""
        task = context.get('task')
        return task and task.get('task_type') == 'find_applications'

    def check_relevance(context: Dict[str, Any]) -> bool:
        """Check if unit has algorithm and valid generalizations."""
        unit = context.get('unit')
        if not unit:
            return False
            
        # Need algorithm and generalizations
        if not unit.get_prop('algorithm'):
            return False
            
        # Check generalizations exist
        gen_names = unit.get_prop('generalizations')
        if not gen_names:
            return False
            
        # Store registry for later
        context['registry'] = heuristic.unit_registry
        context['space_to_use'] = gen_names
        return True

    def print_results(context: Dict[str, Any]) -> bool:
        """Print the applications found."""
        unit = context.get('unit')
        new_values = context.get('task_results', {}).get('new_values', [])
        if not unit or not new_values:
            return False
            
        logger.info(f"\nFound {len(new_values)} applications for {unit.name}")
        logger.debug(f"Applications: {new_values}")
        return True

    def compute_action(context: Dict[str, Any]) -> bool:
        """Find applications from generalizations."""
        unit = context.get('unit')
        registry = context.get('registry')
        gen_names = context.get('space_to_use')
        if not all([unit, registry, gen_names]):
            return False
            
        # Get algorithm
        algorithm = unit.get_prop('algorithm')
        
        # Track new applications
        new_values = []
        current_apps = unit.get_prop('applications') or []
        known_apps = {str(app) for app in current_apps}
        
        # Check each generalization's applications
        for gen_name in gen_names:
            gen_unit = registry.get_unit(gen_name)
            if not gen_unit:
                continue
                
            apps = gen_unit.get_prop('applications') or []
            for app in apps:
                app_str = str(app)
                if app_str not in known_apps:
                    if verify_application(app, algorithm):
                        new_values.append(app)
                        known_apps.add(app_str)
        
        # Update results if we found any
        if new_values:
            if 'task_results' not in context:
                context['task_results'] = {}
            context['task_results']['new_values'] = new_values
            
        return bool(new_values)

    def verify_application(app: Dict[str, Any], algorithm: callable) -> bool:
        """Verify an application works with current algorithm."""
        try:
            args = app.get('args', [])
            if not args:
                return False
                
            if len(args) == 1:
                result = algorithm(args[0])
            else:
                result = algorithm(*args)
            return result == app.get('result')
        except:
            return False

    # Configure the heuristic
    heuristic.set_prop('if_working_on_task', check_task)
    heuristic.set_prop('if_truly_relevant', check_relevance) 
    heuristic.set_prop('then_print_to_user', print_results)
    heuristic.set_prop('then_compute', compute_action)