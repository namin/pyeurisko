"""H15 heuristic implementation: Find examples from multiple operations."""
from typing import Any, Dict
import logging
from ..heuristics import rule_factory

logger = logging.getLogger(__name__)

def setup_h15(heuristic) -> None:
    """Configure H15: Find examples from operation range outputs."""
    heuristic.set_prop('worth', 700)
    heuristic.set_prop('english', 
        "IF the current task is to find examples of a unit, and it is the range of "
        "some operation f, THEN gather together the outputs of the I/O pairs stored on "
        "Applications of f")
    heuristic.set_prop('abbrev', "Find examples from operation range outputs")
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
            
        ops_to_use = unit.get_prop('is_range_of', [])
        context['ops_to_use'] = ops_to_use
        return bool(ops_to_use)

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
        ops_to_use = context.get('ops_to_use')
        if not all([unit, ops_to_use]):
            return False
            
        space_to_use = []
        for op_name in ops_to_use:
            op_unit = rule.unit_registry.get_unit(op_name)
            if op_unit:
                space_to_use.extend(op_unit.get_prop('applications', []))
                
        context['space_to_use'] = space_to_use
        if not space_to_use:
            return True  # Allow then_add_to_agenda to handle empty case
            
        current_examples = unit.get_prop('examples', [])
        new_examples = []
        
        for application in space_to_use:
            output = application.get('result')
            if output and output not in current_examples:
                new_examples.append(output)
                
        if new_examples:
            unit.set_prop('examples', current_examples + new_examples)
            context['new_values'] = new_examples
            
            task_results = context.get('task_results', {})
            task_results['new_values'] = {
                'unit': unit.name,
                'examples': new_examples,
                'description': f"Found {len(new_examples)} examples by examining "
                             f"applications of {len(ops_to_use)} operations"
            }
            context['task_results'] = task_results
            
        return True

    @rule_factory
    def then_add_to_agenda(rule, context):
        """Add tasks to find more applications if needed."""
        unit = context.get('unit')
        task = context.get('task')
        ops_to_use = context.get('ops_to_use')
        space_to_use = context.get('space_to_use')
        if not all([unit, task, ops_to_use]) or space_to_use:
            return False
            
        # Create tasks for each operation
        new_tasks = []
        for op in ops_to_use:
            new_tasks.append({
                'priority': task['priority'] - 1,
                'unit': op,
                'slot': 'applications',
                'reasons': [f"Recent task was stymied for lack of such applications"],
                'supplemental': {'credit_to': ['h15']}
            })
            
        # Add task to retry examples
        new_tasks.append({
            'priority': task['priority'] // 2,
            'unit': unit.name,
            'slot': 'examples',
            'reasons': [f"Had to suspend whilst gathering applications of {ops_to_use}"],
            'supplemental': task.get('supplemental', {})
        })
        
        for new_task in new_tasks:
            if not rule.task_manager.add_task(new_task):
                return False
                
        task_results = context.get('task_results', {})
        task_results['new_tasks'] = [
            f"{len(ops_to_use)} tasks to find Applications and 1 task "
            "just like the current one"
        ]
        context['task_results'] = task_results
        
        logger.info(f"\nHmmm... can't proceed with this until some Applications "
                   f"of {ops_to_use} are known.")
        return True