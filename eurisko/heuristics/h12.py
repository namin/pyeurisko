"""H12 heuristic implementation: Create prevention rules from failed concepts."""
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

def setup_h12(heuristic) -> None:
    """Configure H12: Learn from concept deletion.
    
    This heuristic examines concepts being deleted due to failure and creates
    prevention rules that would have blocked their creation, helping the system
    avoid similar mistakes in the future.
    """
    heuristic.set_prop('worth', 700)
    heuristic.set_prop('english',
        "IF C is about to die, THEN try to form a new heuristic that -- had "
        "it existed earlier -- would have prevented C from ever being defined.")
    heuristic.set_prop('abbrev', "Form prevention rule from failed concept")

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
        creator = creditors[0]  # Main creator
        context['creator'] = creator
        return True

    def get_creation_task(unit: Any, creator: str) -> Optional[Dict[str, Any]]:
        """Find the task that created this unit."""
        # Check creator's applications for task that made this unit
        creator_apps = unit.get_prop('applications') or []
        
        # Look for application that created this unit
        for app in creator_apps:
            if app.get('task_info'):
                return app
        return None

    def compute_action(context: Dict[str, Any]) -> bool:
        """Create prevention rule based on failure analysis."""
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
        if not changed_slot:
            return False

        # Create prevention rule
        rule_name = f"prevent_{changed_slot}_changes"
        prevention_rule = {
            'name': rule_name,
            'isa': ['prevention-rule'],
            'english': (
                f"Prevent changes to {changed_slot} slot that led to the "
                f"failure of {unit.name}"
            ),
            'slot_to_avoid': changed_slot,
            'learned_from': unit.name,
            'creditor': creator
        }

        # Record the new rule
        context['task_results'] = context.get('task_results', {})
        context['task_results']['new_units'] = [prevention_rule]
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

        logger.info(
            f"\nLearned prevention rule from failure of {unit.name}:"
        )
        
        for rule in new_units:
            logger.info(
                f"- Will prevent changes to {rule['slot_to_avoid']} slot"
            )
        return True

    # Configure heuristic slots
    heuristic.set_prop('if_potentially_relevant', check_unit_deletion)
    heuristic.set_prop('then_compute', compute_action)
    heuristic.set_prop('then_print_to_user', print_to_user)