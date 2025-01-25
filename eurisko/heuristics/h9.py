"""H9 heuristic implementation: Find examples through generalizations.

This heuristic finds examples of a unit by examining examples of its generalizations.
It tests each example against the unit's definition to identify valid examples that 
can be added to the current unit.
"""
from typing import Any, Dict, List
from ..unit import Unit
import logging

logger = logging.getLogger(__name__)

def setup_h9(heuristic) -> None:
    """Configure H9: Find examples through generalizations."""
    # Set properties from original LISP implementation
    heuristic.set_prop('worth', 700)
    heuristic.set_prop('english',
        "IF the current task is to find examples of a unit, and it has a "
        "definition, THEN look over examples of generalizations of the unit, "
        "and see if any of them are valid examples of this as well")
    heuristic.set_prop('abbrev', "Examples can be found among examples of generalizations")
    heuristic.set_prop('arity', 1)
    
    # Set record counts from original
    heuristic.set_prop('then_compute_record', (533544, 7))
    heuristic.set_prop('then_print_to_user_record', (5014, 7))
    heuristic.set_prop('overall_record', (541853, 7))
    heuristic.set_prop('then_compute_failed_record', (912711, 5))

    def check_task(context: Dict[str, Any]) -> bool:
        """Check if we're working on an examples task."""
        task = context.get('task')
        return task and task.get('task_type') == 'find_examples'

    def check_relevance(context: Dict[str, Any]) -> bool:
        """Check if unit has definition and valid generalizations."""
        unit = context.get('unit')
        if not unit:
            return False
            
        # Need definition and generalizations
        if not unit.get_prop('definition'):
            return False
            
        # Check generalizations exist
        gen_names = unit.get_prop('generalizations')
        if not gen_names:
            return False
            
        # Store info for later use
        context['space_to_use'] = gen_names
        context['registry'] = heuristic.unit_registry
        return True

    def print_results(context: Dict[str, Any]) -> bool:
        """Print the examples found."""
        unit = context.get('unit')
        new_values = context.get('task_results', {}).get('new_values', [])
        if not unit or not new_values:
            return False
            
        logger.info(f"\nFound {len(new_values)} valid examples of {unit.name}")
        logger.debug(f"Examples: {new_values}")
        return True

    def compute_action(context: Dict[str, Any]) -> bool:
        """Find examples from generalizations."""
        unit = context.get('unit')
        registry = context.get('registry')
        gen_names = context.get('space_to_use')
        if not all([unit, registry, gen_names]):
            return False
            
        # Get definition function
        definition = unit.get_prop('definition')
        if not callable(definition):
            return False
            
        # Track examples
        new_values = []
        current_examples = unit.get_prop('examples') or []
        non_examples = unit.get_prop('non_examples') or []
        known_examples = set(str(ex) for ex in current_examples + non_examples)
        
        # Check each generalization's examples
        for gen_name in gen_names:
            gen_unit = registry.get_unit(gen_name)
            if not gen_unit:
                continue
                
            examples = gen_unit.get_prop('examples') or []
            for example in examples:
                ex_str = str(example)
                if ex_str not in known_examples:
                    if verify_example(example, definition):
                        new_values.append(example)
                        known_examples.add(ex_str)
        
        # Update results if we found any
        if new_values:
            if 'task_results' not in context:
                context['task_results'] = {}
            context['task_results']['new_values'] = new_values
            
            # Add to unit's examples
            current_examples.extend(new_values)
            unit.set_prop('examples', current_examples)
            
        return bool(new_values)

    def verify_example(example: Any, definition: callable) -> bool:
        """Test if an example satisfies the definition."""
        try:
            return bool(definition(example))
        except:
            return False

    # Configure the heuristic
    heuristic.set_prop('if_working_on_task', check_task)
    heuristic.set_prop('if_truly_relevant', check_relevance)
    heuristic.set_prop('then_print_to_user', print_results)
    heuristic.set_prop('then_compute', compute_action)