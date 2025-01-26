"""H19 heuristic implementation: Eliminate duplicate units."""
from typing import Any, Dict
import logging
from ..heuristics import rule_factory

logger = logging.getLogger(__name__)

def setup_h19(heuristic) -> None:
    """Configure H19: Remove duplicate units."""
    heuristic.set_prop('worth', 150)
    heuristic.set_prop('english', "IF we just created some new units, THEN eliminate any whose slots are equivalent to already-extant units")
    heuristic.set_prop('abbrev', "Kill any new unit that's the same as an existing one")
    heuristic.set_prop('arity', 1)
    
    def record_func(rule, context):
        return True
    for record_type in ['then_print_to_user', 'then_delete_old_concepts', 'overall']:
        heuristic.set_prop(f'{record_type}_record', record_func)

    @rule_factory
    def if_finished_working_on_task(rule, context):
        """Check for duplicate units."""
        task_results = context.get('task_results', {})
        new_units = task_results.get('new_units', [])
        if not new_units:
            return False
            
        doomed_units = []
        for unit in new_units:
            if not unit:
                continue
                
            unit_slots = set(s for s in unit.get_prop('slots', []) if unit.has_prop(s))
            slot_types = rule.unit_registry.get_units_by_category('slot')
            valid_slots = unit_slots & set(slot_types)
            
            generalizations = unit.get_prop('generalizations', [])
            specializations = unit.get_prop('specializations', [])
            type_examples = rule.unit_registry.get_units_by_type(unit.get_prop('type', ''))
            candidates = set(type_examples) - {unit} - set(specializations)
            
            for other in candidates:
                if all(unit.get_prop(slot) == other.get_prop(slot) for slot in valid_slots):
                    doomed_units.append(unit)
                    break
                    
        context['doomed_units'] = doomed_units
        return bool(doomed_units)

    @rule_factory
    def then_print_to_user(rule, context):
        """Print units to be deleted."""
        new_units = context.get('task_results', {}).get('new_units', [])
        doomed_units = context.get('doomed_units', [])
        if not doomed_units:
            return False
            
        logger.info(f"\nHmf! {len(doomed_units)} of the {len(new_units)} new units "
                   f"(namely: {[u.name for u in doomed_units]}) seem indistinguishable "
                   f"from pre-existing units! They must be destroyed...")
                   
        # Update new_units list
        task_results = context.get('task_results', {})
        task_results['new_units'] = [u for u in new_units if u not in doomed_units]
        context['task_results'] = task_results
        return True

    @rule_factory
    def then_delete_old_concepts(rule, context):
        """Delete duplicate units."""
        doomed_units = context.get('doomed_units', [])
        if not doomed_units:
            return False
            
        for unit in doomed_units:
            rule.unit_registry.delete_unit(unit.name)
        return True