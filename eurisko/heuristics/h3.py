"""H3 heuristic implementation: Choose slot to specialize."""
from typing import Any, Dict
import random
import logging

logger = logging.getLogger(__name__)

def setup_h3(heuristic) -> None:
    """Configure H3: Choose slot to specialize."""
    # Set properties from original LISP implementation
    heuristic.set_prop('worth', 101)
    heuristic.set_prop('english', 
        "IF the current task is to specialize a unit, but no specific slot to "
        "specialize is yet known, THEN choose one")
    heuristic.set_prop('abbrev', "Randomly choose a slot to specialize")
    heuristic.set_prop('arity', 1)

    def check_task(context: Dict[str, Any]) -> bool:
        """Check if we need to choose a slot to specialize."""
        unit = context.get('unit')
        task = context.get('task')
        if not unit or not task:
            return False
            
        # Check if this is a specialization task without a chosen slot
        is_specialization = task.get('task_type') == 'specialization'
        no_slot_chosen = not task.get('slot_to_change')
        
        # Check agenda count (as in LISP version)
        if hasattr(heuristic, 'task_manager'):
            similar_tasks = sum(1 for t in heuristic.task_manager.tasks
                              if (t.get('unit') == unit.name and 
                                  t.get('task_type') == 'specialization'))
            too_many_tasks = similar_tasks >= 11
            if too_many_tasks:
                return False
                
        return is_specialization and no_slot_chosen

    def print_to_user(context: Dict[str, Any]) -> bool:
        """Print explanation of slot choice."""
        unit = context.get('unit')
        slot = context.get('chosen_slot')
        reason = context.get('reason')
        
        if not all([unit, slot, reason]):
            return False
            
        logger.info(f"\n{reason}")
        return True

    def compute_action(context: Dict[str, Any]) -> bool:
        """Randomly select a slot for specialization."""
        unit = context.get('unit')
        task = context.get('task')
        if not unit or not task:
            return False

        # Get slot options - intersection of unit slots and known slot types
        unit_slots = unit.get_prop('slots') or []
        if hasattr(heuristic, 'unit_registry'):
            slot_types = heuristic.unit_registry.get_units_by_category('slot')
            valid_slots = set(unit_slots) & set(slot_types)
            slots = list(valid_slots) if valid_slots else unit_slots
        else:
            slots = unit_slots

        if not slots:
            return False

        # Choose slot and update context
        chosen_slot = random.choice(slots)
        task['slot_to_change'] = chosen_slot
        context['chosen_slot'] = chosen_slot
        
        # Store credit information
        task['credit_to'] = task.get('credit_to', []) + ['h3']
        
        # Create reason text
        reason = (f"A new unit will be created by specializing the {chosen_slot} slot "
                 f"of {unit.name}; that slot was chosen randomly.")
        context['reason'] = reason
        
        return True

    def add_to_agenda(context: Dict[str, Any]) -> bool:
        """Add specialized task to agenda."""
        unit = context.get('unit')
        task = context.get('task')
        chosen_slot = context.get('chosen_slot')
        reason = context.get('reason')
        
        if not all([unit, task, chosen_slot, reason]):
            return False
            
        if not hasattr(heuristic, 'task_manager'):
            return False
            
        # Calculate priority based on worths
        base_priority = task.get('priority', 500)
        h3_worth = heuristic.worth_value()
        unit_worth = unit.worth_value()
        new_priority = (base_priority + h3_worth + unit_worth) // 3
        
        # Create new task
        new_task = {
            'priority': new_priority,
            'unit': unit,
            'slot': 'specializations',
            'reasons': [reason],
            'supplemental': {
                'slot_to_change': chosen_slot,
                'credit_to': ['h3'] + (task.get('credit_to', []))
            }
        }
        
        heuristic.task_manager.add_task(new_task)
        
        # Record task creation
        if hasattr(heuristic, 'add_task_result'):
            heuristic.add_task_result('new_tasks', 
                f"1 specific slot of {unit.name} to find specializations of")
            
        return True

    # Set up all the slots
    heuristic.set_prop('if_working_on_task', check_task)
    heuristic.set_prop('then_print_to_user', print_to_user)
    heuristic.set_prop('then_compute', compute_action)
    heuristic.set_prop('then_add_to_agenda', add_to_agenda)
    
    # Add subsumption information from LISP
    heuristic.set_prop('subsumed_by', ['h5', 'h5-criterial', 'h5-good'])