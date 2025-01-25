"""H15 heuristic implementation: Find examples through multiple operations."""
from typing import Any, Dict, List, Set, Tuple
from ..unit import Unit
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

def setup_h15(heuristic) -> None:
    """Configure H15: Find examples through operation chains."""
    def check_task(context: Dict[str, Any]) -> bool:
        """Check if we're looking for examples with multiple operations."""
        unit = context.get('unit')
        task = context.get('task')
        if not unit or not task:
            return False
            
        if task.get('task_type') != 'find_examples':
            return False
            
        # Check if unit is in range of operations
        operations = unit.get_prop('is_range_of') or []
        if not operations:
            return False
            
        return True

    def build_dependency_map(operations: Dict[str, Unit]) -> Dict[str, Dict[str, List[str]]]:
        """Build a map of value dependencies between operations."""
        dependencies = defaultdict(lambda: defaultdict(list))
        values_to_ops = defaultdict(list)
        
        # First map values to their producing operations
        for op_name, op_unit in operations.items():
            applications = op_unit.get_prop('applications') or []
            for app in applications:
                if isinstance(app, dict):
                    result = app.get('result')
                    if result is not None:
                        values_to_ops[result].append(op_name)
        
        # Then map dependencies between operations
        for op_name, op_unit in operations.items():
            applications = op_unit.get_prop('applications') or []
            for app in applications:
                if not isinstance(app, dict):
                    continue
                    
                # Find all operations that produce this operation's arguments
                args = app.get('args', [])
                result = app.get('result')
                if not args or result is None:
                    continue
                    
                for arg in args:
                    for producer in values_to_ops[arg]:
                        if producer != op_name:  # Avoid self-dependencies
                            dependencies[producer][op_name].append(result)
                            
        return dependencies

    def find_operation_chain(start_op: str, target_value: Any, dependencies: Dict[str, Dict[str, List[str]]], 
                           chain: List[str], visited: Set[str]) -> List[str]:
        """Find a chain of operations leading to target value."""
        logger.debug(f"Finding chain from {start_op} to {target_value}")
        logger.debug(f"Current chain: {chain}")
        logger.debug(f"Dependencies for {start_op}: {dependencies[start_op]}")
        
        if len(chain) > 10:  # Prevent infinite recursion
            return chain
            
        current_chain = chain + [start_op]
        visited.add(start_op)
        
        # Check if this operation leads directly to any consumers
        for consumer_op, results in dependencies[start_op].items():
            if consumer_op in visited:
                continue
                
            if target_value in results:
                return current_chain + [consumer_op]
                
            # Try each operation that consumes our output
            for result in results:
                if consumer_op not in visited:
                    next_chain = find_operation_chain(consumer_op, target_value, dependencies, 
                                                    current_chain, visited.copy())
                    if target_value in next_chain:
                        return next_chain
                        
        return current_chain

    def compute_action(context: Dict[str, Any]) -> bool:
        """Find examples by examining multiple operations."""
        unit = context.get('unit')
        if not unit:
            return False
            
        # Get and validate operations that might produce examples
        operation_names = unit.get_prop('is_range_of') or []
        if not operation_names:
            return False
            
        # Get current examples to avoid duplicates
        current_examples = unit.get_prop('examples') or []
        
        # Track new examples and their sources
        new_examples = []
        operation_chains = {}
        example_sources = defaultdict(list)
        
        # Collect all available operations
        operations = {}
        for op_name in operation_names:
            op_unit = heuristic.unit_registry.get_unit(op_name)
            if not op_unit:
                continue
            operations[op_name] = op_unit
            
        # Build dependency map between operations
        logger.debug("Building dependency map...")
        dependencies = build_dependency_map(operations)
        logger.debug(f"Dependency map: {dependencies}")
        
        # First collect all potential examples from all operations
        all_results = set()
        for op_unit in operations.values():
            apps = op_unit.get_prop('applications') or []
            for app in apps:
                if isinstance(app, dict):
                    result = app.get('result')
                    if result is not None:
                        all_results.add(result)
        
        # For each potential example, try to find operation chains that produce it
        for op_name, op_unit in operations.items():
            apps = op_unit.get_prop('applications') or []
            
            for app in apps:
                if not isinstance(app, dict):
                    continue
                    
                result = app.get('result')
                if result is None or result in current_examples or result in new_examples:
                    continue
                    
                # Add this example and its source
                new_examples.append(result)
                example_sources[result].append(op_name)
                
                # Try to find operation chain leading to this result
                chain = find_operation_chain(op_name, result, dependencies, [], set())
                if len(chain) > 1:
                    operation_chains[result] = chain
        
        if new_examples:
            # Update unit's examples
            unit.set_prop('examples', current_examples + new_examples)
            
            # Update task results
            task_results = context.get('task_results', {})
            task_results['new_values'] = new_examples
            
            # Record all source operations
            source_ops = set()
            for ops in example_sources.values():
                source_ops.update(ops)
            task_results['source_operations'] = list(source_ops)
            
            # Record operation chains if found
            if operation_chains:
                longest_chain = max(operation_chains.values(), key=len)
                task_results['operation_chain'] = longest_chain
            
            return True
            
        # If no examples found, schedule tasks to find more applications
        else:
            task_results = context.get('task_results', {})
            new_tasks = []
            
            # Schedule application-finding tasks
            for op_name in operation_names:
                new_tasks.append({
                    'task_type': 'find_applications',
                    'target_unit': op_name,
                    'priority': 500,
                    'reason': f"Need applications of {op_name} to find examples of {unit.name}"
                })
                
            # Schedule a retry with lower priority
            new_tasks.append({
                'task_type': 'find_examples',
                'target_unit': unit.name,
                'priority': 300,
                'reason': f"Retry finding examples after gathering more applications"
            })
            
            if new_tasks:
                task_results['new_tasks'] = new_tasks
                
            return False

    # Set up heuristic properties
    heuristic.set_prop('if_working_on_task', check_task)
    heuristic.set_prop('then_compute', compute_action)