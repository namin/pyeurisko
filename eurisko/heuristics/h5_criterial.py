"""H5-Criterial heuristic implementation: Choose criterial slots to specialize."""
from typing import Any, Dict, List
import random
import logging
from ..heuristics import rule_factory

logger = logging.getLogger(__name__)

def setup_h5_criterial(heuristic) -> None:
    """Configure H5-Criterial: Choose criterial slots for specialization."""
    heuristic.set_prop('worth', 700)
    heuristic.set_prop('english', 
        "IF the current task is to specialize a unit, and no specific slot has been "
        "chosen to be the one changed, THEN randomly select which criterial slots to specialize")
    heuristic.set_prop('abbrev', "Choose some particular criterial slots of u to specialize")
    heuristic.set_prop('arity', 1)
    heuristic.set_prop('subsumes', ['h3', 'h5'])
    heuristic.set_prop('creditors', ['h6', 'h5', 'h1'])
    
    # Initialize records as in LISP
    heuristic.set_prop('then_compute_record', (3850, 46))
    heuristic.set_prop('then_add_to_agenda_record', (12150, 46))
    heuristic.set_prop('then_print_to_user_record', (7532, 46))
    heuristic.set_prop('overall_record', (37450, 46))

    @rule_factory
    def if_working_on_task(rule, context):
        """Check if we need to choose criterial slots to specialize."""
        unit = context.get('unit')
        task = context.get('task')
        if not unit or not task:
            return False
            
        is_specialization = task.get('task_type') == 'specialization'
        no_slots_chosen = not task.get('slot_to_change')
        
        # Check for too many similar tasks
        similar_tasks = sum(1 for t in rule.task_manager.tasks
                          if (t.get('unit') == unit.name and 
                              t.get('task_type') == 'specialization'))
        if similar_tasks >= 7:
            return False
                
        return is_specialization and no_slots_chosen

    @rule_factory
    def then_compute(rule, context):
        """Select criterial slots for specialization."""
        unit = context.get('unit')
        task = context.get('task')
        if not unit or not task:
            return False

        # Get criterial slots
        unit_slots = unit.get_prop('slots') or []
        criterial_slots = rule.unit_registry.get_units_by_category('criterial-slot')
        valid_slots = set(unit_slots) & set(criterial_slots)
        slots = list(valid_slots) if valid_slots else []

        if not slots:
            return False

        # Select multiple criterial slots randomly
        num_slots = min(random.randint(1, 3), len(slots))
        selected_slots = random.sample(slots, num_slots)
        
        # Update context and task
        context['slots_to_change'] = selected_slots
        task['slots_to_change'] = selected_slots
        task['credit_to'] = task.get('credit_to', []) + ['h5-criterial']
        
        return True

    @rule_factory
    def then_print_to_user(rule, context):
        """Print explanation of criterial slot choices."""
        unit = context.get('unit')
        slots = context.get('slots_to_change', [])
        if not unit or not slots:
            return False
            
        logger.info(f"\n{unit.name} will be specialized by specializing the following "
                   f"of its criterial slots: {slots}")
        return True

    @rule_factory
    def then_add_to_agenda(rule, context):
        """Add specialization tasks for chosen criterial slots."""
        unit = context.get('unit')
        selected_slots = context.get('slots_to_change', [])
        task = context.get('task')
        
        if not all([unit, selected_slots, task]):
            return False

        base_priority = task.get('priority', 500)
        successful_adds = 0
        
        # Create and add tasks for each selected slot
        for slot in selected_slots:
            new_task = {
                'priority': int((base_priority + rule.worth_value() + 
                               unit.worth_value()) / 3),
                'unit': unit.name,
                'slot': 'specializations',
                'reasons': [f"A new unit will be created by specializing the {slot} "
                          f"slot of {unit.name}; that criterial slot was chosen randomly."],
                'supplemental': {
                    'slot_to_change': slot,
                    'credit_to': ['h5-criterial'] + (task.get('credit_to', []))
                }
            }
            
            if rule.task_manager.add_task(new_task):
                successful_adds += 1
                
        if successful_adds > 0:
            context['task_results'] = {
                'new_tasks': f"{successful_adds} specific criterial slots of {unit.name} to find specializations of"
            }
            return True
            
        return False