"""H20 heuristic implementation: Cross-operation pattern detection."""
from typing import Any, Dict, List, Set
from ..unit import Unit
import logging

logger = logging.getLogger(__name__)

def setup_h20(heuristic) -> None:
    """Configure H20: Detect patterns across operations.
    
    This heuristic examines operations that can apply to the same inputs,
    running them and looking for potential relationships or patterns in their
    behavior.
    """
    heuristic.set_prop('worth', 600)
    heuristic.set_prop('english',
        "IF an operation F can apply to any of the domain items of another operation, "
        "THEN apply it and look for patterns between their behaviors.")
    heuristic.set_prop('abbrev', "Run F on args used for other ops")
    
    # Initialize record keeping
    heuristic.set_prop('then_compute_failed_record', (5828, 14))
    heuristic.set_prop('then_compute_record', (-546691, 16))
    heuristic.set_prop('then_add_to_agenda_record', (5355, 16))
    heuristic.set_prop('overall_record', (-528368, 16))
    heuristic.set_prop('arity', 1)

    def check_potential_relevance(context: Dict[str, Any]) -> bool:
        """Check if operation has algorithm and can be meaningfully compared."""
        unit = context.get('unit')
        if not unit:
            return False
            
        # Need an executable algorithm
        algorithm = unit.get_prop('alg')
        if not algorithm:
            return False
            
        context['algorithm'] = algorithm
        return True

    def find_comparable_operations(unit: Unit, system: Any) -> List[Unit]:
        """Find other operations with same arity that have applications."""
        comparable = []
        unit_arity = unit.get_prop('arity')
        
        # Get sibling operations
        siblings = unit.get_prop('sibs', [])
        for sib_name in siblings:
            sib = system.unit_registry.get_unit(sib_name)
            if not sib or sib.name == unit.name:
                continue
                
            # Check arity matches
            if sib.get_prop('arity') != unit_arity:
                continue
                
            # Check has applications
            if len(sib.get_prop('applications', [])) > 3:
                comparable.append(sib)
                
        return comparable

    def check_relevance(context: Dict[str, Any]) -> bool:
        """Find operations to compare against."""
        unit = context.get('unit')
        system = context.get('system')
        
        if not unit or not system:
            return False
            
        # Find comparable operations
        comparable_ops = find_comparable_operations(unit, system)
        if not comparable_ops:
            return False
            
        # Verify we can test domain compatibility
        domain_tests = []
        for domain in unit.get_prop('domain', []):
            test = domain.get('test')
            if not test:
                return False
            domain_tests.append(test)
            
        context['comparable_ops'] = comparable_ops
        context['domain_tests'] = domain_tests
        return True

    def print_to_user(context: Dict[str, Any]) -> bool:
        """Report on operations compared and patterns found."""
        unit = context.get('unit')
        added_ops = context.get('added_ops', [])
        
        if not unit or not added_ops:
            return False
            
        logger.info(
            f"\nRan {unit.name}'s algorithm on data from: "
            f"{', '.join(op.name for op in added_ops)}\n"
            f"Will examine for potential connections between these operations."
        )
        return True

    def compute_action(context: Dict[str, Any]) -> bool:
        """Apply operation to inputs from other operations."""
        unit = context.get('unit')
        comparable_ops = context.get('comparable_ops', [])
        algorithm = context.get('algorithm')
        domain_tests = context.get('domain_tests', [])
        
        if not all([unit, comparable_ops, algorithm, domain_tests]):
            return False
            
        added_ops = []
        for other_op in comparable_ops:
            for application in other_op.get_prop('applications', []):
                args = application.get('args', [])
                
                # Skip if we already know this application
                if unit.has_application(args):
                    continue
                    
                # Verify args pass domain tests
                if not all(test(arg) for test, arg in zip(domain_tests, args)):
                    continue
                    
                # Apply algorithm
                try:
                    result = algorithm(*args)
                    unit.add_application(args, result)
                    if other_op not in added_ops:
                        added_ops.append(other_op)
                except Exception as e:
                    logger.debug(f"Failed to apply {unit.name} to {args}: {e}")
                    
        context['added_ops'] = added_ops
        return bool(added_ops)

    def add_to_agenda(context: Dict[str, Any]) -> bool:
        """Add tasks to investigate patterns between operations."""
        unit = context.get('unit')
        system = context.get('system')
        added_ops = context.get('added_ops', [])
        
        if not all([unit, system, added_ops]):
            return False
            
        for other_op in added_ops:
            task = {
                'priority': int((
                    unit.get_prop('worth', 500) + 
                    other_op.get_prop('worth', 500)
                ) / 2),
                'unit': unit,
                'slot': 'conjectures',
                'reasons': [
                    f"{unit.name} has now been run on the same data as "
                    f"{other_op.name} - investigate potential patterns"
                ],
                'supplemental': {
                    'credit_to': ['h20'],
                    'involved_units': [other_op.name]
                }
            }
            system.task_manager.add_task(task)
            
        system.add_task_result(
            'new_tasks',
            f"{len(added_ops)} operations will be examined for connections"
        )
        return True

    # Configure heuristic slots
    heuristic.set_prop('if_potentially_relevant', check_potential_relevance)
    heuristic.set_prop('if_truly_relevant', check_relevance)
    heuristic.set_prop('then_compute', compute_action)
    heuristic.set_prop('then_print_to_user', print_to_user)
    heuristic.set_prop('then_add_to_agenda', add_to_agenda)
