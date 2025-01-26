"""H2 heuristic implementation: Kill concepts that produce garbage."""
from typing import Any, Dict, List
from ..units import Unit
import logging

logger = logging.getLogger(__name__)

def setup_h2(heuristic) -> None:
    """Configure H2: Kill concepts that produce garbage."""
    heuristic.set_prop('worth', 700)
    
    def check_task_factory(rule):
        """Function factory - returns test function."""
        def check_task(context):
            """Check if this is the end of a task that created units."""
            unit = context['unit']
            return check_applications(unit)
        return check_task
        
    def print_action_factory(rule):
        """Function factory - returns print action."""
        def print_action(context):
            """Print message about killed units."""
            units = context.get('killed_units', [])
            if units:
                print(f"Killed {len(units)} garbage units")
            return True
        return print_action
        
    # Set up factories that will produce the actual test/action functions
    heuristic.set_prop('if_finished_working_on_task', check_task_factory)
    heuristic.set_prop('then_print_to_user', print_action_factory)
