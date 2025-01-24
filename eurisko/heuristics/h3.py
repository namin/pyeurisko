"""H3 heuristic implementation: Choose slot to specialize."""
from typing import Any, Dict
import random

def setup_h3(heuristic) -> None:
    """Configure H3: Choose slot to specialize."""
    def check_task(context: Dict[str, Any]) -> bool:
        """Check if we need to choose a slot to specialize."""
        unit = context.get('unit')
        task = context.get('task')
        if not unit or not task:
            return False
            
        return (task.get('task_type') == 'specialization' and
                not task.get('slot_to_change'))

    def compute_action(context: Dict[str, Any]) -> bool:
        """Randomly select a slot for specialization."""
        unit = context.get('unit')
        task = context.get('task')
        if not unit or not task:
            return False

        slots = unit.get_prop('slots') or []
        if not slots:
            return False

        chosen_slot = random.choice(slots)
        task['slot_to_change'] = chosen_slot
        return True

    heuristic.set_prop('if_working_on_task', check_task)
    heuristic.set_prop('then_compute', compute_action)