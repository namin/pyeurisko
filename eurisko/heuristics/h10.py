"""H10 heuristic implementation: Find examples from operation ranges."""
from typing import Any, Dict, List
import logging

logger = logging.getLogger(__name__)

def setup_h10(heuristic) -> None:
    """Configure H10: Find examples by examining operation ranges."""
    def check_task(context: Dict[str, Any]) -> bool:
        """Check if unit is in range of operations and needs examples."""
        unit = context.get('unit')
        task = context.get('task')
        if not unit or not task:
            return False
            
        if task.get('task_type') != 'find_examples':
            return False
            
        # Check if unit is in range of any operations
        operations = unit.get_prop('is_range_of') or []
        if not operations:
            return False
            
        return True

    def compute_action(context: Dict[str, Any]) -> bool:
        """Find examples by examining operation outputs."""
        unit = context.get('unit')
        if not unit:
            return False
            
        operation_names = unit.get_prop('is_range_of') or []
        current_examples = unit.get_prop('examples') or []
        
        new_examples = []
        sources = []
        
        # Examine each operation's outputs
        for op_name in operation_names:
            operation = heuristic.unit_registry.get_unit(op_name)
            if not operation:
                continue
                
            # Get operation's applications
            applications = operation.get_prop('applications') or []
            found_example = False
            
            for app in applications:
                result = None
                
                # Extract result from application
                if isinstance(app, dict):
                    result = app.get('result')
                elif isinstance(app, (list, tuple)) and len(app) >= 2:
                    result = app[1]
                
                # Skip invalid or duplicate results
                if result is None or result in current_examples or result in new_examples:
                    continue
                    
                new_examples.append(result)
                found_example = True
                
            if found_example:
                sources.append(op_name)
                
        # Update unit and task results if we found anything
        if new_examples:
            # Add new examples to unit
            unit.set_prop('examples', current_examples + new_examples)
            
            # Update task results
            task_results = context.get('task_results', {})
            task_results['new_values'] = new_examples
            task_results['source_operations'] = sources
            task_results['num_found'] = len(new_examples)
            return True
            
        return False

    # Set up heuristic properties
    heuristic.set_prop('if_working_on_task', check_task)
    heuristic.set_prop('then_compute', compute_action)