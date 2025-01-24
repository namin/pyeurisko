"""H10 heuristic implementation: Find examples from operation ranges."""
from typing import Any, Dict, List
from ..unit import Unit
import random
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
            
        # Select one operation randomly to examine
        selected_op = random.choice(operations)
        context['selected_operation'] = selected_op
        return True

    def compute_action(context: Dict[str, Any]) -> bool:
        """Find examples by examining operation outputs."""
        unit = context.get('unit')
        if not unit:
            return False
            
        operation_name = context.get('selected_operation')
        if not operation_name:
            return False
            
        operation = heuristic.unit_registry.get_unit(operation_name)
        if not operation:
            return False
            
        # Get current examples and non-examples
        current_examples = unit.get_prop('examples') or []
        current_non_examples = unit.get_prop('non_examples') or []
        
        # Examine applications of the operation
        applications = operation.get_prop('applications') or []
        new_examples = []
        
        for application in applications:
            # Extract output from application
            output = None
            if isinstance(application, dict):
                output = application.get('result')
            elif isinstance(application, (list, tuple)) and len(application) >= 2:
                output = application[1]
                
            if output is None:
                continue
                
            # Check if output is already known
            if output in current_examples or output in current_non_examples:
                continue
                
            new_examples.append(output)
            
        if new_examples:
            # Update examples
            unit.set_prop('examples', current_examples + new_examples)
            
            # Update task results
            task_results = context.get('task_results', {})
            task_results['new_values'] = new_examples
            task_results['source_operation'] = operation_name
            return True
            
        # If no examples found, create task to find applications for operation
        else:
            task = context.get('task', {})
            new_task = {
                'task_type': 'find_applications',
                'target_unit': operation_name,
                'priority': task.get('priority', 500) - 100,
                'reason': f"Need applications of {operation_name} to find examples of {unit.name}"
            }
            task_results = context.get('task_results', {})
            new_tasks = task_results.get('new_tasks', [])
            new_tasks.append(new_task)
            task_results['new_tasks'] = new_tasks
            
            # Also reschedule current task with lower priority
            task['priority'] = task.get('priority', 500) // 2
            new_tasks.append(task)
            
            return False

    # Set up heuristic properties
    heuristic.set_prop('if_working_on_task', check_task)
    heuristic.set_prop('then_compute', compute_action)