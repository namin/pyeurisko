"""H12 heuristic implementation: Create prevention rules from failed concepts.

This heuristic creates prevention rules when concepts are about to be deleted. It examines
the circumstances under which the failing concept was created and generates rules that 
would have prevented similar unproductive concepts from being created.
"""
from typing import Any, Dict, Optional
from ..unit import Unit
import logging

logger = logging.getLogger(__name__)

def setup_h12(heuristic) -> None:
    """Configure H12: Create prevention rules from failed concepts."""
    # Set properties from original LISP implementation
    heuristic.set_prop('worth', 700)
    heuristic.set_prop('english',
        "IF C is about to die, then try to form a new heuristic, one which -- "
        "had it existed earlier -- would have prevented C from ever being defined "
        "in the first place")
    heuristic.set_prop('abbrev', "Form a rule that would have prevented this mistake")
    heuristic.set_prop('arity', 1)

    def check_potentially_relevant(context: Dict[str, Any]) -> bool:
        """Check if unit is being deleted."""
        unit = context.get('unit')
        deleted_units = context.get('deleted_units', [])
        return unit and unit.name in deleted_units

    def check_relevance(context: Dict[str, Any]) -> bool:
        """Check if we can identify what led to unit's creation."""
        unit = context.get('unit')
        if not unit:
            return False

        # Need to know what created this unit
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
        if not unit or not new_units:
            return False
            
        rule = new_units[0]
        slot = rule.get_prop('slot_to_avoid')
        logger.info(f"\nJust before destroying {unit.name}, created prevention rule: "
                   f"will no longer alter the {slot} slot when it leads to errors")
        return True

    def compute_action(context: Dict[str, Any]) -> bool:
        """Create prevention rule from failed unit."""
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
            
        # Extract slot that was modified
        task_info = app_record.get('task_info', {})
        slot_to_avoid = task_info.get('slot_to_change')
        if not slot_to_avoid:
            return False
            
        # Create prevention rule
        rule_unit = create_prevention_rule(unit, slot_to_avoid, creditor_name)
        if not rule_unit:
            return False
            
        # Register the new rule
        registry.register(rule_unit)
            
        # Add to results
        if 'task_results' not in context:
            context['task_results'] = {}
        context['task_results']['new_units'] = [rule_unit]
        
        return True

    def find_creation_record(creditor: Unit, unit_name: str) -> Optional[Dict[str, Any]]:
        """Find the application record that created the unit."""
        applications = creditor.get_prop('applications') or []
        for app in applications:
            results = app.get('result', [])
            if isinstance(results, list) and unit_name in results:
                return app
        return None

    def create_prevention_rule(unit: Unit, slot: str, creditor: str) -> Optional[Unit]:
        """Create a new prevention rule unit."""
        try:
            # Create rule unit
            rule = Unit(f"prevent-{unit.name}", worth=600)
            
            # Set properties
            rule.set_prop('isa', ['prevention-rule'])
            rule.set_prop('slot_to_avoid', slot)
            rule.set_prop('learned_from', unit.name)
            rule.set_prop('english', 
                f"Do not modify the {slot} slot in the way that led to {unit.name}")
            rule.set_prop('source_creditor', creditor)
            
            return rule
            
        except Exception as e:
            logger.error(f"Error creating prevention rule: {e}")
            return None

    # Configure the heuristic
    heuristic.set_prop('if_potentially_relevant', check_potentially_relevant)
    heuristic.set_prop('if_truly_relevant', check_relevance)
    heuristic.set_prop('then_print_to_user', print_results)
    heuristic.set_prop('then_compute', compute_action)