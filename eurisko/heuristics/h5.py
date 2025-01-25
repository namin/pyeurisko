"""H5 heuristic implementation: Choose multiple slots to specialize."""
from typing import Any, Dict, List
import random
import logging

logger = logging.getLogger(__name__)

def setup_h5(heuristic) -> None:
    """Configure H5: Choose multiple slots to randomly specialize."""
    heuristic.set_prop('worth', 151)
    heuristic.set_prop('english', 
        "IF the current task is to specialize a unit, and no specific slot has been "
        "chosen to be the one changed, THEN randomly select which slots to specialize")
    heuristic.set_prop('abbrev', "Choose some particular slots of u to specialize")
    heuristic.set_prop('arity', 1)
    heuristic.set_prop('subsumes', ['h3'])
    heuristic.set_prop('subsumed_by', ['h5-criterial', 'h5-good'])

    def check_task(context: Dict[str, Any]) -> bool:
        """Check if we need to choose slots to specialize."""
        unit = context.get('unit')
        task = context.get('task')
        if not unit or not task:
            return False
            
        # Check task type and missing slot selection
        is_specialization = task.get('task_type') == 'specialization'
        no_slots_chosen = not task.get('slots_to_change')
        
        # Check agenda count as in LISP
        if hasattr(heuristic, 'task_manager'):
            similar_tasks = sum(1 for t in heuristic.task_manager.tasks
                              if (t.get('unit') == unit.name and 
                                  t.get('task_type') == 'specialization'))
            if similar_tasks >= 7:  # LISP used 7 as threshold
                return False
                
        return is_specialization and no_slots_chosen

    def print_to_user(context: Dict[str, Any]) -> bool:
        """Print explanation of slot choices."""
        unit = context.get('unit')
        slots = context.get('slots_to_change', [])
        if not unit or not slots:
            return False
            
        logger.info(f"\n{unit.name} will be specialized by specializing the following "
                   f"of its slots: {slots}")
        return True

    def compute_action(context: Dict[str, Any]) -> bool:
        """Randomly select slots for specialization."""
        unit = context.get('unit')
        task = context.get('task')
        if not unit or not task:
            return False

        # Get valid slots - intersection with known slot types
        unit_slots = unit.get_prop('slots') or []
        if hasattr(heuristic, 'unit_registry'):
            slot_types = heuristic.unit_registry.get_units_by_category('slot')
            valid_slots = set(unit_slots) & set(slot_types)
            slots = list(valid_slots) if valid_slots else unit_slots
        else:
            slots = unit_slots

        if not slots:
            return False

        # Select multiple slots randomly
        num_slots = min(random.randint(1, 3), len(slots))
        selected_slots = random.sample(slots, num_slots)
        
        # Update context and task
        context['slots_to_change'] = selected_slots
        task['slots_to_change'] = selected_slots
        task['credit_to'] = task.get('credit_to', []) + ['h5']
        
        return True

    def add_to_agenda(context: Dict[str, Any]) -> bool:
        """Add specialization tasks for chosen slots."""
        unit = context.get('unit')
        selected_slots = context.get('slots_to_change', [])
        task = context.get('task')
        
        if not all([unit, selected_slots, task]) or not hasattr(heuristic, 'task_manager'):
            return False

        new_tasks = []
        base_priority = task.get('priority', 500)
        
        for slot in selected_slots:
            # Create specialized task for each slot
            new_task = {
                'priority': int((base_priority + heuristic.worth_value() + 
                               unit.worth_value()) / 3),
                'unit': unit,
                'slot': 'specializations',
                'reasons': [f"A new unit will be created by specializing the {slot} "
                          f"slot of {unit.name}; that slot was chosen randomly."],
                'supplemental': {
                    'slot_to_change': slot,
                    'credit_to': ['h5'] + (task.get('credit_to', []))
                }
            }
            new_tasks.append(new_task)
            
        # Sort tasks by priority and add to manager
        for task in sorted(new_tasks, key=lambda x: x['priority'], reverse=True):
            heuristic.task_manager.add_task(task)
            
        # Record task creation
        if hasattr(heuristic, 'add_task_result'):
            heuristic.add_task_result('new_tasks',
                f"{len(selected_slots)} specific slots of {unit.name} to find specializations of")
            
        return True

    # Set up all the slots
    heuristic.set_prop('if_working_on_task', check_task)
    heuristic.set_prop('then_print_to_user', print_to_user)
    heuristic.set_prop('then_compute', compute_action)
    heuristic.set_prop('then_add_to_agenda', add_to_agenda)