"""H5-CRITERIAL heuristic implementation: Choose criterial slots to specialize."""
from typing import Any, Dict
import logging
from ..heuristics import rule_factory

logger = logging.getLogger(__name__)

def setup_h5_criterial(heuristic) -> None:
    """Configure H5-CRITERIAL: Choose criterial slots."""
    heuristic.set_prop('worth', 700)
    heuristic.set_prop('english', 
        "IF the current task is to specialize a unit, and no specific slot has been chosen "
        "to be the one changed, THEN randomly select which criterial slots to specialize")
    heuristic.set_prop('abbrev', "Choose some particular criterial slots to specialize")
    heuristic.set_prop('arity', 1)
    heuristic.set_prop('subsumes', ['h3', 'h5'])
    
    def record_func(rule, context):
        return True
    for record_type in ['then_compute', 'then_add_to_agenda', 'then_print_to_user', 'overall']:
        heuristic.set_prop(f'{record_type}_record', record_func)

    @rule_factory
    def if_working_on_task(rule, context):
        """Check if we need to choose slots for specialization."""
        unit = context.get('unit')
        task = context.get('task')
        if not all([unit, task]):
            return False
            
        if task.get('slot') != 'specializations':
            return False
            
        if 'slot_to_change' in task.get('supplemental', {}):
            return False
            
        similar_tasks = sum(1 for t in rule.task_manager.agenda
                          if (t.unit_name == unit.name and 
                              t.slot == 'specializations'))
        return similar_tasks <= 7

    @rule_factory
    def then_print_to_user(rule, context):
        """Print chosen slots."""
        unit = context.get('unit')
        slots = context.get('slots_to_change')
        if not all([unit, slots]):
            return False
            
        logger.info(f"\n{unit.name} will be specialized by specializing the "
                   f"following of its criterial slots: {slots}")
        return True

    @rule_factory
    def then_compute(rule, context):
        """Choose criterial slots for specialization."""
        unit = context.get('unit')
        task = context.get('task')
        if not all([unit, task]):
            return False
            
        unit_slots = unit.get_prop('slots', [])
        criterial_slots = rule.unit_registry.get_units_by_category('criterial_slot')
        if not criterial_slots:
            return False
            
        valid_slots = list(set(unit_slots) & set(criterial_slots))
        if not valid_slots:
            return False
            
        context['slots_to_change'] = valid_slots
        context['credit_to'] = task.get('supplemental', {}).get('credit_to', [])
        return True

    @rule_factory
    def then_add_to_agenda(rule, context):
        """Add tasks to specialize chosen slots."""
        unit = context.get('unit')
        task = context.get('task')
        slots = context.get('slots_to_change')
        creditors = context.get('credit_to', [])
        if not all([unit, task, slots]):
            return False
            
        tasks = []
        for slot in slots:
            slot_unit = rule.unit_registry.get_unit(slot)
            priority = (task['priority'] + slot_unit.worth_value() + 
                       rule.worth_value()) // 3
            
            tasks.append({
                'priority': priority,
                'unit': unit.name,
                'slot': 'specializations',
                'reasons': [f"A new unit will be created by specializing the {slot} "
                          f"slot of {unit.name}; that criterial slot was chosen randomly."],
                'supplemental': {
                    'slot_to_change': slot,
                    'credit_to': ['h5_criterial'] + creditors
                }
            })
            
        tasks.sort(key=lambda t: t['priority'], reverse=True)
        for task in tasks:
            if not rule.task_manager.add_task(task):
                return False
                
        task_results = context.get('task_results', {})
        task_results['new_tasks'] = [
            f"{len(slots)} specific criterial slots of {unit.name} to find specializations of"
        ]
        context['task_results'] = task_results
        return True