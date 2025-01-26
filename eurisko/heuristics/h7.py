"""H7 heuristic implementation: Find instances for concepts with none.

This heuristic triggers when a concept has no known instances, prompting the system
to search for some. It works for both categories and operators.
"""

from typing import Any, Dict
from ..units import Unit
import logging
from ..heuristics import rule_factory

logger = logging.getLogger(__name__)

def setup_h7(heuristic) -> None:
    """Configure H7: Find instances for concepts with no known instances."""
    # Set properties from original LISP implementation
    heuristic.set_prop('worth', 700)
    heuristic.set_prop('english',
        "IF a concept has no known instances, THEN try to find some")
    heuristic.set_prop('abbrev', "Instantiate a concept having no known instances")
    heuristic.set_prop('arity', 1)
    
    # Set record counts from original
    heuristic.set_prop('then_add_to_agenda_record', (11017, 172))
    heuristic.set_prop('then_print_to_user_record', (21543, 172))
    heuristic.set_prop('overall_record', (71147, 172))

    @rule_factory
    def if_potentially_relevant(rule, context):
        """Check if the concept has no instances."""
        unit = context.get('unit')
        if not unit:
            return False
            
        return not bool(unit.get_prop('examples'))

    @rule_factory
    def if_truly_relevant(rule, context):
        """Check if the concept is a category or operator."""
        unit = context.get('unit')
        if not unit:
            return False
            
        isa = unit.get_prop('isa')
        if not isa:
            return False
            
        return 'category' in isa or 'op' in isa

    @rule_factory
    def then_print_to_user(rule, context):
        """Print explanation of the instance-finding task."""
        unit = context.get('unit')
        if not unit:
            return False
            
        logger.info(f"\nSince {unit.name} has no known examples, "
                   f"it is probably worth looking for some.")
        return True

    @rule_factory
    def then_compute(rule, context):
        """Create task to find instances."""
        unit = context.get('unit')
        if not unit:
            return False
            
        # Initialize context if needed
        if not isinstance(context.get('task'), dict):
            context['task'] = {}
            
        # Create task
        task = {
            'priority': unit.worth_value(),
            'task_type': 'find_instances',
            'target_unit': unit.name,
            'supplemental': {
                'credit_to': ['h7']
            }
        }
        
        # Add task to manager
        if not rule.task_manager.add_task(task):
            return False
            
        # Update task results
        context['task_results'] = {
            'new_tasks': "1 unit must be instantiated"
        }
        
        return True