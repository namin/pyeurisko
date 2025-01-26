"""H5-Good heuristic implementation: Choose valuable slots to specialize."""
from typing import Any, Dict, List
import random
import logging
from ..heuristics import rule_factory

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

    @rule_factory
    def if_working_on_task(rule, context):
        """Check if we need to choose valuable slots to specialize."""
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
        """Select valuable slots for specialization."""
        unit = context.get('unit')
        task = context.get('task')
        if not unit or not task:
            return False

        # Get available slots
        unit_slots = unit.get_prop('slots') or []
        slot_types = rule.unit_registry.get_units_by_category('slot')
        valid_slots = set(unit_slots) & set(slot_types)
        slots = list(valid_slots) if valid_slots else []

        if not slots:
            return False

        # Score and select valuable slots
        slot_scores = []
        for slot_name in slots:
            slot = rule.unit_registry.get_unit(slot_name)
            if not slot:
                continue
                
            score = slot.worth_value()
            # Consider past specializations
            if slot.get_prop('successful_specializations'):
                score *= 1.5
                
            slot_scores.append((slot_name, score))
            
        # Select top scoring slots
        slot_scores.sort(key=lambda x: x[1], reverse=True)
        selected_slots = [s[0] for s in slot_scores[:3]]
        
        if not selected_slots:
            return False
        
        # Update context and task
        context['slots_to_change'] = selected_slots
        context['slot_scores'] = {name: score for name, score in slot_scores}
        task['slots_to_change'] = selected_slots
        task['credit_to'] = task.get('credit_to', []) + ['h5-good']
        
        return True

    @rule_factory
    def then_print_to_user(rule, context):
        """Print explanation of valuable slot choices."""
        unit = context.get('unit')
        slots = context.get('slots_to_change', [])
        slot_scores = context.get('slot_scores', {})
        
        if not unit or not slots:
            return False
            
        logger.info(f"\n{unit.name} will be specialized by specializing these "
                   f"valuable slots:")
        
        for slot in slots:
            score = slot_scores.get(slot, 0)
            logger.info(f"- {slot} (worth score: {score:.1f})")
            
        return True

    @rule_factory
    def then_add_to_agenda(rule, context):
        """Add specialization tasks for chosen valuable slots."""
        unit = context.get('unit')
        selected_slots = context.get('slots_to_change', [])
        slot_scores = context.get('slot_scores', {})
        task = context.get('task')
        
        if not all([unit, selected_slots, task]):
            return False

        base_priority = task.get('priority', 500)
        successful_adds = 0
        
        # Create and add tasks for each selected slot
        for slot in selected_slots:
            slot_worth = slot_scores.get(slot, 500)
            new_task = {
                'priority': int((base_priority + rule.worth_value() + slot_worth) / 3),
                'unit': unit.name,
                'slot': 'specializations',
                'reasons': [f"A new unit will be created by specializing the {slot} "
                          f"slot of {unit.name}; that slot was chosen because of its "
                          f"high worth score ({slot_scores.get(slot, 0):.1f})."],
                'supplemental': {
                    'slot_to_change': slot,
                    'credit_to': ['h5-good'] + (task.get('credit_to', []))
                }
            }
            
            if rule.task_manager.add_task(new_task):
                successful_adds += 1
                
        if successful_adds > 0:
            context['task_results'] = {
                'new_tasks': f"{successful_adds} specific valuable slots of {unit.name} to find specializations of"
            }
            return True
            
        return False