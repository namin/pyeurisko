"""H7 heuristic implementation: Find instances for concepts with none.

This heuristic triggers when a concept has no known instances, prompting the system
to search for some. It works for both categories and operators.
"""
from typing import Any, Dict
from ..unit import Unit
import logging

logger = logging.getLogger(__name__)

def setup_h7(heuristic) -> None:
    """Configure H7: Find instances for concepts with no known instances."""
    # Set properties from original LISP implementation
    heuristic.set_prop('worth', 700)
    heuristic.set_prop('english',
        "IF a concept has no known instances, THEN try to find some")
    heuristic.set_prop('abbrev', "Instantiate a concept having no known instances")
    heuristic.set_prop('arity', 1)
    
    # Set record counts from original
    heuristic.set_prop('then_add_to_agenda_record', (11017, 172))
    heuristic.set_prop('then_print_to_user_record', (21543, 172))
    heuristic.set_prop('overall_record', (71147, 172))

    def check_applics(context: Dict[str, Any]) -> bool:
        """Check if the concept has no instances."""
        unit = context.get('unit')
        if not unit:
            return False
            
        return not bool(unit.get_prop('examples'))

    def check_relevance(context: Dict[str, Any]) -> bool:
        """Check if the concept is a category or operator."""
        unit = context.get('unit')
        if not unit:
            return False
            
        isa = unit.get_prop('isa')
        if not isa:
            return False
            
        return 'category' in isa or 'op' in isa

    def print_results(context: Dict[str, Any]) -> bool:
        """Print explanation of the instance-finding task."""
        unit = context.get('unit')
        if not unit:
            return False
            
        logger.info(f"\nSince {unit.name} has no known examples, "
                   f"it is probably worth looking for some.")
        return True

    def compute_action(context: Dict[str, Any]) -> bool:
        """Create task to find instances."""
        unit = context.get('unit')
        if not unit:
            return False
            
        # Initialize context if needed
        if not isinstance(context.get('task'), dict):
            context['task'] = {}
            
        # Add task fields
        task = context['task']
        task['task_type'] = 'find_instances'
        task['target_unit'] = unit.name
        
        # Update task results
        context['task_results'] = {
            'new_tasks': "1 unit must be instantiated"
        }
        
        return True

    # Configure the heuristic
    heuristic.set_prop('if_potentially_relevant', check_applics)
    heuristic.set_prop('if_truly_relevant', check_relevance)
    heuristic.set_prop('then_print_to_user', print_results)
    heuristic.set_prop('then_compute', compute_action)