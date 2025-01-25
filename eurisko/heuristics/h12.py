"""H12 heuristic implementation: Form preventive rules from mistakes."""
from typing import Any, Dict, List
from ..unit import Unit
import logging

logger = logging.getLogger(__name__)

def setup_h12(heuristic) -> None:
    """Configure H12: Learn from mistakes by creating preventive rules."""
    def check_relevance(context: Dict[str, Any]) -> bool:
        """Check if unit is being deleted and we can learn from it."""
        unit = context.get('unit')
        if not unit:
            return False
            
        # Check if unit is marked for deletion
        deleted_units = context.get('deleted_units', [])
        return unit.name in deleted_units

    def compute_action(context: Dict[str, Any]) -> bool:
        """Create rule to prevent similar mistakes."""
        unit = context.get('unit')
        if not unit:
            return False
            
        # Find the task that created this unit
        creditors = unit.get_prop('creditors') or []
        if not creditors:
            return False
            
        creation_tasks = []
        for creditor in creditors:
            creditor_unit = heuristic.unit_registry.get_unit(creditor)
            if not creditor_unit:
                continue
                
            # Look through creditor's applications
            applications = creditor_unit.get_prop('applications') or []
            for app in applications:
                if isinstance(app, dict):
                    results = app.get('result', [])
                    if isinstance(results, list) and unit.name in results:
                        creation_tasks.append(app)
                elif isinstance(app, (list, tuple)) and len(app) >= 2:
                    if unit.name in app[1]:
                        creation_tasks.append(app)
                        
        if not creation_tasks:
            return False
            
        # Extract slot that was changed from creation task
        creation_task = creation_tasks[0]  # Use first task found
        task_info = creation_task.get('task_info', {}) if isinstance(creation_task, dict) else {}
        slot_to_change = task_info.get('slot_to_change')
        
        if not slot_to_change:
            return False
            
        # Create prevention rule
        rule_name = f"avoid_{slot_to_change}_change"
        prevention_rule = Unit(rule_name, worth=700)
        prevention_rule.set_prop('isa', ['heuristic', 'prevention-rule'])
        prevention_rule.set_prop('english', 
            f"Prevent changes to {slot_to_change} slot when similar to failed unit {unit.name}")
        prevention_rule.set_prop('slot_to_avoid', slot_to_change)
        prevention_rule.set_prop('learned_from', unit.name)
        
        # Add check conditions based on failure
        prevention_rule.set_prop('if_potentially_relevant', 
            lambda ctx: ctx.get('task', {}).get('task_type') == 'modification' and
                       ctx.get('task', {}).get('slot_to_change') == slot_to_change)
                       
        # Register the new rule
        heuristic.unit_registry.register(prevention_rule)
        
        # Update task results
        task_results = context.get('task_results', {})
        new_units = task_results.get('new_units', [])
        new_units.append(prevention_rule)
        task_results['new_units'] = new_units
        task_results['prevention_rule'] = rule_name
        
        return True

    # Set up heuristic properties
    heuristic.set_prop('if_potentially_relevant', check_relevance)
    heuristic.set_prop('then_compute', compute_action)