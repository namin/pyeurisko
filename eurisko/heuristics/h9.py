"""H9 heuristic implementation: Find examples by examining generalizations."""
from typing import Any, Dict, List, Set
from ..unit import Unit
import logging

logger = logging.getLogger(__name__)

def setup_h9(heuristic) -> None:
    """Configure H9: Find examples by examining generalizations."""
    def check_task(context: Dict[str, Any]) -> bool:
        """Check if we're looking for examples and unit has definition."""
        unit = context.get('unit')
        task = context.get('task')
        if not unit or not task:
            return False
            
        if task.get('task_type') != 'find_examples':
            return False
            
        # Check for definition existence
        if not unit.get_prop('definition'):
            return False
            
        # Check for generalizations to examine
        generalizations = unit.get_prop('generalizations') or []
        if not generalizations:
            # Check isa relationships for examples if no direct generalizations
            isa_types = unit.get_prop('isa') or []
            found = False
            for typ in isa_types:
                type_unit = heuristic.unit_registry.get_unit(typ)
                if type_unit and type_unit.get_prop('examples'):
                    found = True
                    break
            if not found:
                return False
                
        return True

    def compute_action(context: Dict[str, Any]) -> bool:
        """Find examples by examining generalizations."""
        unit = context.get('unit')
        if not unit:
            return False
            
        definition = unit.get_prop('definition')
        if not definition:
            return False
            
        # Collect potential spaces to examine
        spaces_to_use = set()
        
        # Direct generalizations
        generalizations = unit.get_prop('generalizations') or []
        spaces_to_use.update(generalizations)
        
        # Add examples from isa types
        isa_types = unit.get_prop('isa') or []
        for typ in isa_types:
            type_unit = heuristic.unit_registry.get_unit(typ)
            if type_unit:
                examples = type_unit.get_prop('examples') or []
                spaces_to_use.update(examples)
                
        # Remove unit itself and its specializations
        specializations = unit.get_prop('specializations') or []
        spaces_to_use.discard(unit.name)
        for spec in specializations:
            spaces_to_use.discard(spec)
            
        if not spaces_to_use:
            return False
            
        # For each space, examine its examples
        new_examples = []
        current_examples = unit.get_prop('examples') or []
        current_non_examples = unit.get_prop('non_examples') or []
        
        for space_name in spaces_to_use:
            space_unit = heuristic.unit_registry.get_unit(space_name)
            if not space_unit:
                continue
                
            examples = space_unit.get_prop('examples') or []
            for example in examples:
                # Skip if we already know about this example
                if example in current_examples or example in current_non_examples:
                    continue
                    
                # Check if example satisfies definition
                try:
                    if definition(example):
                        new_examples.append(example)
                        logger.debug(f"Found new example {example} for {unit.name}")
                    else:
                        # Record non-examples for future reference
                        current_non_examples.append(example)
                except Exception as e:
                    logger.warning(f"Failed to evaluate definition on {example}: {e}")
                    
        if new_examples:
            # Update examples list
            unit.set_prop('examples', current_examples + new_examples)
            
            # Update non-examples list if changed
            if len(current_non_examples) > len(unit.get_prop('non_examples') or []):
                unit.set_prop('non_examples', current_non_examples)
            
            # Update task results
            task_results = context.get('task_results', {})
            task_results['new_values'] = new_examples
            task_results['source_spaces'] = list(spaces_to_use)
            return True
            
        return False

    # Set up heuristic properties
    heuristic.set_prop('if_working_on_task', check_task)
    heuristic.set_prop('then_compute', compute_action)