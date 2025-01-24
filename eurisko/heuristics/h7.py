"""H7 heuristic implementation: Find instances for concepts with none."""
from typing import Any, Dict
from ..unit import Unit
import logging

logger = logging.getLogger(__name__)

def setup_h7(heuristic) -> None:
    """Configure H7: Find instances for concepts that have none."""
    def check_relevant(context: Dict[str, Any]) -> bool:
        """Check if unit has no instances but should have some."""
        unit = context.get('unit')
        if not unit:
            return False
            
        # Check if unit has instances slot defined
        instances_slot = unit.get_prop('instances_slot')
        if not instances_slot:
            return False
            
        # Check if instances exist
        instances = unit.get_prop(instances_slot)
        if instances:
            return False
            
        # Check if unit is a category that should have instances
        isa = unit.get_prop('isa') or []
        return 'category' in isa or 'op' in isa

    def compute_action(context: Dict[str, Any]) -> bool:
        """Add task to find instances for unit."""
        unit = context.get('unit')
        if not unit:
            return False
            
        instances_slot = unit.get_prop('instances_slot')
        if not instances_slot:
            return False
            
        # Create task to find instances
        task = context.get('task', {})
        task['task_type'] = 'find_instances'
        task['target_unit'] = unit.name
        task['target_slot'] = instances_slot
        task['priority'] = unit.worth_value() * 0.8  # Scale priority based on unit worth
        task['reason'] = f"Find instances for {unit.name} which currently has none"
        
        return True

    # Setup functions on heuristic
    heuristic.set_prop('if_potentially_relevant', lambda ctx: True)  # Always potentially relevant
    heuristic.set_prop('if_truly_relevant', check_relevant)
    heuristic.set_prop('then_compute', compute_action)