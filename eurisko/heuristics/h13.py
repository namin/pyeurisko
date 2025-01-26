"""H13 heuristic implementation: Create modification prevention rules."""
from typing import Any, Dict, List, Optional
import logging
from ..heuristics import rule_factory

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

    @rule_factory
    def if_potentially_relevant(rule, context):
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

    @rule_factory
    def then_compute(rule, context):
        """Create prevention rules based on modification analysis."""
        unit = context.get('unit')
        creator = context.get('creator')
        if not unit or not creator:
            return False

        # Get information about how unit was created by examining applications
        creator_apps = unit.get_prop('applications') or []
        creation_task = None
        for app in creator_apps:
            if app.get('task_info'):
                task_info = app['task_info']
                if 'old_value' in task_info and 'new_value' in task_info:
                    # Analyze the modification pattern
                    old_value = task_info['old_value']
                    new_value = task_info['new_value']
                    
                    if old_value is None or new_value is None:
                        continue
                        
                    pattern = {
                        'from': str(old_value),
                        'to': str(new_value),
                        'from_type': type(old_value).__name__,
                        'to_type': type(new_value).__name__,
                        'type_changed': type(old_value) != type(new_value),
                        'complexity_increased': len(str(new_value)) > len(str(old_value))
                    }
                    
                    task_info['pattern'] = pattern
                    creation_task = app
                    break

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
        
        prevention_rule = rule.unit_registry.create_unit(rule_name)
        if not prevention_rule:
            return False
            
        prevention_rule.set_prop('isa', ['prevention-rule'])
        prevention_rule.set_prop('english',
            f"Prevent changes to {changed_slot} slot that convert "
            f"{pattern['from_type']} values to {pattern['to_type']} values")
        prevention_rule.set_prop('slot_to_avoid', changed_slot)
        prevention_rule.set_prop('pattern_from', pattern['from'])
        prevention_rule.set_prop('pattern_to', pattern['to'])
        prevention_rule.set_prop('learned_from', unit.name)
        prevention_rule.set_prop('source_creditor', creator)
        
        # Register the new rule
        rule.unit_registry.register(prevention_rule)

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

    @rule_factory
    def then_print_to_user(rule, context):
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