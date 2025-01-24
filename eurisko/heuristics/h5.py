"""H5 heuristic implementation: Choose multiple slots to specialize."""
from typing import Any, Dict
import random

def setup_h5(heuristic) -> None:
    """Configure H5: Choose multiple slots to specialize."""
    def check_task(context: Dict[str, Any]) -> bool:
        """Check if we need to choose slots to specialize."""
        unit = context.get('unit')
        task = context.get('task')
        if not unit or not task:
            return False
            
        return (task.get('task_type') == 'specialization' and
                not task.get('slots_to_change'))

    def compute_action(context: Dict[str, Any]) -> bool:
        """Randomly select slots for specialization."""
        unit = context.get('unit')
        if not unit:
            return False

        # Get available slots
        all_slots = unit.get_prop('slots') or []
        if not all_slots:
            return False

        # Select a subset of slots randomly
        num_slots = min(random.randint(1, 3), len(all_slots))
        selected_slots = random.sample(all_slots, num_slots)
        
        # Set the selected slots in the context
        task = context.get('task')
        if task:
            task['slots_to_change'] = selected_slots
            return True
            
        return False

    heuristic.set_prop('if_working_on_task', check_task)
    heuristic.set_prop('then_compute', compute_action)