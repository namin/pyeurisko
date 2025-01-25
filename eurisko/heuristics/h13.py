"""H13 heuristic implementation: Create modification prevention rules.

This heuristic creates prevention rules when concepts are deleted by identifying specific
patterns in how the concept was modified during its creation. It looks for potentially
problematic transformation patterns and creates rules to prevent similar modifications
in the future.
"""
from typing import Any, Dict, Optional, Tuple
from ..unit import Unit
import logging

logger = logging.getLogger(__name__)

def setup_h13(heuristic) -> None:
    """Configure H13: Create modification prevention rules."""
    # Set properties from original LISP implementation
    heuristic.set_prop('worth', 700)
    heuristic.set_prop('english',
        "IF C is about to die, then try to form a new heuristic, one which -- "
        "had it existed earlier -- would have prevented C from ever being defined "
        "in the first place, by preventing the kind of changed object from being changed")
    heuristic.set_prop('abbrev', "Form a rule that would have prevented this pattern")
    heuristic.set_prop('arity', 1)

    def check_potentially_relevant(context: Dict[str, Any]) -> bool:
        """Check if unit is being deleted."""
        unit = context.get('unit')
        deleted_units = context.get('deleted_units', [])
        return unit and unit.name in deleted_units

    def check_relevance(context: Dict[str, Any]) -> bool:
        """Check if we can identify modification patterns."""
        unit = context.get('unit')
        if not unit:
            return False

        # Need creditor information
        creditors = unit.get_prop('creditors')
        if not creditors:
            return False

        # Store registry for later use
        context['registry'] = heuristic.unit_registry
        return True

    def print_results(context: Dict[str, Any]) -> bool:
        """Print explanation of the prevention rule created."""
        unit = context.get('unit')
        task_results = context.get('task_results', {})
        new_units = task_results.get('new_units', [])
        pattern = task_results.get('pattern_detected', {})
        if not unit or not new_units or not pattern:
            return False
            
        logger.info(f"\nJust before destroying {unit.name}, created prevention rule: "
                   f"will no longer change {pattern.get('from')} to {pattern.get('to')} "
                   f"in the {pattern.get('slot')} slot")
        return True

    def compute_action(context: Dict[str, Any]) -> bool:
        """Create prevention rule from modification pattern."""
        unit = context.get('unit')
        registry = context.get('registry')
        if not unit or not registry:
            return False
            
        # Get the creator heuristic's record
        creditor_name = unit.get_prop('creditors')[0]  # Take first creditor
        creditor = registry.get_unit(creditor_name)
        if not creditor:
            return False
            
        # Find the relevant application record
        app_record = find_creation_record(creditor, unit.name)
        if not app_record:
            return False
            
        # Extract modification pattern
        pattern = extract_modification_pattern(app_record)
        if not pattern:
            return False
            
        # Create prevention rule
        rule_unit = create_prevention_rule(unit, pattern, creditor_name)
        if not rule_unit:
            return False
            
        # Register the new rule
        registry.register(rule_unit)
            
        # Add to results
        if 'task_results' not in context:
            context['task_results'] = {}
        context['task_results'].update({
            'new_units': [rule_unit],
            'pattern_detected': {
                'slot': pattern[0],
                'from': pattern[1],
                'to': pattern[2]
            }
        })
        
        return True

    def find_creation_record(creditor: Unit, unit_name: str) -> Optional[Dict[str, Any]]:
        """Find the application record that created the unit."""
        applications = creditor.get_prop('applications') or []
        for app in applications:
            results = app.get('result', [])
            if isinstance(results, list) and unit_name in results:
                return app
        return None

    def extract_modification_pattern(record: Dict[str, Any]) -> Optional[Tuple[str, str, str]]:
        """Extract the modification pattern from the application record."""
        try:
            task_info = record.get('task_info', {})
            if not task_info:
                return None
                
            slot = task_info.get('slot_to_change')
            old_value = task_info.get('old_value')
            new_value = task_info.get('new_value')
            
            if all([slot, old_value, new_value]):
                return (slot, old_value, new_value)
            return None
            
        except Exception as e:
            logger.error(f"Error extracting modification pattern: {e}")
            return None

    def create_prevention_rule(unit: Unit, pattern: Tuple[str, str, str], 
                             creditor: str) -> Optional[Unit]:
        """Create a new prevention rule unit."""
        try:
            # Create rule unit
            rule = Unit(f"prevent-mod-{unit.name}", worth=600)
            
            # Unpack pattern
            slot, pattern_from, pattern_to = pattern
            
            # Set properties
            rule.set_prop('isa', ['prevention-rule'])
            rule.set_prop('slot_to_avoid', slot)
            rule.set_prop('pattern_from', pattern_from)
            rule.set_prop('pattern_to', pattern_to)
            rule.set_prop('learned_from', unit.name)
            rule.set_prop('source_creditor', creditor)
            rule.set_prop('english',
                f"Do not change {pattern_from} to {pattern_to} in the {slot} slot")
            
            return rule
            
        except Exception as e:
            logger.error(f"Error creating prevention rule: {e}")
            return None

    # Configure the heuristic
    heuristic.set_prop('if_potentially_relevant', check_potentially_relevant)
    heuristic.set_prop('if_truly_relevant', check_relevance)
    heuristic.set_prop('then_print_to_user', print_results)
    heuristic.set_prop('then_compute', compute_action)