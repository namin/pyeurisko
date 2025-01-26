"""H19 heuristic implementation: Eliminate redundant units."""
from typing import Any, Dict, List, Set
from ..units import Unit
import logging
from ..heuristics import rule_factory

logger = logging.getLogger(__name__)

def setup_h19(heuristic) -> None:
    """Configure H19: Detect and eliminate redundant units.
    
    This heuristic examines newly created units to determine if they are effectively
    identical to existing units. It prevents concept space pollution by removing
    units that don't add meaningful distinctions.
    """
    heuristic.set_prop('worth', 150)
    heuristic.set_prop('english',
        "IF we have just created new units, THEN eliminate any whose slots are "
        "equivalent to already-extant units to maintain a clean concept space.")
    heuristic.set_prop('abbrev', "Remove duplicate units")
    
    # Initialize record keeping
    heuristic.set_prop('overall_record', (71147, 172))
    heuristic.set_prop('arity', 1)

    def equivalent_values(val1: Any, val2: Any, unit1: Unit, unit2: Unit) -> bool:
        """Check if two values are equivalent, accounting for substitutions."""
        if val1 == val2:
            return True
            
        # Handle lists/tuples
        if isinstance(val1, (list, tuple)) and isinstance(val2, (list, tuple)):
            if len(val1) != len(val2):
                return False
            return all(
                equivalent_values(v1, v2, unit1, unit2)
                for v1, v2 in zip(val1, val2)
            )
            
        # Handle dictionaries
        if isinstance(val1, dict) and isinstance(val2, dict):
            if val1.keys() != val2.keys():
                return False
            return all(
                equivalent_values(val1[k], val2[k], unit1, unit2)
                for k in val1.keys()
            )
            
        # Check for substitutable values (e.g., variable names)
        substitutions = unit1.get_prop('substitutions', {})
        if val1 in substitutions and substitutions[val1] == val2:
            return True
            
        return False

    @rule_factory
    def if_finished_working_on_task(rule, context):
        """Check if we've just finished a task that created new units."""
        task = context.get('task')
        task_results = context.get('task_results', {})
        
        return bool(task_results.get('new_units'))

    @rule_factory
    def then_compute(rule, context):
        """Identify duplicate units."""
        task_results = context.get('task_results', {})
        new_units = task_results.get('new_units', [])
        if not new_units:
            return False
            
        doomed_units = []
        for unit_name in new_units:
            unit = rule.unit_registry.get_unit(unit_name)
            if not unit:
                continue
                
            # Find potential equivalent units
            criterial_slots = unit.get_prop('criterial_slots', [])
            if not criterial_slots:
                criterial_slots = unit.get_prop('slots', [])
                
            # Get units in same categories
            categories = unit.get_prop('isa', [])
            potential_matches = set()
            for category in categories:
                category_units = rule.unit_registry.get_units_by_category(category)
                if category_units:
                    potential_matches.update(category_units)
                    
            # Remove self and known specializations/generalizations
            potential_matches.discard(unit_name)
            for spec in unit.get_prop('specializations', []):
                potential_matches.discard(spec)
            for gen in unit.get_prop('generalizations', []):
                potential_matches.discard(gen)
                
            # Check each potential match
            for other_name in potential_matches:
                other = rule.unit_registry.get_unit(other_name)
                if not other:
                    continue
                    
                # Check if all criterial slots match
                matches = True
                for slot in criterial_slots:
                    val1 = unit.get_prop(slot)
                    val2 = other.get_prop(slot)
                    
                    if not equivalent_values(val1, val2, unit, other):
                        matches = False
                        break
                        
                if matches:
                    doomed_units.append(unit_name)
                    # Record which unit this duplicates
                    context[f'duplicate_of_{unit_name}'] = other_name
                    break
                    
        if doomed_units:
            context['doomed_units'] = doomed_units
            return True
            
        return False

    @rule_factory
    def then_print_to_user(rule, context):
        """Explain which units were found to be duplicates and why."""
        doomed_units = context.get('doomed_units', [])
        task_results = context.get('task_results', {})
        
        if not doomed_units:
            return False
            
        new_units = task_results.get('new_units', [])
        
        logger.info(
            f"\nFound {len(doomed_units)} duplicate units among {len(new_units)} "
            f"new creations."
        )
        
        for unit_name in doomed_units:
            duplicate_of = context.get(f'duplicate_of_{unit_name}')
            if duplicate_of:
                logger.info(f"\n{unit_name} duplicates existing unit: {duplicate_of}")
            
        return True

    @rule_factory
    def then_delete_old_concepts(rule, context):
        """Remove duplicate units from the system."""
        doomed_units = context.get('doomed_units', [])
        task_results = context.get('task_results', {})
        
        if not doomed_units:
            return False
            
        # Remove doomed units from new_units list
        new_units = task_results.get('new_units', [])
        updated_units = [u for u in new_units if u not in doomed_units]
        task_results['new_units'] = updated_units
        
        # Delete the duplicate units
        for unit_name in doomed_units:
            rule.unit_registry.delete_unit(unit_name)
                
        return True