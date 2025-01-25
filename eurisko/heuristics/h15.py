"""H15 heuristic implementation: Find examples through multiple operations."""
from typing import Any, Dict, List, Set, Tuple
from ..unit import Unit
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def setup_h15(heuristic) -> None:
    """Configure H15: Find examples through operation chains."""
    def check_task(context: Dict[str, Any]) -> bool:
        """Check if we're looking for examples with multiple operations."""
        unit = context.get('unit')
        task = context.get('task', {})
        return unit and task.get('task_type') == 'find_examples' and bool(unit.get_prop('is_range_of'))

    def build_dependency_graph() -> Dict[str, List[str]]:
        """Build operation dependency graph."""
        depends_on = defaultdict(list)
        op_results = {}  # Track operation results

        # First pass: collect all operation results
        for unit in heuristic.unit_registry.all_units().values():
            applications = unit.get_prop('applications') or []
            for app in applications:
                if isinstance(app, dict) and 'result' in app:
                    result = app.get('result')
                    if isinstance(result, (str, int, float)):  # Only use hashable results
                        op_results[result] = unit.name

        # Second pass: build dependencies
        for unit in heuristic.unit_registry.all_units().values():
            applications = unit.get_prop('applications') or []
            for app in applications:
                if isinstance(app, dict):
                    args = app.get('args', [])
                    for arg in args:
                        if isinstance(arg, (str, int, float)) and arg in op_results:  # Only use hashable args
                            if op_results[arg] != unit.name:
                                depends_on[unit.name].append(op_results[arg])

        return depends_on

    def find_operation_chain(op_name: str, dependencies: Dict[str, List[str]], visited: Set[str] = None) -> List[str]:
        """Find all operations in the chain."""
        if visited is None:
            visited = set()
        if op_name in visited:
            return []
        visited.add(op_name)
        
        chain = [op_name]
        for dep in dependencies.get(op_name, []):
            subchain = find_operation_chain(dep, dependencies, visited)
            if subchain:
                chain = subchain + chain
        return chain

    def compute_action(context: Dict[str, Any]) -> bool:
        """Find examples by examining multiple operations."""
        unit = context.get('unit')
        if not unit:
            return False
            
        operation_names = unit.get_prop('is_range_of') or []
        if not operation_names:
            return False

        # Initialize results
        task_results = {}
        current_examples = unit.get_prop('examples') or []
        new_examples = []
        example_sources = set()

        # First pass: collect examples
        for op_name in operation_names:
            op_unit = heuristic.unit_registry.get_unit(op_name)
            if not op_unit:
                continue

            applications = op_unit.get_prop('applications') or []
            for app in applications:
                if isinstance(app, dict) and 'result' in app:
                    result = app['result']
                    if result not in current_examples and result not in new_examples:
                        new_examples.append(result)
                        example_sources.add(op_name)

        if new_examples:
            # Update unit's examples
            unit.set_prop('examples', current_examples + new_examples)

            # Find operation chains
            dependencies = build_dependency_graph()
            longest_chain = []
            for op_name in operation_names:
                chain = find_operation_chain(op_name, dependencies)
                if len(chain) > len(longest_chain):
                    longest_chain = chain

            # Update task results
            task_results['new_values'] = new_examples
            task_results['source_operations'] = list(example_sources)
            if len(longest_chain) > 1:
                task_results['operation_chain'] = longest_chain

            context['task_results'] = task_results
            return True

        return False

    # Set up heuristic properties
    heuristic.set_prop('if_working_on_task', check_task)
    heuristic.set_prop('then_compute', compute_action)