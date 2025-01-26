"""H14 heuristic implementation: Create type-based prevention rules."""
from typing import Any, Dict, List, Optional
import logging
import inspect

logger = logging.getLogger(__name__)

def setup_h14(heuristic) -> None:
    """Configure H14: Create type-based prevention rules.
    
    This heuristic examines failing concepts to understand type changes that
    led to failure. It creates prevention rules that block problematic type
    transitions (e.g., simple to complex) while still allowing safe changes.
    """
    heuristic.set_prop('worth', 700)
    heuristic.set_prop('english',
        "IF C is about to die, THEN try to form prevention rules based on "
        "problematic type transformations that led to failure.")
    heuristic.set_prop('abbrev', "Form type-based prevention rules")

    def analyze_type_changes(old_value: Any, new_value: Any) -> Dict[str, Any]:
        """Analyze type changes between values in detail.
        
        Examines:
        - Basic type transitions (e.g., int to function)
        - Structural changes (atomic to compound)
        - Complexity increases
        """
        def get_type_category(value: Any) -> str:
            """Determine high-level type category."""
            if callable(value):
                return 'function'
            elif isinstance(value, (list, tuple, set)):
                return 'sequence'
            elif isinstance(value, dict):
                return 'mapping'
            elif isinstance(value, (int, float)):
                return 'numeric'
            elif isinstance(value, str):
                return 'text'
            else:
                return type(value).__name__

        def measure_complexity(value: Any) -> int:
            """Estimate structural complexity of a value."""
            if callable(value):
                try:
                    source = inspect.getsource(value)
                    return len(source.split('\n'))
                except:
                    return 5  # Default for functions
            elif isinstance(value, (list, tuple, set)):
                return sum(measure_complexity(x) for x in value) + 1
            elif isinstance(value, dict):
                return sum(
                    measure_complexity(k) + measure_complexity(v)
                    for k, v in value.items()
                ) + 1
            elif isinstance(value, str):
                return len(value)
            else:
                return 1

        old_type = type(old_value).__name__
        new_type = type(new_value).__name__
        old_category = get_type_category(old_value)
        new_category = get_type_category(new_value)
        
        old_complexity = measure_complexity(old_value)
        new_complexity = measure_complexity(new_value)
        
        return {
            'from_type': old_type,
            'to_type': new_type,
            'from_category': old_category,
            'to_category': new_category,
            'type_changed': old_type != new_type,
            'category_changed': old_category != new_category,
            'complexity_increased': new_complexity > old_complexity,
            'complexity_ratio': new_complexity / old_complexity if old_complexity > 0 else float('inf')
        }

    def check_unit_deletion(context: Dict[str, Any]) -> bool:
        """Check if unit is being deleted."""
        unit = context.get('unit')
        deleted_units = context.get('deleted_units', [])
        
        if not unit or unit.name not in deleted_units:
            return False
            
        # Need to know what created this unit
        creditors = unit.get_prop('creditors', [])
        if not creditors:
            return False
            
        # Store creator info for later
        creator = creditors[0]
        context['creator'] = creator
        return True

    def get_creation_task(unit: Any, creator: str) -> Optional[Dict[str, Any]]:
        """Find the task that created this unit."""
        # First try unit's own applications
        unit_apps = unit.get_prop('applications') or []
        
        # Then check creator's applications
        creator_unit = unit.get_prop('creditors_applications') or []
        
        # Combine both sources
        all_apps = unit_apps + creator_unit
        
        for app in all_apps:
            task_info = app.get('task_info', {})
            old_value = task_info.get('old_value')
            new_value = task_info.get('new_value')
            
            if old_value is not None and new_value is not None:
                type_analysis = analyze_type_changes(old_value, new_value)
                if type_analysis['type_changed'] or type_analysis['complexity_increased']:
                    task_info['type_analysis'] = type_analysis
                    return app
                    
        return None

    def compute_action(context: Dict[str, Any]) -> bool:
        """Create type-based prevention rules."""
        unit = context.get('unit')
        creator = context.get('creator')
        if not unit or not creator:
            return False

        # Get information about how unit was created
        creation_task = get_creation_task(unit, creator)
        if not creation_task:
            return False

        task_info = creation_task.get('task_info', {})
        changed_slot = task_info.get('slot_to_change')
        type_analysis = task_info.get('type_analysis')
        
        if not all([changed_slot, type_analysis]):
            return False

        # Create prevention rules
        new_rules = []
        
        # Rule for type changes if relevant
        if type_analysis['type_changed']:
            type_rule = {
                'name': (
                    f"prevent_{type_analysis['from_type']}_to_"
                    f"{type_analysis['to_type']}_changes"
                ),
                'type': 'type-prevention-rule',
                'english': (
                    f"Prevent changes in {changed_slot} slot that convert "
                    f"{type_analysis['from_type']} values to "
                    f"{type_analysis['to_type']} values"
                ),
                'slot_to_avoid': changed_slot,
                'from_type': type_analysis['from_type'],
                'to_type': type_analysis['to_type'],
                'learned_from': unit.name,
                'source_creditor': creator
            }
            new_rules.append(type_rule)

        # Rule for complexity increases if relevant
        if type_analysis['complexity_increased']:
            complexity_rule = {
                'name': f"prevent_complexity_increase_in_{changed_slot}",
                'type': 'complexity-prevention-rule',
                'english': (
                    f"Prevent changes to {changed_slot} slot that significantly "
                    f"increase structural complexity"
                ),
                'slot_to_avoid': changed_slot,
                'check': 'complexity_increase',
                'learned_from': unit.name,
                'source_creditor': creator,
                'complexity_threshold': type_analysis['complexity_ratio']
            }
            new_rules.append(complexity_rule)

        if new_rules:
            context['task_results'] = context.get('task_results', {})
            context['task_results'].update({
                'new_units': new_rules,
                'type_analysis': type_analysis
            })
            return True

        return False

    def print_to_user(context: Dict[str, Any]) -> bool:
        """Report on prevention rules created."""
        unit = context.get('unit')
        task_results = context.get('task_results', {})
        
        if not unit or not task_results:
            return False
            
        new_units = task_results.get('new_units', [])
        if not new_units:
            return False

        type_analysis = task_results.get('type_analysis', {})
        
        logger.info(
            f"\nCreated prevention rules from {unit.name} failure:")
            
        for rule in new_units:
            if rule['type'] == 'type-prevention-rule':
                logger.info(
                    f"- Type rule: prevent {rule['from_type']} to "
                    f"{rule['to_type']} conversions in {rule['slot_to_avoid']}"
                )
            else:
                logger.info(
                    f"- Complexity rule: prevent large increases "
                    f"(>{type_analysis['complexity_ratio']:.1f}x) in "
                    f"{rule['slot_to_avoid']}"
                )
        return True

    # Configure heuristic slots
    heuristic.set_prop('if_potentially_relevant', check_unit_deletion)
    heuristic.set_prop('then_compute', compute_action)
    heuristic.set_prop('then_print_to_user', print_to_user)