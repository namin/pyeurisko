"""H4 heuristic implementation: Gather data about newly synthesized units."""
from typing import Any, Dict
import logging
from ..heuristics import rule_factory

logger = logging.getLogger(__name__)

def setup_h4(heuristic) -> None:
    """Configure H4: Trigger empirical data gathering for new units."""
    heuristic.set_prop('worth', 703)
    heuristic.set_prop('english',
        "IF a new unit has been synthesized, THEN place a task on the Agenda "
        "to gather new empirical data about it")
    heuristic.set_prop('abbrev', "about concepts gather data new empirical")
    heuristic.set_prop('arity', 1)

    @rule_factory
    def if_potentially_relevant(rule, context):
        """Initial relevance check."""
        task = context.get('task')
        if not task:
            return False
            
        task_type = task.get('task_type', '')
        if task_type not in ['specialization', 'define_concept']:
            return False
            
        return True

    @rule_factory 
    def if_working_on_task(rule, context):
        """Check for newly created units."""
        task = context.get('task')
        if not task:
            logger.debug("H4 if_working_on_task: No task")
            return False
            
        task_type = task.get('task_type', '')
        logger.debug(f"H4 task type: {task_type}")
        
        if task_type not in ['specialization', 'define_concept']: 
            logger.debug("H4 if_working_on_task: Wrong task type")
            return False

        # New units should be defined in task results
        task_results = context.get('task_results', {})
        new_units = task_results.get('new_units', [])
        
        # Filter valid units
        valid_units = [u for u in new_units if hasattr(u, 'name')]
        if not valid_units:
            logger.debug("H4 if_working_on_task: No valid new units with names")
            return False
            
        logger.debug(f"H4 if_working_on_task: Found {len(valid_units)} valid new units: {[u.name for u in valid_units]}")
        context['new_units'] = valid_units
        return True

    @rule_factory
    def then_print_to_user(rule, context):
        """Report on units discovered."""
        new_units = context.get('new_units', [])
        if not new_units:
            logger.debug("H4 then_print_to_user: No new units")
            return False
            
        unit_names = [u.name for u in new_units]
        logger.info(f"\n{len(new_units)} new units ({', '.join(unit_names)}) " 
                   f"need empirical data gathering.")
        return True

    @rule_factory
    def then_add_to_agenda(rule, context):
        """Add tasks to gather data about units."""
        new_units = context.get('new_units', [])
        if not new_units:
            logger.debug("H4 then_add_to_agenda: No new units")
            return False
            
        task_manager = rule.task_manager
        if not task_manager:
            logger.debug("H4 then_add_to_agenda: No task manager")
            return False

        tasks_added = 0
        for unit in new_units:
            # Get instance slot name based on unit type
            instances_slot = 'examples'  # Default
            if hasattr(unit, 'get_prop') and unit.get_prop('isa'):
                logger.debug(f"H4 unit {unit.name} isa: {unit.get_prop('isa')}")
                if 'category' in unit.get_prop('isa'):
                    instances_slot = 'examples'
                elif 'op' in unit.get_prop('isa'):
                    instances_slot = 'applics'
                    
            # Create task
            logger.debug(f"H4 adding task for unit {unit.name} slot {instances_slot}")
            new_task = {
                'priority': max(300, int((rule.worth_value() + unit.worth_value()) / 2)),
                'unit': unit.name,
                'slot': instances_slot,
                'reasons': ["After a unit is synthesized, gather empirical data about it."],
                'task_type': 'find_instances',
                'supplemental': {
                    'credit_to': ['h4']
                }
            }
            task_manager.add_task(new_task)
            tasks_added += 1

        if tasks_added == 0:
            logger.debug("H4 then_add_to_agenda: No tasks added")
            return False
            
        # Record task creation
        task_results = context.get('task_results', {})
        task_results['new_tasks'] = [
            f"{tasks_added} new units require empirical data"
        ]
        task_results['status'] = 'completed'
        task_results['success'] = True
        context['task_results'] = task_results
        logger.debug(f"H4 then_add_to_agenda: Added {tasks_added} tasks")
        return True