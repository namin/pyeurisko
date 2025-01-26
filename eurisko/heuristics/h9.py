"""H9 heuristic implementation: Find examples through generalizations."""
from typing import Any, Dict, List
import logging

logger = logging.getLogger(__name__)

def setup_h9(heuristic) -> None:
    """Configure H9: Find examples by examining generalizations.
    
    This heuristic examines the examples of more general concepts to find
    examples that satisfy the current unit's definition, enabling efficient
    example discovery by leveraging the generalization hierarchy.
    """
    heuristic.set_prop('worth', 700)
    heuristic.set_prop('english',
        "IF the current task is to find examples of a unit, and it has a "
        "definition, THEN look over instances of generalizations of the unit, "
        "and see if any of them are valid examples of this as well.")
    heuristic.set_prop('abbrev', "Examples from generalization examples")

    def check_task_relevance(context: Dict[str, Any]) -> bool:
        """Verify task is for finding examples."""
        task = context.get('task')
        unit = context.get('unit')
        
        if not task or not unit:
            return False
            
        if task.get('task_type') != 'find_examples':
            return False
            
        # Need definition to validate examples
        definition = unit.get_prop('definition')
        if not definition:
            return False
            
        context['definition'] = definition
        return True

    def get_examples_from_generalizations(
        unit: Any,
        registry: Any
    ) -> List[Dict[str, Any]]:
        """Get examples from unit's generalizations."""
        candidate_examples = []
        generalizations = unit.get_prop('generalizations', [])
        
        for gen_name in generalizations:
            gen = registry.unit_registry.get_unit(gen_name)
            if not gen:
                continue
                
            examples = gen.get_prop('examples', [])
            if examples:
                for example in examples:
                    candidate_examples.append({
                        'value': example,
                        'source': gen_name
                    })
                    
        return candidate_examples

    def compute_action(context: Dict[str, Any]) -> bool:
        """Find and validate examples from generalizations."""
        unit = context.get('unit')
        definition = context.get('definition')
        registry = context.get('registry')
        
        if not all([unit, definition, registry]):
            return False

        # Get candidate examples
        candidates = get_examples_from_generalizations(unit, registry)
        if not candidates:
            return False

        # Track valid examples
        current_examples = set(unit.get_prop('examples', []))
        new_examples = []

        # Validate candidates
        for candidate in candidates:
            value = candidate['value']
            if value not in current_examples:
                try:
                    if definition(value):
                        new_examples.append({
                            'value': value,
                            'from_unit': candidate['source']
                        })
                except Exception as e:
                    logger.debug(
                        f"Failed to validate {value} from "
                        f"{candidate['source']}: {e}"
                    )

        if new_examples:
            context['task_results'] = context.get('task_results', {})
            context['task_results']['new_values'] = [
                example['value'] for example in new_examples
            ]
            return True

        return False

    def print_to_user(context: Dict[str, Any]) -> bool:
        """Report on examples found."""
        unit = context.get('unit')
        task_results = context.get('task_results', {})
        
        if not unit or not task_results:
            return False
        
        new_examples = task_results.get('new_values', [])
        if not new_examples:
            return False

        logger.info(
            f"\nFound {len(new_examples)} valid examples for {unit.name} "
            f"from generalizations"
        )
        
        return True

    # Configure heuristic slots
    heuristic.set_prop('if_potentially_relevant', check_task_relevance)
    heuristic.set_prop('then_compute', compute_action)
    heuristic.set_prop('then_print_to_user', print_to_user)