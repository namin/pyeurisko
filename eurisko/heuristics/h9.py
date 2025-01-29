"""H9 heuristic implementation: Find examples by checking generalizations.

This heuristic looks for examples of a unit by checking existing generalizations and the ISA hierarchy
for valid examples that meet the unit's definition.
"""
import logging
from typing import Any, Dict, List, Optional
from ..heuristics import rule_factory

logger = logging.getLogger(__name__)

def init_task_results(context: Dict[str, Any]) -> Dict[str, Any]:
    """Initialize task results structure if needed."""
    if 'task_results' not in context:
        context['task_results'] = {
            'status': 'in_progress',
            'initial_unit_state': {},
            'new_units': [],
            'new_tasks': [],
            'modified_units': []
        }
    else:
        results = context['task_results']
        if 'new_units' not in results:
            results['new_units'] = []
        if 'new_tasks' not in results:
            results['new_tasks'] = []
        if 'modified_units' not in results:
            results['modified_units'] = []
    return context['task_results']

def get_generalizations(unit, task_manager, include_self=False) -> List[Any]:
    """Get generalizations and ISA parent examples.
    
    Args:
        unit: Unit to get generalizations for
        task_manager: Task manager for registry access
        include_self: Whether to include the unit itself in exclusions
        
    Returns:
        List of generalization units excluding the unit and its specializations
    """
    generalizations = set()
    exclusions = set()
    
    # Units to exclude
    if include_self:
        exclusions.add(unit)
        
    # Add specializations to exclusions    
    spec_names = unit.get_prop('specializations', [])
    for name in spec_names:
        spec = task_manager.unit_registry.get_unit(name)
        if spec:
            exclusions.add(spec)
            
    # Direct generalizations
    gen_names = unit.get_prop('generalizations', [])
    for name in gen_names:
        gen = task_manager.unit_registry.get_unit(name)
        if gen and gen not in exclusions:
            generalizations.add(gen)
            
    # Parent category examples from ISA
    isa_names = unit.get_prop('isa', [])
    for name in isa_names:
        isa_unit = task_manager.unit_registry.get_unit(name)
        if not isa_unit:
            continue
            
        for ex_name in isa_unit.get_prop('examples', []):
            ex_unit = task_manager.unit_registry.get_unit(ex_name)
            if ex_unit and ex_unit not in exclusions:
                generalizations.add(ex_unit)
                
    return list(generalizations)

def is_active_unit(unit) -> bool:
    """Check if a unit is active (not killed)."""
    # Could be expanded based on unit state flags
    return bool(unit)

def setup_h9(heuristic) -> None:
    """Configure H9: Find examples by checking generalizations."""
    heuristic.set_prop('worth', 700)
    heuristic.set_prop('english',
        "IF the current task is to find examples of a unit, and it has a definition, "
        "THEN look over instances of generalizations of the unit, and see if any of "
        "them are valid examples of this as well")
    heuristic.set_prop('abbrev', "Find examples by checking generalizations")
    heuristic.set_prop('arity', 1)

    @rule_factory
    def if_potentially_relevant(rule, context: Dict[str, Any]) -> bool:
        """Check task validity and required data."""
        task = context.get('task')
        if not task:
            logger.debug("H9: No task")
            return False
            
        logger.debug(f"H9 task type: {task.task_type}, slot: {task.slot_name}")
        
        # Must be finding examples
        if task.task_type != 'find_examples' or task.slot_name != 'examples':
            logger.debug("H9: Wrong task type/slot")
            return False
            
        return True

    @rule_factory
    def if_truly_relevant(rule, context: Dict[str, Any]) -> bool:
        """Check if unit has definition and potential examples sources."""
        unit = context.get('unit')
        if not unit:
            logger.debug("H9: No unit")
            return False
            
        # Get definition and verify it's callable
        definition = unit.get_prop('definition')
        if not callable(definition):
            logger.debug("H9: No callable definition")
            return False
            
        # Get generalizations excluding self and specializations
        space_to_use = get_generalizations(unit, rule.task_manager, include_self=True)
        space_to_use = [u for u in space_to_use if is_active_unit(u)]
        
        if not space_to_use:
            logger.debug("H9: No valid generalizations")
            return False
            
        # Store for compute phase  
        context['definition'] = definition
        context['space_to_use'] = space_to_use
        
        logger.debug(f"H9: Found definition and {len(space_to_use)} potential sources")
        return True

    @rule_factory
    def then_compute(rule, context: Dict[str, Any]) -> bool:
        """Try definition on examples from generalizations."""
        unit = context.get('unit')
        definition = context.get('definition') 
        space_to_use = context.get('space_to_use')
        
        if not all([unit, definition, space_to_use]):
            logger.debug("H9: Missing required context")
            return False
            
        # Track examples
        current_examples = unit.get_prop('examples', [])
        non_examples = unit.get_prop('non_examples', [])
        new_examples = []
        
        # Maximum examples to check
        max_examples = 400  # From original LISP code
        count = 0
        
        # Check examples from each generalization
        for gen_unit in space_to_use:
            if count >= max_examples:
                break
                
            for example in gen_unit.get_prop('examples', []):
                if count >= max_examples:
                    break
                    
                # Skip if already processed
                if example in current_examples or example in non_examples:
                    continue
                    
                count += 1
                try:
                    # Test definition and update lists
                    if definition(example):
                        new_examples.append(example)
                        current_examples.append(example)
                    else:
                        non_examples.append(example)
                except Exception as e:
                    logger.warning(f"Failed to test {example} with {unit.name}'s definition: {e}")
                    
        if not new_examples:
            logger.debug("H9: No new examples found")
            return False
            
        # Update unit
        unit.set_prop('examples', current_examples)
        unit.set_prop('non_examples', non_examples)
        
        # Update results
        task_results = init_task_results(context)
        task_results['status'] = 'completed'
        task_results['success'] = True
        task_results['modified_units'].append(unit)
        task_results['new_values'] = {
            'unit': unit.name,
            'slot': 'examples',
            'values': new_examples,
            'description': (f"Found {len(new_examples)} examples by examining "
                         f"examples of {len(space_to_use)} generalizations")
        }
        
        logger.info(f"H9: Added {len(new_examples)} examples to {unit.name}")
        return True

    @rule_factory
    def then_print_to_user(rule, context: Dict[str, Any]) -> bool:
        """Print results summary."""
        unit = context.get('unit')
        task_results = context.get('task_results', {})
        new_values = task_results.get('new_values', {})
        
        if not all([unit, new_values]):
            return False
            
        values = new_values.get('values', [])
        logger.info(f"\nInstantiated {unit.name}; found {len(values)} examples")
        logger.info(f"    Namely: {values}")
        return True

    # Register rule functions
    heuristic.set_prop('if_potentially_relevant', if_potentially_relevant)
    heuristic.set_prop('if_truly_relevant', if_truly_relevant)
    heuristic.set_prop('then_compute', then_compute)
    heuristic.set_prop('then_print_to_user', then_print_to_user)