"""H22 heuristic implementation: Look for interesting instances."""
from typing import Any, Dict
import logging
from ..heuristics import rule_factory

logger = logging.getLogger(__name__)

def setup_h22(heuristic) -> None:
    """Configure H22: Find interesting unit instances."""
    heuristic.set_prop('worth', 500)
    heuristic.set_prop('english', 
        "IF instances of a unit have been found, THEN place a task on the Agenda to "
        "see if any of them are unusually interesting")
    heuristic.set_prop('abbrev', "Check instances of a unit for gems")
    heuristic.set_prop('arity', 1)
    
    def record_func(rule, context):
        return True
    for record_type in ['then_add_to_agenda', 'then_print_to_user', 'overall']:
        heuristic.set_prop(f'{record_type}_record', record_func)

    @rule_factory 
    def if_finished_working_on_task(rule, context):
        """Check if we should evaluate instance interestingness."""
        unit = context.get('unit')
        task = context.get('task')
        if not all([unit, task]):
            return False
            
        unit_instances = unit.get_prop('instances', {})
        cur_slot = task.get('slot')
        
        if not unit_instances or not cur_slot:
            return False
            
        # Check if interestingness metric exists
        if not unit.get_prop('interestingness'):
            return False
            
        # Get more interesting slot
        more_interesting = unit.get_prop('more_interesting_slots', [])
        if not more_interesting:
            return False
            
        more_interesting_slot = more_interesting[0]
        context['more_interesting_slot'] = more_interesting_slot
        
        # Avoid infinite loops
        if more_interesting_slot == cur_slot:
            new_values = task_results.get('new_values')
            if not new_values:
                return False
                
        return True

    @rule_factory
    def then_print_to_user(rule, context):
        """Print task description."""
        unit = context.get('unit')
        if not unit:
            return False
            
        examples = len(unit.get_prop('examples', []))
        logger.info(f"A new task was added to the agenda, to see which of the "
                   f"{examples} are interesting ones.")
        return True

    @rule_factory
    def then_add_to_agenda(rule, context):
        """Add task to check instance interestingness."""
        unit = context.get('unit')
        more_interesting_slot = context.get('more_interesting_slot')
        if not all([unit, more_interesting_slot]):
            return False
            
        task = {
            'priority': (unit.worth_value() + rule.worth_value()) // 2,
            'unit': unit,
            'slot': more_interesting_slot,
            'reasons': [
                "Now that instances of a unit have been found, see if any are "
                "unusually interesting"
            ],
            'supplemental': {
                'credit_to': ['h22']
            }
        }
        
        if not rule.task_manager.add_task(task):
            return False
            
        task_results = context.get('task_results', {})
        task_results['new_tasks'] = [
            "1 unit's instances must be evaluated for Interestingness"
        ]
        context['task_results'] = task_results
        
        return True