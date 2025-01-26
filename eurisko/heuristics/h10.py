"""H10 heuristic implementation: Find examples from operation outputs."""
from typing import Any, Dict
import logging
from ..heuristics import rule_factory

logger = logging.getLogger(__name__)

def setup_h10(heuristic) -> None:
    """Configure H10: Find examples from operation range."""
    heuristic.set_prop('worth', 700)
    heuristic.set_prop('english', 
        "IF the current task is to find examples of a unit, and it is the range of "
        "some operation f, THEN gather together the outputs of the I/O pairs stored "
        "on Applications of f")
    heuristic.set_prop('abbrev', "Find examples from operation outputs")
    heuristic.set_prop('arity', 1)
    
    def record_func(rule, context):
        return True
    for record_type in ['then_compute', 'then_add_to_agenda', 'then_print_to_user', 'overall']:
        heuristic.set_prop(f'{record_type}_record', record_func)
    heuristic.set_prop('then_add_to_agenda_failed_record', record_func)

    @rule_factory
    def if_working_on_task(rule, context):
        """Check if unit is in operation range."""
        unit = context.get('unit')
        task = context.get('task')
        if not all([unit, task]) or task.get('slot') != 'examples':
            return False
            
        op_to_use = next(iter(unit.get_prop('is_range_of', [])), None)
        context['op_to_use'] = op_to_use
        return bool(op_to_use)

    @rule_factory
    def then_print_to_user(rule, context):
        """Print example counts."""
        unit = context.get('unit')
        new_values = context.get('new_values', [])
        if not all([unit, new_values]):
            return False
            
        logger.info(f"\nInstantiated {unit.name}; there are now "
                   f"{len(unit.get_prop('examples', []))} examples")
        logger.info(f"    The new ones are: {new_values}")
        return True

    @rule_factory 
    def then_compute(rule, context):
        """Extract examples from operation applications."""
        unit = context.get('unit')
        op_to_use = context.get('op_to_use')
        if not all([unit, op_to_use]):
            return False
            
        op_unit = rule.unit_registry.get_unit(op_to_use)
        if not op_unit:
            return False
            
        space_to_use = op_unit.get_prop('applications', [])
        context['space_to_use'] = space_to_use
        if not space_to_use:
            return True  # Allow then_add_to_agenda to handle empty case
            
        current_examples = unit.get_prop('examples', []) 
        non_examples = unit.get_prop('non_examples', [])
        new_examples = []
        
        for application in space_to_use:
            output = application.get('result')
            if output and output not in current_examples + non_examples:
                new_examples.append(output)
                
        if new_examples:
            unit.set_prop('examples', current_examples + new_examples)
            context['new_values'] = new_examples
            task_results = context.get('task_results', {})
            task_results['new_values'] = {
                'unit': unit.name,
                'examples': new_examples,
                'description': f"Found {len(new_examples)} examples by examining "
                             f"applications of {op_to_use}"
            }
            context['task_results'] = task_results
            
        return True

    @rule_factory
    def then_add_to_agenda(rule, context):
        """Add tasks to find more applications if needed."""
        unit = context.get('unit')
        task = context.get('task')
        op_to_use = context.get('op_to_use')
        space_to_use = context.get('space_to_use')
        if not all([unit, task, op_to_use]) or space_to_use:
            return False
            
        # Add tasks to find applications and retry examples
        new_tasks = [
            {
                'priority': task['priority'] - 1,
                'unit': op_to_use,
                'slot': 'applications',
                'reasons': ["Recent task was stymied for lack of such applications"],
                'supplemental': {'credit_to': ['h10']}
            },
            {
                'priority': task['priority'] // 2,
                'unit': unit.name,
                'slot': 'examples',
                'reasons': [f"Had to suspend whilst gathering applications of {op_to_use}"],
                'supplemental': task.get('supplemental', {})
            }
        ]
        
        for new_task in new_tasks:
            if not rule.task_manager.add_task(new_task):
                return False
                
        task_results = context.get('task_results', {})
        task_results['new_tasks'] = [
            f"1 task to find Applications of {op_to_use} "
            "and 1 task just like the current one"
        ]
        context['task_results'] = task_results
        
        logger.info(f"\nHmmm... can't proceed with this until some Applications "
                   f"of {op_to_use} are known.")
        return True