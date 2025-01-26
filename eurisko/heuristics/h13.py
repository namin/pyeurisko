"""H13 heuristic implementation: Create modification prevention rules."""
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

def setup_h13(heuristic) -> None:
    """Configure H13: Create specific prevention rules from modifications.
    
    This heuristic examines failing concepts to understand the specific
    modifications that led to their failure. It then creates targeted
    prevention rules that block similar changes, helping the system avoid
    similar mistakes while still allowing other potentially useful changes.
    """
    heuristic.set_prop('worth', 700)
    heuristic.set_prop('english',
        "IF C is about to die, THEN try to form prevention rules based on "
        "the specific modifications that led to C's failure, preventing "
        "similar problematic changes.")
    heuristic.set_prop('abbrev', "Form specific modification prevention rules")

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

    def analyze_modification(
        old_value: Any,
        new_value: Any
    ) -> Optional[Dict[str, Any]]:
        """Analyze how a value was modified.
        
        Returns details about the modification including:
        - Type changes
        - Value pattern changes
        - Complexity changes
        """
        if old_value is None or new_value is None:
            return None
            
        pattern = {
            'from': str(old_value),
            'to': str(new_value),
            'from_type': type(old_value).__name__,
            'to_type': type(new_value).__name__,
            'type_changed': type(old_value) != type(new_value),
            'complexity_increased': len(str(new_value)) > len(str(old_value))
        }
        
        return pattern

    def get_creation_task(unit: Any, creator: str) -> Optional[Dict[str, Any]]:
        """Find the task that created this unit."""
        creator_apps = unit.get_prop('applications') or []
        
        for app in creator_apps:
            if app.get('task_info'):
                task_info = app['task_info']
                if 'old_value' in task_info and 'new_value' in task_info:
                    pattern = analyze_modification(
                        task_info['old_value'],
                        task_info['new_value']
                    )
                    if pattern:
                        task_info['pattern'] = pattern
                        return app
                    
        return None

    def compute_action(context: Dict[str, Any]) -> bool:
        """Create prevention rules based on modification analysis."""
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
        pattern = task_info.get('pattern')
        
        if not all([changed_slot, pattern]):
            return False

        # Create prevention rule targeting this pattern
        rule_name = (
            f"prevent_{pattern['from_type']}_to_{pattern['to_type']}_"
            f"in_{changed_slot}"
        )
        
        prevention_rule = {
            'name': rule_name,
            'isa': ['prevention-rule'],
            'english': (
                f"Prevent changes to {changed_slot} slot that convert "
                f"{pattern['from_type']} values to {pattern['to_type']} values"
            ),
            'slot_to_avoid': changed_slot,
            'pattern_from': pattern['from'],
            'pattern_to': pattern['to'],
            'learned_from': unit.name,
            'source_creditor': creator
        }

        # Record pattern information
        context['task_results'] = context.get('task_results', {})
        context['task_results'].update({
            'new_units': [prevention_rule],
            'pattern_detected': {
                'slot': changed_slot,
                'from': pattern['from'],
                'to': pattern['to']
            }
        })
        return True

    def print_to_user(context: Dict[str, Any]) -> bool:
        """Report on prevention rule creation."""
        unit = context.get('unit')
        task_results = context.get('task_results', {})
        
        if not unit or not task_results:
            return False
            
        new_units = task_results.get('new_units', [])
        if not new_units:
            return False

        pattern = task_results.get('pattern_detected', {})
        logger.info(
            f"\nLearned specific prevention rule from {unit.name}:\n"
            f"Will prevent changes in {pattern.get('slot', 'unknown')} slot "
            f"from '{pattern.get('from', 'unknown')}' to "
            f"'{pattern.get('to', 'unknown')}'"
        )
        return True

    # Configure heuristic slots
    heuristic.set_prop('if_potentially_relevant', check_unit_deletion)
    heuristic.set_prop('then_compute', compute_action)
    heuristic.set_prop('then_print_to_user', print_to_user)