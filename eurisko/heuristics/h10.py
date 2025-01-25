"""H10 heuristic implementation: Find examples from operation ranges.

This heuristic finds examples of a unit by examining the outputs of operations for which
this unit represents their range. When a unit is defined as being in the range of some
operation, we can find examples by collecting the results of that operation's applications.
"""
from typing import Any, Dict, List
from ..unit import Unit
import logging

logger = logging.getLogger(__name__)

def setup_h10(heuristic) -> None:
    """Configure H10: Find examples from operation ranges."""
    # Set properties from original LISP implementation
    heuristic.set_prop('worth', 700)
    heuristic.set_prop('english',
        "IF the current task is to find examples of a unit, and it is the range "
        "of some operation f, THEN gather together the outputs of the I/O pairs "
        "stored on Applics of f")
    heuristic.set_prop('abbrev', "If C is Range(f), then Exs(C) from Applics(f)")
    heuristic.set_prop('arity', 1)
    
    # Set record counts from original
    heuristic.set_prop('then_compute_record', (12618, 7))
    heuristic.set_prop('then_add_to_agenda_failed_record', (1307, 3))
    heuristic.set_prop('then_add_to_agenda_record', (37, 4))
    heuristic.set_prop('then_print_to_user_record', (2101, 4))
    heuristic.set_prop('overall_record', (16037, 4))

    def check_task(context: Dict[str, Any]) -> bool:
        """Check if we're working on an examples task."""
        task = context.get('task')
        return task and task.get('task_type') == 'find_examples'

    def check_relevance(context: Dict[str, Any]) -> bool:
        """Check if unit is in the range of some operation."""
        unit = context.get('unit')
        if not unit:
            return False
            
        # Check for range operations
        op_names = unit.get_prop('is_range_of')
        if not op_names:
            return False
            
        # Store registry and operation names for later
        context['registry'] = heuristic.unit_registry
        context['ops_to_use'] = op_names
        return True

    def print_results(context: Dict[str, Any]) -> bool:
        """Print examples found from operation outputs."""
        unit = context.get('unit')
        new_values = context.get('task_results', {}).get('new_values', [])
        if not unit or not new_values:
            return False
            
        logger.info(f"\nFound {len(new_values)} examples for {unit.name}")
        logger.debug(f"Examples: {new_values}")
        return True

    def compute_action(context: Dict[str, Any]) -> bool:
        """Find examples from operation outputs."""
        unit = context.get('unit')
        registry = context.get('registry')
        op_names = context.get('ops_to_use')
        if not all([unit, registry, op_names]):
            return False
            
        # Track examples
        new_values = []
        current_examples = unit.get_prop('examples') or []
        non_examples = unit.get_prop('non_examples') or []
        known_examples = set(str(ex) for ex in current_examples + non_examples)
        
        # Check applications of each operation
        space_to_use = []
        for op_name in op_names:
            op_unit = registry.get_unit(op_name)
            if not op_unit:
                continue
                
            apps = op_unit.get_prop('applications') or []
            space_to_use.extend(apps)
            
        if not space_to_use:
            # Add task to find applications
            add_application_tasks(context)
            return False
            
        # Extract results from applications
        for app in space_to_use:
            result = app.get('result')
            if result is not None:
                result_str = str(result)
                if result_str not in known_examples:
                    new_values.append(result)
                    known_examples.add(result_str)
        
        # Update results if we found any
        if new_values:
            if 'task_results' not in context:
                context['task_results'] = {}
            context['task_results']['new_values'] = new_values
            
            # Add to unit's examples
            current_examples.extend(new_values)
            unit.set_prop('examples', current_examples)
            
        return bool(new_values)

    def add_application_tasks(context: Dict[str, Any]) -> None:
        """Add tasks to find applications for operations."""
        unit = context.get('unit')
        op_names = context.get('ops_to_use')
        task = context.get('task', {})
        
        # Create tasks to find applications
        for op_name in op_names:
            new_task = {
                'priority': task.get('priority', 500) - 1,
                'unit': op_name,
                'task_type': 'find_applications',
                'reasons': [f"Need applications to find examples of {unit.name}"],
                'supports': {'credit_to': ['h10']}
            }
            
            if 'task_results' not in context:
                context['task_results'] = {}
            task_results = context['task_results']
            
            if 'new_tasks' not in task_results:
                task_results['new_tasks'] = []
            task_results['new_tasks'].append(new_task)
            
            logger.info(f"Adding task to find applications for {op_name}")

    # Configure the heuristic
    heuristic.set_prop('if_working_on_task', check_task)
    heuristic.set_prop('if_truly_relevant', check_relevance)
    heuristic.set_prop('then_print_to_user', print_results)
    heuristic.set_prop('then_compute', compute_action)