"""H12 heuristic implementation: Create prevention rules from failed concepts."""
from typing import Any, Dict, List, Optional
import logging
from ..heuristics import rule_factory

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
        creator = creditors[0]  # Main creator
        context['creator'] = creator
        return True

    @rule_factory
    def then_compute(rule, context):
        """Create prevention rule based on failure analysis."""
        unit = context.get('unit')
        creator = context.get('creator')
        if not unit or not creator:
            return False

        # Find task that created this unit by checking creator's applications
        creator_apps = unit.get_prop('applications') or []
        creation_task = None
        for app in creator_apps:
            if app.get('task_info'):
                creation_task = app
                break
                
        if not creation_task:
            return False

        task_info = creation_task.get('task_info', {})
        changed_slot = task_info.get('slot_to_change')
        if not changed_slot:
            return False

        # Create prevention rule unit
        rule_name = f"prevent_{changed_slot}_changes"
        prevention_rule = rule.unit_registry.create_unit(rule_name)
        if not prevention_rule:
            return False
            
        prevention_rule.set_prop('isa', ['prevention-rule'])
        prevention_rule.set_prop('english', 
            f"Prevent changes to {changed_slot} slot that led to the "
            f"failure of {unit.name}")
        prevention_rule.set_prop('slot_to_avoid', changed_slot)
        prevention_rule.set_prop('learned_from', unit.name)
        prevention_rule.set_prop('creditor', creator)
        
        # Register the new rule
        rule.unit_registry.register(prevention_rule)

        # Record the new rule in results
        context['task_results'] = context.get('task_results', {})
        context['task_results']['new_units'] = [prevention_rule]
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

        logger.info(
            f"\nLearned prevention rule from failure of {unit.name}:"
        )
        
        for prevention_rule in new_units:
            logger.info(
                f"- Will prevent changes to {prevention_rule.get_prop('slot_to_avoid')} slot"
            )
        return True