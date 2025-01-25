"""H14 heuristic implementation: Create prevention rules for problematic replacements.

This heuristic creates prevention rules when concepts are deleted by analyzing patterns
where specific replacement components consistently lead to failures. It examines both
the specific values and their types to identify problematic replacement patterns.
"""
from typing import Any, Dict, Optional, Tuple, Union, Callable
from ..unit import Unit
import logging
import types

logger = logging.getLogger(__name__)

def setup_h14(heuristic) -> None:
    """Configure H14: Create prevention rules for problematic replacements."""
    # Set properties from original LISP implementation
    heuristic.set_prop('worth', 700)
    heuristic.set_prop('english',
        "IF C is about to die, then try to form a new heuristic, one which -- "
        "had it existed earlier -- would have prevented C from ever being defined "
        "in the first place, by preventing the same losing sort of entity being "
        "the replacer")
    heuristic.set_prop('abbrev', "Form a rule that would have prevented this mistake")
    heuristic.set_prop('arity', 1)

    def check_potentially_relevant(context: Dict[str, Any]) -> bool:
        """Check if unit is being deleted."""
        unit = context.get('unit')
        deleted_units = context.get('deleted_units', [])
        return unit and unit.name in deleted_units

    def check_relevance(context: Dict[str, Any]) -> bool:
        """Check if we can identify replacement patterns."""
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
            
        from_type = pattern.get('from_type', '')
        to_type = pattern.get('to_type', '')
        
        logger.info(f"\nJust before destroying {unit.name}, created prevention rule: "
                   f"will no longer replace {from_type} values with {to_type} values "
                   f"in the {pattern.get('slot')} slot")
        return True

    def compute_action(context: Dict[str, Any]) -> bool:
        """Create prevention rule from replacement pattern."""
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
            
        # Extract replacement pattern
        pattern = extract_replacement_pattern(app_record)
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
        slot, old_val, new_val, from_type, to_type = pattern
        context['task_results'].update({
            'new_units': [rule_unit],
            'pattern_detected': {
                'slot': slot,
                'from': old_val,
                'to': new_val,
                'from_type': from_type,
                'to_type': to_type
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

    def extract_replacement_pattern(record: Dict[str, Any]) -> Optional[Tuple[str, Any, Any, str, str]]:
        """Extract the replacement pattern including type information."""
        try:
            task_info = record.get('task_info', {})
            if not task_info:
                return None
                
            slot = task_info.get('slot_to_change')
            old_value = task_info.get('old_value')
            new_value = task_info.get('new_value')
            
            if not all([slot, old_value is not None, new_value is not None]):
                return None
                
            # Determine value types
            from_type = get_value_type(old_value)
            to_type = get_value_type(new_value)
                
            return (slot, old_value, new_value, from_type, to_type)
            
        except Exception as e:
            logger.error(f"Error extracting replacement pattern: {e}")
            return None

    def get_value_type(value: Any) -> str:
        """Determine a descriptive type for a value."""
        if isinstance(value, (int, float)):
            return 'number'
        elif isinstance(value, str):
            return 'string'
        elif isinstance(value, (types.FunctionType, types.LambdaType)):
            return 'function'
        elif isinstance(value, list):
            return 'list'
        elif isinstance(value, dict):
            return 'dict'
        elif callable(value):
            return 'callable'
        return type(value).__name__

    def create_prevention_rule(unit: Unit, pattern: Tuple[str, Any, Any, str, str],
                             creditor: str) -> Optional[Unit]:
        """Create a new prevention rule unit."""
        try:
            # Create rule unit
            rule = Unit(f"prevent-repl-{unit.name}", worth=600)
            
            # Unpack pattern
            slot, old_val, new_val, from_type, to_type = pattern
            
            # Set properties
            rule.set_prop('isa', ['prevention-rule'])
            rule.set_prop('slot_to_avoid', slot)
            rule.set_prop('pattern_from', str(old_val))
            rule.set_prop('pattern_to', str(new_val))
            rule.set_prop('from_type', from_type)
            rule.set_prop('to_type', to_type)
            rule.set_prop('learned_from', unit.name)
            rule.set_prop('source_creditor', creditor)
            rule.set_prop('english',
                f"Do not replace {from_type} values with {to_type} values in the {slot} slot")
            
            # Add behavior enforcement functions
            def check_potential(task_context: Dict[str, Any]) -> bool:
                """Check if a task might violate this prevention rule."""
                task = task_context.get('task', {})
                unit = task_context.get('unit')
                if not task or not unit:
                    return False
                    
                # Check slot match
                if task.get('slot_to_change') != slot:
                    return False
                    
                # Get current value of that slot
                current_value = unit.get_prop(slot)
                if current_value is None:
                    return False
                    
                # Check current value type
                if get_value_type(current_value) != from_type:
                    return False
                    
                # Check new value type
                new_value = task.get('new_value')
                if new_value is None:
                    return False
                    
                # Match if new value has the problematic type
                return get_value_type(new_value) == to_type
                       
            def validate_change(task_context: Dict[str, Any]) -> bool:
                """Validate if a proposed change violates this prevention rule."""
                return not check_potential(task_context)
                
            def explain_violation(task_context: Dict[str, Any]) -> str:
                """Explain why a change was prevented."""
                task = task_context.get('task', {})
                unit = task_context.get('unit')
                if not task or not unit:
                    return "Invalid task context"
                    
                current_value = unit.get_prop(task.get('slot_to_change'))
                new_value = task.get('new_value')
                
                return (f"Prevented replacing {from_type} value ({current_value}) with "
                       f"{to_type} value ({new_value}) in {slot} slot based on learning "
                       f"from failure of {unit.name}")
                       
            rule.set_prop('if_potentially_relevant', check_potential)
            rule.set_prop('if_truly_relevant', validate_change)
            rule.set_prop('explain_prevention', explain_violation)
            
            return rule
            
        except Exception as e:
            logger.error(f"Error creating prevention rule: {e}")
            return None

    # Configure the heuristic
    heuristic.set_prop('if_potentially_relevant', check_potentially_relevant)
    heuristic.set_prop('if_truly_relevant', check_relevance)
    heuristic.set_prop('then_print_to_user', print_results)
    heuristic.set_prop('then_compute', compute_action)