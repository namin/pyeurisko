"""H17 heuristic implementation: Generalize slots."""
from typing import Any, Dict
import logging
import random
from ..heuristics import rule_factory

logger = logging.getLogger(__name__)

def setup_h17(heuristic) -> None:
    """Configure H17: Choose slots to generalize."""
    heuristic.set_prop('worth', 600)
    heuristic.set_prop('english', 
        "IF the current task is to generalize a unit, and no general slot has been "
        "chosen to be the one changed, THEN randomly select which slots to generalize")
    heuristic.set_prop('abbrev', "Generalize u by generalizing some random slots")
    heuristic.set_prop('arity', 1)
    
    def record_func(rule, context):
        return True
    for record_type in ['then_compute', 'then_add_to_agenda', 'then_print_to_user', 'overall']:
        heuristic.set_prop(f'{record_type}_record', record_func)

    @rule_factory
    def if_working_on_task(rule, context):
        """Check if we should choose slots for generalization."""
        unit = context.get('unit')
        task = context.get('task')
        if not all([unit, task]):
            return False
            
        if 'slot_to_change' in task.get('supplemental', {}):
            return False
            
        if task.get('slot') != 'generalizations':
            return False
            
        # Check similar task count
        task_manager = rule.task_manager
        if not task_manager:
            return False
            
        similar_tasks = sum(1 for t in task_manager.agenda
                          if (t.unit_name == unit.name and 
                              t.slot == 'generalizations'))
        return similar_tasks <= 7

    @rule_factory
    def then_print_to_user(rule, context):
        """Print chosen slots."""
        unit = context.get('unit')
        slots = context.get('slots_to_change')
        if not all([unit, slots]):
            return False
            
        logger.info(f"\n{unit.name} will be generalized by generalizing the "
                   f"following slots: {slots}")
        return True

    @rule_factory
    def then_compute(rule, context):
        """Choose slots to generalize."""
        unit = context.get('unit')
        task = context.get('task')
        if not all([unit, task]):
            return False
            
        # Get valid slots for generalization
        unit_slots = unit.get_prop('slots', [])
        slot_types = rule.unit_registry.get_units_by_category('slot')
        if not slot_types:
            return False
            
        valid_slots = list(set(unit_slots) & set(slot_types))
        if not valid_slots:
            return False
            
        # Randomly select subset
        slots_to_change = random.sample(valid_slots, random.randint(1, len(valid_slots)))
        context['slots_to_change'] = slots_to_change
        
        # Store task creditors
        context['credit_to'] = task.get('supplemental', {}).get('credit_to', [])
        
        return True

    @rule_factory
    def then_add_to_agenda(rule, context):
        """Add tasks to generalize chosen slots."""
        unit = context.get('unit')
        task = context.get('task')
        slots = context.get('slots_to_change')
        creditors = context.get('credit_to', [])
        
        if not all([unit, task, slots]):
            return False
            
        tasks = []
        # Calculate base priority 
        base_priority = task['priority']
        h17_worth = rule.worth_value()
        
        for slot in slots:
            # Get slot worth if available
            slot_unit = rule.unit_registry.get_unit(slot)
            slot_worth = slot_unit.worth_value() if slot_unit else 500
            
            # Average priorities
            priority = (base_priority + h17_worth + slot_worth) // 3
            
            reason = (f"A new unit will be created by generalizing the {slot} "
                     f"slot of {unit.name}")
            
            tasks.append({
                'priority': priority,
                'unit': unit.name,
                'slot': 'generalizations',
                'reasons': [reason],
                'supplemental': {
                    'slot_to_change': slot,
                    'credit_to': ['h17'] + creditors
                }
            })
            
        # Sort by priority and add to agenda
        tasks.sort(key=lambda t: t['priority'], reverse=True)
        for task in tasks:
            if not rule.task_manager.add_task(task):
                return False
                
        task_results = context.get('task_results', {})
        task_results['new_tasks'] = [
            f"{len(slots)} specific slots of {unit.name} to find generalizations of"
        ]
        context['task_results'] = task_results
        
        return True