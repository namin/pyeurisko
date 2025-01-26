"""H9 heuristic implementation: Find examples from generalizations."""
from typing import Any, Dict
import logging
from ..heuristics import rule_factory

logger = logging.getLogger(__name__)

def setup_h9(heuristic) -> None:
    """Configure H9: Find examples by checking generalizations."""
    heuristic.set_prop('worth', 700)
    heuristic.set_prop('english', 
        "IF the current task is to find examples of a unit, and it has a definition, "
        "THEN look over instances of generalizations of the unit, and see if any of "
        "them are valid examples of this as well")
    heuristic.set_prop('abbrev', "Find examples by checking generalizations")
    heuristic.set_prop('arity', 1)
    
    def record_func(rule, context):
        return True
    heuristic.set_prop('then_compute_record', record_func)
    heuristic.set_prop('then_print_to_user_record', record_func)
    heuristic.set_prop('overall_record', record_func)
    heuristic.set_prop('then_compute_failed_record', record_func)

    @rule_factory
    def if_working_on_task(rule, context):
        """Check if we can find examples from generalizations."""
        unit = context.get('unit')
        task = context.get('task')
        if not unit or not task:
            return False
            
        if task.get('slot') != 'examples':
            return False
            
        # Get definition and generalizations
        definition = unit.get_prop('definition')
        generalizations = unit.get_prop('generalizations', [])
        if not definition or not generalizations:
            return False
            
        # Get non-specialized generalizations
        specializations = unit.get_prop('specializations', [])
        space_to_use = [g for g in generalizations if g not in specializations]
                
        context['definition'] = definition
        context['space_to_use'] = space_to_use
        return bool(space_to_use)

    @rule_factory
    def then_print_to_user(rule, context):
        """Print found examples."""
        unit = context.get('unit')
        new_values = context.get('new_values', [])
        if not unit or not new_values:
            return False
            
        logger.info(f"\nInstantiated {unit.name}; found {len(new_values)} examples")
        logger.info(f"    Namely: {new_values}")
        return True

    @rule_factory 
    def then_compute(rule, context):
        """Try definition on examples from generalizations."""
        unit = context.get('unit')
        definition = context.get('definition')
        space_to_use = context.get('space_to_use')
        if not all([unit, definition, space_to_use]):
            return False
            
        current_examples = unit.get_prop('examples', [])
        non_examples = unit.get_prop('non_examples', [])
        new_examples = []
        max_examples = 400  # From original LISP code
        count = 0
        
        # Check examples from each generalization
        for gen_name in space_to_use:
            if count >= max_examples:
                break
                
            gen_unit = rule.unit_registry.get_unit(gen_name)
            if not gen_unit:
                continue
                
            for example in gen_unit.get_prop('examples', []):
                if count >= max_examples:
                    break
                    
                # Skip if already processed
                if example in current_examples or example in non_examples:
                    continue
                    
                count += 1
                try:
                    # Test definition and update lists
                    if definition(example):
                        new_examples.append(example)
                        current_examples.append(example)
                    else:
                        non_examples.append(example)
                except Exception as e:
                    logger.warning(f"Failed to test {example} with {unit.name}'s definition: {e}")
                    
        if new_examples:
            # Update unit properties
            unit.set_prop('examples', current_examples)
            unit.set_prop('non_examples', non_examples)
            context['new_values'] = new_examples
            
            # Update task results
            task_results = context.get('task_results', {})
            task_results['new_values'] = {
                'unit': unit.name,
                'slot': 'examples',
                'values': new_examples,
                'description': f"Found {len(new_examples)} examples by examining "
                             f"examples of {len(space_to_use)} generalizations"
            }
            context['task_results'] = task_results
            
        return bool(new_examples)