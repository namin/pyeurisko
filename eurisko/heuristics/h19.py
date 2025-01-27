"""H19 heuristic implementation: Eliminate redundant newly created units."""
import logging
from ..heuristics import rule_factory

logger = logging.getLogger(__name__)

def setup_h19(heuristic):
    """Configure H19 to detect and eliminate redundant units."""
    heuristic.set_prop('worth', 150)
    heuristic.set_prop('english',
        "IF new units have been synthesized, THEN eliminate any whose slots "
        "are equivalent to already-extant units")
    heuristic.set_prop('abbrev', "Kill any new unit that's the same as an existing one")
    heuristic.set_prop('arity', 1)

    # Add success record functions
    def then_compute_record(rule, context):
        return True
    def then_delete_old_concepts_record(rule, context):
        return True 
    heuristic.set_prop('then_compute_record', then_compute_record)
    heuristic.set_prop('then_delete_old_concepts_record', then_delete_old_concepts_record)

    @rule_factory
    def if_potentially_relevant(rule, context):
        """Check for new units to potentially delete."""
        task_results = context.get('task_results', {})
        new_units = task_results.get('new_units', [])
        return bool(new_units)

    @rule_factory
    def then_compute(rule, context):
        """Find units that duplicate existing ones."""
        task_results = context.get('task_results', {})
        new_units = task_results.get('new_units', [])
        unit_registry = rule.unit_registry
        
        if not new_units:
            return False
            
        # Track units to eliminate
        doomed_units = []
        
        # For each new unit, check against all examples of its types
        for unit in new_units:
            # Get all examples of unit's types
            unit_types = unit.get_prop('isa', [])
            all_examples = []
            for unit_type in unit_types:
                examples = unit_registry.get_examples(unit_type)
                if examples:
                    all_examples.extend(examples)
            
            # Remove self and any specialized versions
            existing_units = [u for u in all_examples 
                            if u != unit and u not in unit.get_prop('specializations', [])]
            
            # Check each unit's slots
            for other in existing_units:
                # Compare all regular slots
                slots = set(unit.properties.keys()) & set(other.properties.keys())
                slots = [s for s in slots if s in unit_registry.get_slot_examples()]
                
                # Check if all slot values match
                if slots and all(unit.get_prop(s) == other.get_prop(s) for s in slots):
                    doomed_units.append(unit)
                    break
                    
        # Remove doomed units from results
        if doomed_units:
            context['doomed_units'] = doomed_units
            new_units = [u for u in new_units if u not in doomed_units]
            task_results['new_units'] = new_units
            context['task_results'] = task_results
            return True
            
        return True  # Still return True even if no units to delete

    @rule_factory
    def then_delete_old_concepts(rule, context):
        """Delete the redundant units."""
        doomed_units = context.get('doomed_units', [])
        unit_registry = rule.unit_registry
        
        # Update task results either way
        task_results = context.get('task_results', {})
        task_results['status'] = 'completed'
        task_results['success'] = True
            
        if doomed_units:
            # Delete each unit
            for unit in doomed_units:
                unit_registry.delete_unit(unit)
            task_results['deleted_units'] = doomed_units
            logger.info(f"Deleted redundant units: {doomed_units}")
        else:
            task_results['deleted_units'] = []
            logger.info("No redundant units found")
            
        context['task_results'] = task_results
        return True # Return True even with no units to delete