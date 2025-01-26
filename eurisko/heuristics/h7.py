"""H7 heuristic implementation: Find instances for concepts with none."""
from typing import Any, Dict
import logging
from ..heuristics import rule_factory

logger = logging.getLogger(__name__)

def setup_h7(heuristic) -> None:
    """Configure H7: Find instances for concepts that have none."""
    # Set basic properties
    heuristic.set_prop('worth', 700)
    heuristic.set_prop('english', 
        "IF a concept has no known instances, THEN try to find some")
    heuristic.set_prop('abbrev', "Instantiate a concept having no known instances")
    heuristic.set_prop('arity', 1)
    
    # Initialize record properties
    def record_func(rule, context):
        return True
    heuristic.set_prop('then_add_to_agenda_record', record_func)
    heuristic.set_prop('then_print_to_user_record', record_func)
    heuristic.set_prop('overall_record', record_func)

    @rule_factory
    def if_potentially_relevant(rule, context):
        """Check if unit has no instances."""
        unit = context.get('unit')
        if not unit:
            return False
            
        instances = unit.get_prop('instances', [])
        return len(instances) == 0

    @rule_factory 
    def if_truly_relevant(rule, context):
        """Check if unit is a category or operation."""
        unit = context.get('unit')
        if not unit:
            return False
            
        # Check unit type
        unit_type = unit.get_prop('type', '')
        return unit_type in ['category', 'operation']

    @rule_factory
    def then_print_to_user(rule, context):
        """Print explanation of action."""
        unit = context.get('unit')
        if not unit:
            return False
            
        instance_type = unit.get_prop('instance_type', 'instances')
        logger.info(f"\nSince {unit.name} has no known {instance_type}, "
                   f"it is probably worth looking for some.")
        return True

    @rule_factory
    def then_add_to_agenda(rule, context):
        """Add task to find instances of the unit."""
        unit = context.get('unit')
        if not unit:
            return False
            
        # Create new task
        task = {
            'priority': unit.get_prop('worth', 500),
            'unit': unit,
            'slot': unit.get_prop('instance_type', 'instances'),
            'reasons': [
                f"To properly study {unit.name} we must gather empirical data "
                "about instances of that concept"
            ],
            'supplemental': {
                'credit_to': ['h7']
            }
        }
        
        # Add task and update results
        system = rule.unit_registry 
        if not system or not system.task_manager.add_task(task):
            return False
            
        system.add_task_result('new_tasks', "1 unit must be instantiated")
        return True