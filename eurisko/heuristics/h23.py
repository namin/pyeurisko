"""H23 heuristic implementation: Find interesting examples."""
from typing import Any, Dict
import logging
from ..heuristics import rule_factory

logger = logging.getLogger(__name__)

def setup_h23(heuristic) -> None:
    """Configure H23: Find interesting examples."""
    heuristic.set_prop('worth', 700)
    heuristic.set_prop('english', 
        "IF the current task is to find interesting examples of a unit, and it has some "
        "known examples already, THEN look over examples of the unit, and see if any of "
        "them are interesting")
    heuristic.set_prop('abbrev', "Find interesting examples")
    heuristic.set_prop('arity', 1)
    
    def record_func(rule, context):
        return True
    for record_type in ['then_compute', 'then_print_to_user', 'overall']:
        heuristic.set_prop(f'{record_type}_record', record_func)

    @rule_factory
    def if_working_on_task(rule, context):
        """Check if we can find interesting examples."""
        unit = context.get('unit')
        task = context.get('task')
        if not all([unit, task]) or task.get('slot') != 'interesting_examples':
            return False
            
        definition = unit.get_prop('interestingness')
        space_to_use = unit.get_prop('examples', [])
        if not definition or not space_to_use:
            return False
            
        context.update({
            'definition': definition,
            'space_to_use': space_to_use
        })
        return True

    @rule_factory
    def then_print_to_user(rule, context):
        """Print found interesting examples."""
        unit = context.get('unit')
        new_values = context.get('new_values')
        total = len(context.get('space_to_use', []))
        if not all([unit, new_values, total]):
            return False
            
        logger.info(f"\nFound {len(new_values)} of the {total} to be interesting.")
        logger.info(f"    Namely: {new_values}")
        return True

    @rule_factory 
    def then_compute(rule, context):
        """Test examples for interestingness."""
        unit = context.get('unit')
        definition = context.get('definition')
        space_to_use = context.get('space_to_use')
        
        current_examples = unit.get_prop('interesting_examples', [])
        new_examples = []
        
        for example in space_to_use:
            try:
                if definition(example):
                    logger.info("+")
                    new_examples.append(example)
                else:
                    logger.info("-")
            except Exception as e:
                logger.warning(f"Failed to test {example}: {e}")
                
        if new_examples:
            all_examples = current_examples + new_examples
            unit.set_prop('interesting_examples', all_examples)
            context['new_values'] = new_examples
            
            task_results = context.get('task_results', {})
            task_results['new_values'] = {
                'unit': unit.name,
                'slot': 'interesting_examples',
                'values': new_examples,
                'description': f"Found {len(new_examples)} interesting examples by "
                             f"examining {len(space_to_use)} examples"
            }
            context['task_results'] = task_results
            
        return bool(new_examples)