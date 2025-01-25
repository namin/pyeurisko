"""H14 heuristic implementation: Prevent modifications based on entity types."""
from typing import Any, Dict, List, Optional, Tuple
from ..unit import Unit
import logging

logger = logging.getLogger(__name__)

def setup_h14(heuristic) -> None:
    """Configure H14: Create rules to prevent problematic type transitions."""
    def check_relevance(context: Dict[str, Any]) -> bool:
        """Check if unit is being deleted and we can learn from it."""
        unit = context.get('unit')
        if not unit:
            return False
            
        deleted_units = context.get('deleted_units', [])
        return unit.name in deleted_units

    def determine_value_type(value: Any, registry) -> str:
        """Determine the type category of a value."""
        if isinstance(value, str) and registry.get_unit(value):
            unit = registry.get_unit(value)
            # Use most specific non-unit category if available
            categories = unit.get_prop('isa') or []
            for category in categories:
                if category != 'unit':
                    return category
            return 'unit'
            
        if callable(value):
            return 'function'
        elif isinstance(value, bool):
            return 'boolean'
        elif isinstance(value, (int, float)):
            return 'number'
        elif isinstance(value, str):
            return 'string'
        elif isinstance(value, list):
            return 'list'
        elif isinstance(value, dict):
            return 'dict'
        else:
            return 'unknown'

    def extract_type_transition(task_info: Dict[str, Any], registry) -> Optional[Tuple[str, str, str]]:
        """Extract the slot name and type transition from task info."""
        if not isinstance(task_info, dict):
            return None
            
        slot_name = task_info.get('slot_to_change')
        old_value = task_info.get('old_value')
        new_value = task_info.get('new_value')
        
        if not all([slot_name, old_value is not None, new_value is not None]):
            return None
            
        old_type = determine_value_type(old_value, registry)
        new_type = determine_value_type(new_value, registry)
        
        return (slot_name, old_type, new_type)

    def compute_action(context: Dict[str, Any]) -> bool:
        """Create rule to prevent problematic type transitions."""
        unit = context.get('unit')
        if not unit:
            return False
            
        # Find the creation task
        creditors = unit.get_prop('creditors') or []
        creator_tasks = []
        
        for creditor_name in creditors:
            creditor = heuristic.unit_registry.get_unit(creditor_name)
            if not creditor:
                continue
                
            applications = creditor.get_prop('applications') or []
            for app in applications:
                task_info = {}
                results = []
                
                if isinstance(app, dict):
                    task_info = app.get('task_info', {})
                    results = app.get('result', [])
                elif isinstance(app, (list, tuple)) and len(app) >= 3:
                    results = app[1] if isinstance(app[1], list) else [app[1]]
                    task_info = app[2] if isinstance(app[2], dict) else {}
                    
                if unit.name in results:
                    creator_tasks.append((creditor_name, task_info))
                    
        if not creator_tasks:
            return False
            
        # Extract type transition from the creation task
        creditor_name, task_info = creator_tasks[0]
        transition = extract_type_transition(task_info, heuristic.unit_registry)
        if not transition:
            return False
            
        slot_name, from_type, to_type = transition
        
        # Create prevention rule
        rule_name = f"prevent_{from_type}_to_{to_type}_in_{slot_name}"
        prevention_rule = Unit(rule_name, worth=700)
        prevention_rule.set_prop('isa', ['heuristic', 'prevention-rule'])
        prevention_rule.set_prop('english',
            f"Prevent changing {slot_name} values from {from_type} to {to_type} types "
            f"based on failure of {unit.name}")
            
        # Set prevention rule properties
        prevention_rule.set_prop('slot_to_avoid', slot_name)
        prevention_rule.set_prop('from_type', from_type)
        prevention_rule.set_prop('to_type', to_type)
        prevention_rule.set_prop('learned_from', unit.name)
        prevention_rule.set_prop('source_creditor', creditor_name)
        
        # Create relevance check for similar type transitions
        def check_type_transition(ctx: Dict[str, Any]) -> bool:
            task = ctx.get('task', {})
            if task.get('task_type') != 'modification':
                return False
                
            if task.get('slot_to_change') != slot_name:
                return False
                
            current_unit = ctx.get('unit')
            if not current_unit:
                return False
                
            current_value = current_unit.get_prop(slot_name)
            new_value = task.get('new_value')
            
            current_type = determine_value_type(current_value, heuristic.unit_registry)
            target_type = determine_value_type(new_value, heuristic.unit_registry)
            
            return (current_type == from_type and 
                    target_type == to_type)
                    
        prevention_rule.set_prop('if_potentially_relevant', check_type_transition)
        
        # Register the rule
        heuristic.unit_registry.register(prevention_rule)
        
        # Update task results
        task_results = context.get('task_results', {})
        new_units = task_results.get('new_units', [])
        new_units.append(prevention_rule)
        task_results['new_units'] = new_units
        task_results['prevention_rule'] = rule_name
        task_results['type_transition'] = {
            'slot': slot_name,
            'from_type': from_type,
            'to_type': to_type
        }
        
        return True

    # Set up heuristic properties
    heuristic.set_prop('if_potentially_relevant', check_relevance)
    heuristic.set_prop('then_compute', compute_action)