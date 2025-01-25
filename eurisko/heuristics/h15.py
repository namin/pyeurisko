"""H15 heuristic implementation: Find examples from operation ranges."""
from typing import Any, Dict, List, Optional, Set, Tuple, DefaultDict
from collections import defaultdict
from ..unit import Unit
import logging

logger = logging.getLogger(__name__)

def setup_h15(heuristic) -> None:
    """Configure H15: Find examples from multiple operation ranges."""
    heuristic.set_prop('worth', 700)
    heuristic.set_prop('english',
        "IF the current task is to find examples of a unit, and it is the range of "
        "some operation f, THEN gather together the outputs of the I/O pairs stored "
        "on Applics of f")
    heuristic.set_prop('abbrev', "Find examples from operation outputs") 
    heuristic.set_prop('arity', 1)
    
    heuristic.set_prop('then_compute_record', (5368, 7))
    heuristic.set_prop('then_add_to_agenda_failed_record', (3302, 3))
    heuristic.set_prop('then_add_to_agenda_record', (36, 4))
    heuristic.set_prop('then_print_to_user_record', (1201, 4))
    heuristic.set_prop('overall_record', (7825, 4))

    def check_task(context: Dict[str, Any]) -> bool:
        """Check if we're working on an examples task."""
        task = context.get('task')
        return task and task.get('task_type') == 'find_examples'

    def check_relevance(context: Dict[str, Any]) -> bool:
        """Check if unit is in the range of some operations."""
        unit = context.get('unit')
        if not unit or not unit.get_prop('is_range_of'):
            return False
        context['registry'] = heuristic.unit_registry
        return True

    def build_dependency_info(registry: Any, start_ops: List[str]) -> Tuple[Dict[str, str], Dict[str, List[str]], Set[str]]:
        """Build maps for results and their dependencies."""
        produces = {}  # Map values to operations
        depends_on = defaultdict(list)  # Map operations to dependencies
        all_ops = set()  # Track all relevant operations

        # First collect all results
        for unit in registry.all_units().values():
            apps = unit.get_prop('applications')
            if not apps:
                continue

            for app in apps:
                if isinstance(app, dict):
                    result = app.get('result')
                    if isinstance(result, str):
                        produces[result] = unit.name

        # Then build dependencies
        for unit in registry.all_units().values():
            op_name = unit.name
            apps = unit.get_prop('applications')
            if not apps:
                continue

            deps = []
            for app in apps:
                if isinstance(app, dict):
                    for arg in app.get('args', []):
                        arg_str = str(arg)
                        if arg_str in produces:
                            provider = produces[arg_str]
                            if provider != op_name and provider not in deps:
                                deps.append(provider)
                                all_ops.add(provider)

            if deps or op_name in start_ops:
                depends_on[op_name] = sorted(deps)
                all_ops.add(op_name)

        return produces, dict(depends_on), all_ops

    def find_operation_chain(unit: Unit, registry: Any) -> List[Tuple[str, List[str]]]:
        """Find operations and their dependencies that produce examples."""
        start_ops = unit.get_prop('is_range_of')
        if not start_ops:
            return []

        # Build dependency graph
        produces, depends_on, all_ops = build_dependency_info(registry, start_ops)
        chain = []
        processed = set()

        def process_op(op_name: str) -> None:
            if op_name in processed:
                return

            # Process dependencies first
            deps = depends_on.get(op_name, [])
            for dep in sorted(deps):
                if dep not in processed:
                    process_op(dep)

            # Add operation with its sorted dependencies
            processed.add(op_name)
            chain.append((op_name, depends_on.get(op_name, [])))

        # Process operations in order
        for op in sorted(all_ops):
            if op not in processed:
                process_op(op)

        return list(reversed(chain))

    def compute_action(context: Dict[str, Any]) -> bool:
        """Find examples from operation outputs."""
        unit = context.get('unit')
        registry = context.get('registry')
        if not unit or not registry:
            return False

        # Build operation chain with dependencies
        ops_chain = find_operation_chain(unit, registry)
        if not ops_chain:
            return False

        # Get current examples
        current = unit.get_prop('examples') or []
        current_strs = {str(ex) for ex in current}
        non_examples = unit.get_prop('non_examples') or []
        non_examples_strs = {str(ex) for ex in non_examples}
        seen = current_strs | non_examples_strs
        
        # Find new examples
        new_values = []
        source_operations = []

        # Process operations in chain order
        target_ops = set(unit.get_prop('is_range_of'))
        for op_name, _ in ops_chain:
            if op_name in target_ops:
                op_unit = registry.get_unit(op_name)
                if not op_unit:
                    continue

                apps = op_unit.get_prop('applications') or []
                for app in apps:
                    result = app.get('result')
                    if isinstance(result, str) and result not in seen:
                        new_values.append(result)
                        seen.add(result)
                        if op_name not in source_operations:
                            source_operations.append(op_name)

        if new_values:
            if 'task_results' not in context:
                context['task_results'] = {}
            context['task_results'].update({
                'new_values': new_values,
                'source_operations': source_operations,
                'operation_chain': ops_chain
            })

            unit.set_prop('examples', current + new_values)
        else:
            add_application_tasks(context, [op for op, _ in ops_chain])

        return bool(new_values)

    def add_application_tasks(context: Dict[str, Any], ops: List[str]) -> None:
        """Add tasks to find applications for operations."""
        unit = context.get('unit')
        if not unit:
            return

        new_tasks = []
        for op_name in ops:
            new_tasks.append({
                'priority': 500,
                'unit': op_name,
                'task_type': 'find_applications',
                'reasons': [f"Need applications to find examples of {unit.name}"],
                'supports': {'credit_to': ['h15']}
            })

        if new_tasks:
            if 'task_results' not in context:
                context['task_results'] = {}
            context['task_results'].update({
                'new_tasks': new_tasks,
                'new_tasks_info': f"Finding applications for {len(ops)} operations"
            })

    def print_results(context: Dict[str, Any]) -> bool:
        """Print examples found and their sources."""
        unit = context.get('unit')
        results = context.get('task_results', {})
        new_values = results.get('new_values', [])
        ops = results.get('source_operations', [])
        if not unit or not new_values:
            return False

        logger.info(f"\nFound {len(new_values)} examples for {unit.name} "
                   f"from operations: {', '.join(ops)}")
        logger.debug(f"Examples: {new_values}")
        return True

    # Configure the heuristic
    heuristic.set_prop('if_working_on_task', check_task)
    heuristic.set_prop('if_truly_relevant', check_relevance)
    heuristic.set_prop('then_print_to_user', print_results)
    heuristic.set_prop('then_compute', compute_action)