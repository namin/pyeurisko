"""H5-Good heuristic implementation: Choose valuable slots to specialize."""
from typing import Any, Dict, List
import random
import logging

logger = logging.getLogger(__name__)

def setup_h5_good(heuristic) -> None:
    """Configure H5-Good: Choose valuable slots for specialization."""
    heuristic.set_prop('worth', 700)
    heuristic.set_prop('english', 
        "IF the current task is to specialize a unit, and no specific slot has been "
        "chosen to be the one changed, THEN choose a good set of slots to specialize")
    heuristic.set_prop('abbrev', "Choose some particular good slots of u to specialize")
    heuristic.set_prop('arity', 1)
    heuristic.set_prop('subsumes', ['h3', 'h5'])
    heuristic.set_prop('creditors', ['h6', 'h5', 'h1'])
    
    # Initialize records as in LISP
    heuristic.set_prop('then_compute_record', (10632, 46))
    heuristic.set_prop('then_add_to_agenda_record', (23977, 46))
    heuristic.set_prop('then_print_to_user_record', (8399, 46))
    heuristic.set_prop('overall_record', (56898, 46))

    def check_task(context: Dict[str, Any]) -> bool:
        """Check if we need to choose valuable slots to specialize."""
        unit = context.get('unit')
        task = context.get('task')
        if not unit or not task:
            return False
            
        is_specialization = task.get('task_type') == 'specialization'
        no_slots_chosen = not task.get('slot_to_change')
        
        if hasattr(heuristic, 'task_manager'):
            similar_tasks = sum(1 for t in heuristic.task_manager.tasks
                              if (t.get('unit') == unit.name and 
                                  t.get('task_type') == 'specialization'))
            if similar_tasks >= 7:
                return False
                
        return is_specialization and no_slots_chosen

    def print_to_user(context: Dict[str, Any]) -> bool:
        """Print explanation of valuable slot choices."""
        unit = context.get('unit')
        slots = context.get('slots_to_change', [])
        if not unit or not slots:
            return False
            
        logger.info(f"\n{unit.name} will be specialized by specializing the following "
                   f"of its valuable slots: {slots}")
        return True

    def select_good_slots(slots: List[str], unit_registry) -> List[str]:
        """Select slots based on their worth and utility."""
        if not slots or not unit_registry:
            return []
            
        # Score slots based on their worth and past success
        slot_scores = []
        for slot_name in slots:
            slot = unit_registry.get_unit(slot_name)
            if not slot:
                continue
                
            score = slot.worth_value()
            # Consider past specializations
            if slot.get_prop('successful_specializations'):
                score *= 1.5
                
            slot_scores.append((slot_name, score))
            
        # Select top scoring slots
        slot_scores.sort(key=lambda x: x[1], reverse=True)
        top_slots = [s[0] for s in slot_scores[:3]]
        return top_slots

    def compute_action(context: Dict[str, Any]) -> bool:
        """Select valuable slots for specialization."""
        unit = context.get('unit')
        task = context.get('task')
        if not unit or not task:
            return False

        # Get available slots
        unit_slots = unit.get_prop('slots') or []
        if hasattr(heuristic, 'unit_registry'):
            slot_types = heuristic.unit_registry.get_units_by_category('slot')
            valid_slots = set(unit_slots) & set(slot_types)
            slots = list(valid_slots) if valid_slots else []
        else:
            return False

        if not slots:
            return False

        # Select valuable slots
        selected_slots = select_good_slots(slots, heuristic.unit_registry)
        if not selected_slots:
            return False
        
        # Update context and task
        context['slots_to_change'] = selected_slots
        task['slots_to_change'] = selected_slots
        task['credit_to'] = task.get('credit_to', []) + ['h5-good']
        
        return True

    def add_to_agenda(context: Dict[str, Any]) -> bool:
        """Add specialization tasks for chosen valuable slots."""
        unit = context.get('unit')
        selected_slots = context.get('slots_to_change', [])
        task = context.get('task')
        
        if not all([unit, selected_slots, task]) or not hasattr(heuristic, 'task_manager'):
            return False

        new_tasks = []
        base_priority = task.get('priority', 500)
        
        for slot in selected_slots:
            new_task = {
                'priority': int((base_priority + heuristic.worth_value() + 
                               unit.worth_value()) / 3),
                'unit': unit,
                'slot': 'specializations',
                'reasons': [f"A new unit will be created by specializing the {slot} "
                          f"slot of {unit.name}; that slot was chosen because of its "
                          f"high worth."],
                'supplemental': {
                    'slot_to_change': slot,
                    'credit_to': ['h5-good'] + (task.get('credit_to', []))
                }
            }
            new_tasks.append(new_task)
            
        # Sort tasks by priority and add to manager
        for task in sorted(new_tasks, key=lambda x: x['priority'], reverse=True):
            heuristic.task_manager.add_task(task)
            
        if hasattr(heuristic, 'add_task_result'):
            heuristic.add_task_result('new_tasks',
                f"{len(selected_slots)} specific valuable slots of {unit.name} to find specializations of")
            
        return True

    # Set up all the slots
    heuristic.set_prop('if_working_on_task', check_task)
    heuristic.set_prop('then_print_to_user', print_to_user)
    heuristic.set_prop('then_compute', compute_action)
    heuristic.set_prop('then_add_to_agenda', add_to_agenda)