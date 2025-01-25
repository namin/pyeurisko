"""H4 heuristic implementation: Gather data about new units."""
from typing import Any, Dict
import logging

logger = logging.getLogger(__name__)

def setup_h4(heuristic) -> None:
    """Configure H4: Gather data about new units."""
    # Set properties from original LISP implementation
    heuristic.set_prop('worth', 703)
    heuristic.set_prop('english', 
        "IF a new unit has been synthesized, THEN place a task on the Agenda to "
        "gather new empirical data about it")
    heuristic.set_prop('abbrev', "Gather empirical data about new concepts")
    heuristic.set_prop('arity', 1)
    
    # Initialize records as in LISP
    heuristic.set_prop('then_add_to_agenda_record', (30653, 87))
    heuristic.set_prop('then_print_to_user_record', (18543, 87))
    heuristic.set_prop('overall_record', (68827, 72))

    def check_task(context: Dict[str, Any]) -> bool:
        """Check for new units created."""
        task_results = context.get('task_results', {})
        new_units = task_results.get('new_units', [])
        # Filter for valid units
        valid_units = [u for u in new_units if hasattr(u, 'get_prop')]
        context['valid_units'] = valid_units
        return bool(valid_units)

    def print_to_user(context: Dict[str, Any]) -> bool:
        """Print information about new units."""
        valid_units = context.get('valid_units', [])
        if not valid_units:
            return False
            
        logger.info(f"\n{len(valid_units)} new units, namely {[u.name for u in valid_units]}, "
                   f"were defined. New tasks are being added to the agenda to ensure that "
                   f"empirical data about them will soon be gathered.")
        return True

    def add_to_agenda(context: Dict[str, Any]) -> bool:
        """Add tasks to gather data about new units."""
        valid_units = context.get('valid_units', [])
        if not valid_units or not hasattr(heuristic, 'task_manager'):
            return False
            
        for unit in valid_units:
            # Get the appropriate instance slot for this unit type
            instance_slot = unit.get_prop('instances') or 'examples'
            
            # Create task to gather instances
            task = {
                'priority': int((unit.worth_value() + heuristic.worth_value()) / 2),
                'unit': unit,
                'slot': instance_slot,
                'reasons': ["After a unit is synthesized, it is useful to seek instances of it."],
                'supplemental': {
                    'credit_to': ['h4'],
                    'task_type': 'data_gathering'
                }
            }
            heuristic.task_manager.add_task(task)
            
        # Record task creation
        num_units = len(valid_units)
        heuristic.add_task_result('new_tasks', 
            f"{num_units} new units must have instances found")
        return True

    # Set up all the slots
    heuristic.set_prop('if_finished_working_on_task', check_task)
    heuristic.set_prop('then_print_to_user', print_to_user)
    heuristic.set_prop('then_add_to_agenda', add_to_agenda)