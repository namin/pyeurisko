"""H19 heuristic implementation: Eliminate redundant units."""
from typing import Any, Dict, List, Set
from ..unit import Unit
import logging

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

    def find_equivalent_units(unit: Unit, system: Any) -> List[Unit]:
        """Find existing units that are equivalent to the given unit.
        
        A unit is considered equivalent if all its criterial slots match
        another unit's values (after accounting for substitutions).
        """
        equivalent = []
        
        # Get criterial slots
        criterial_slots = unit.get_prop('criterial_slots', [])
        if not criterial_slots:
            # If no criterial slots specified, check all slots
            criterial_slots = unit.get_prop('slots', [])
            
        # Get all units of the same categories
        categories = unit.get_prop('isa', [])
        potential_matches = set()
        for category in categories:
            potential_matches.update(
                system.unit_registry.get_units_by_category(category)
            )
            
        # Remove self and known specializations/generalizations
        potential_matches.discard(unit.name)
        for spec in unit.get_prop('specializations', []):
            potential_matches.discard(spec)
        for gen in unit.get_prop('generalizations', []):
            potential_matches.discard(gen)
            
        for other_name in potential_matches:
            other = system.unit_registry.get_unit(other_name)
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
                equivalent.append(other)
                
        return equivalent

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

    def check_task_completion(context: Dict[str, Any]) -> bool:
        """Check if we've just finished a task that created new units."""
        task = context.get('task')
        if not task:
            return False
            
        return bool(context.get('system').get_task_result('new_units'))

    def print_to_user(context: Dict[str, Any]) -> bool:
        """Explain which units were found to be duplicates and why."""
        doomed_units = context.get('doomed_units', [])
        system = context.get('system')
        
        if not doomed_units or not system:
            return False
            
        new_units = system.get_task_result('new_units')
        
        logger.info(
            f"\nFound {len(doomed_units)} duplicate units among {len(new_units)} "
            f"new creations."
        )
        
        for unit_name in doomed_units:
            unit = system.unit_registry.get_unit(unit_name)
            if not unit:
                continue
                
            matches = find_equivalent_units(unit, system)
            logger.info(
                f"\n{unit_name} duplicates existing unit(s): "
                f"{', '.join(m.name for m in matches)}"
            )
            
        return True

    def compute_action(context: Dict[str, Any]) -> bool:
        """Identify duplicate units."""
        system = context.get('system')
        if not system:
            return False
            
        new_units = system.get_task_result('new_units')
        if not new_units:
            return False
            
        doomed_units = []
        for unit_name in new_units:
            unit = system.unit_registry.get_unit(unit_name)
            if not unit:
                continue
                
            equivalents = find_equivalent_units(unit, system)
            if equivalents:
                doomed_units.append(unit_name)
                
        context['doomed_units'] = doomed_units
        return bool(doomed_units)

    def delete_duplicates(context: Dict[str, Any]) -> bool:
        """Remove duplicate units from the system."""
        system = context.get('system')
        doomed_units = context.get('doomed_units', [])
        
        if not system or not doomed_units:
            return False
            
        # Remove doomed units from new_units list
        new_units = system.get_task_result('new_units')
        updated_units = [u for u in new_units if u not in doomed_units]
        system.set_task_result('new_units', updated_units)
        
        # Delete the duplicate units
        for unit_name in doomed_units:
            unit = system.unit_registry.get_unit(unit_name)
            if unit:
                system.delete_unit(unit_name)
                
        return True

    # Configure heuristic slots
    heuristic.set_prop('if_finished_working_on_task', check_task_completion)
    heuristic.set_prop('then_compute', compute_action)
    heuristic.set_prop('then_print_to_user', print_to_user)
    heuristic.set_prop('then_delete_old_concepts', delete_duplicates)