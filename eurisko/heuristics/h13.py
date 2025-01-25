"""H13 heuristic implementation: Create rules to prevent similar modifications."""
from typing import Any, Dict, List, Optional, Tuple
from ..unit import Unit
import logging

logger = logging.getLogger(__name__)

def setup_h13(heuristic) -> None:
    """Configure H13: Create rules to prevent similar faulty modifications."""
    def check_relevance(context: Dict[str, Any]) -> bool:
        """Check if unit is being deleted and we can learn from it."""
        unit = context.get('unit')
        if not unit:
            return False
            
        # Check if unit is marked for deletion
        deleted_units = context.get('deleted_units', [])
        return unit.name in deleted_units

    def extract_change_pattern(task_info: Dict[str, Any]) -> Optional[Tuple[str, Any, Any]]:
        """Extract pattern of change from task info."""
        if not isinstance(task_info, dict):
            return None
            
        # Get the changed slot and values
        slot_name = task_info.get('slot_to_change')
        if not slot_name:
            return None
            
        old_value = task_info.get('old_value')
        new_value = task_info.get('new_value')
        
        if old_value is None or new_value is None:
            return None
            
        return (slot_name, old_value, new_value)

    def compute_action(context: Dict[str, Any]) -> bool:
        """Create rule to prevent similar failed modifications."""
        unit = context.get('unit')
        if not unit:
            return False
            
        # Find the task that created this unit
        creator_tasks = []
        for creditor in (unit.get_prop('creditors') or []):
            creditor_unit = heuristic.unit_registry.get_unit(creditor)
            if not creditor_unit:
                continue
                
            # Look through applications for creation task
            applications = creditor_unit.get_prop('applications') or []
            for app in applications:
                if isinstance(app, dict):
                    results = app.get('result', [])
                    task_info = app.get('task_info', {})
                    
                    if isinstance(results, list) and unit.name in results:
                        creator_tasks.append((creditor, task_info))
                elif isinstance(app, (list, tuple)) and len(app) >= 2:
                    if unit.name in app[1] and len(app) >= 3:
                        task_info = app[2] if isinstance(app[2], dict) else {}
                        creator_tasks.append((creditor, task_info))
                        
        if not creator_tasks:
            return False
            
        # Extract change pattern from the creation task
        creditor, task_info = creator_tasks[0]  # Use first task
        change_pattern = extract_change_pattern(task_info)
        if not change_pattern:
            return False
            
        slot_name, old_value, new_value = change_pattern
        
        # Create prevention rule
        rule_name = f"avoid_{slot_name}_change_pattern"
        prevention_rule = Unit(rule_name, worth=700)
        prevention_rule.set_prop('isa', ['heuristic', 'prevention-rule'])
        prevention_rule.set_prop('english',
            f"Prevent changes to {slot_name} from {old_value} to {new_value} based on failure of {unit.name}")
        prevention_rule.set_prop('slot_to_avoid', slot_name)
        prevention_rule.set_prop('pattern_from', old_value)
        prevention_rule.set_prop('pattern_to', new_value)
        prevention_rule.set_prop('learned_from', unit.name)
        prevention_rule.set_prop('source_creditor', creditor)
        
        # Add relevance check that looks for similar modifications
        def check_modification(ctx):
            task = ctx.get('task', {})
            if task.get('task_type') != 'modification':
                return False
                
            if task.get('slot_to_change') != slot_name:
                return False
                
            current_value = ctx.get('unit', {}).get_prop(slot_name)
            target_value = task.get('new_value')
            
            # Check if this modification matches the failed pattern
            return (current_value == old_value and
                    target_value == new_value)
        
        prevention_rule.set_prop('if_potentially_relevant', check_modification)
        
        # Register the new rule
        heuristic.unit_registry.register(prevention_rule)
        
        # Update task results
        task_results = context.get('task_results', {})
        new_units = task_results.get('new_units', [])
        new_units.append(prevention_rule)
        task_results['new_units'] = new_units
        task_results['prevention_rule'] = rule_name
        task_results['pattern_detected'] = {
            'slot': slot_name,
            'from': old_value,
            'to': new_value
        }
        
        return True

    # Set up heuristic properties
    heuristic.set_prop('if_potentially_relevant', check_relevance)
    heuristic.set_prop('then_compute', compute_action)