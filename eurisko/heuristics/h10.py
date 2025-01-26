"""H10 heuristic implementation: Find examples from operation outputs."""
from typing import Any, Dict, List
import logging

logger = logging.getLogger(__name__)

def setup_h10(heuristic) -> None:
    """Configure H10: Find examples by examining operation outputs.
    
    This heuristic examines operations for which the current unit is in their
    range, collecting their outputs as potential examples. This enables example
    discovery through functional relationships.
    """
    heuristic.set_prop('worth', 700)
    heuristic.set_prop('english',
        "IF the current task is to find examples of a unit, and it is the "
        "range of some operation f, THEN gather together the outputs of the "
        "I/O pairs stored on applications of f.")
    heuristic.set_prop('abbrev', "Find examples from operation outputs")

    def check_task_relevance(context: Dict[str, Any]) -> bool:
        """Verify task is for finding examples."""
        task = context.get('task')
        unit = context.get('unit')
        
        if not task or not unit:
            return False
            
        if task.get('task_type') != 'find_examples':
            return False
            
        # Need operations that produce this type
        operations = unit.get_prop('is_range_of', [])
        if not operations:
            return False
            
        context['source_ops'] = operations
        return True

    def get_examples_from_operations(
        operations: List[str],
        registry: Any
    ) -> List[Dict[str, Any]]:
        """Get outputs from operations that produce this type."""
        examples = []
        
        for op_name in operations:
            op = registry.unit_registry.get_unit(op_name)
            if not op:
                continue
                
            applications = op.get_prop('applications', [])
            for app in applications:
                result = app.get('result')
                if result is not None:
                    examples.append({
                        'value': result,
                        'source': op_name,
                        'from_application': app
                    })
                    
        return examples

    def compute_action(context: Dict[str, Any]) -> bool:
        """Find examples from operation outputs."""
        unit = context.get('unit')
        source_ops = context.get('source_ops', [])
        registry = context.get('registry')
        
        if not all([unit, source_ops, registry]):
            return False

        # Get examples from operations
        examples = get_examples_from_operations(source_ops, registry)
        if not examples:
            return False

        # Track new examples
        current_examples = set(unit.get_prop('examples', []))
        new_examples = []

        # Collect unique examples
        for example in examples:
            value = example['value']
            if value not in current_examples:
                new_examples.append(example)
                current_examples.add(value)

        if new_examples:
            context['task_results'] = context.get('task_results', {})
            context['task_results']['new_values'] = [
                example['value'] for example in new_examples
            ]
            return True

        return False

    def print_to_user(context: Dict[str, Any]) -> bool:
        """Report on examples found."""
        unit = context.get('unit')
        task_results = context.get('task_results', {})
        
        if not unit or not task_results:
            return False
        
        new_examples = task_results.get('new_values', [])
        if not new_examples:
            return False

        logger.info(
            f"\nFound {len(new_examples)} examples for {unit.name} from "
            f"operation outputs"
        )
        
        return True

    # Configure heuristic slots
    heuristic.set_prop('if_potentially_relevant', check_task_relevance)
    heuristic.set_prop('then_compute', compute_action)
    heuristic.set_prop('then_print_to_user', print_to_user)