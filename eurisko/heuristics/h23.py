"""H23 heuristic implementation: Perform interestingness evaluation."""
from typing import Any, Dict, List, Set, Tuple
from ..units import Unit
import logging
import math

logger = logging.getLogger(__name__)

def setup_h23(heuristic) -> None:
    """Configure H23: Evaluate instance interestingness.
    
    This heuristic works in conjunction with H22 to actually perform the
    evaluation of instance interestingness. It applies the criteria identified
    by H22 and maintains a record of particularly interesting instances.
    """
    heuristic.set_prop('worth', 700)
    heuristic.set_prop('english',
        "IF the current task is to find interesting examples of a unit, and "
        "it has some known examples already, THEN evaluate those examples "
        "against interestingness criteria.")
    heuristic.set_prop('abbrev', "Evaluate instance interestingness")
    
    # Initialize record keeping
    heuristic.set_prop('arity', 1)

    def evaluate_instance(
        instance: Any,
        criteria: List[Dict[str, Any]]
    ) -> Tuple[float, List[str]]:
        """Evaluate an instance against interestingness criteria.
        
        Returns:
            Tuple of (score, matching_criteria) where:
            - score: Float from 0-1 indicating overall interestingness
            - matching_criteria: List of descriptions of matched criteria
        """
        total_weight = sum(c['weight'] for c in criteria)
        if total_weight == 0:
            return 0.0, []
            
        score = 0.0
        matched = []
        
        for criterion in criteria:
            try:
                if criterion['test'](instance):
                    score += criterion['weight']
                    matched.append(criterion['description'])
            except Exception as e:
                logger.debug(
                    f"Failed to evaluate criterion: {criterion['description']}, "
                    f"error: {e}"
                )
                
        return score / total_weight, matched

    def check_task_relevance(context: Dict[str, Any]) -> bool:
        """Verify task is about finding interesting instances."""
        task = context.get('task')
        if not task:
            return False
            
        # Check if this task came from H22
        if 'h22' not in task.get('supplemental', {}).get('credit_to', []):
            return False
            
        # Verify we have evaluation criteria
        criteria = task.get('supplemental', {}).get('criteria')
        if not criteria:
            return False
            
        # Verify source instances exist
        source_slot = task.get('supplemental', {}).get('source_slot')
        if not source_slot:
            return False
            
        context['source_slot'] = source_slot
        context['criteria'] = criteria
        return True

    def print_to_user(context: Dict[str, Any]) -> bool:
        """Report on interesting instances found."""
        unit = context.get('unit')
        interesting = context.get('interesting_instances', [])
        
        if not unit or not interesting:
            return False
            
        logger.info(f"\nFound {len(interesting)} interesting instances of {unit.name}:")
        
        for instance, score, reasons in interesting:
            logger.info(
                f"\n- Score {score:.2f}: {instance}"
                f"\n  Interesting because: {', '.join(reasons)}"
            )
        return True

    def compute_action(context: Dict[str, Any]) -> bool:
        """Evaluate instances against interestingness criteria."""
        unit = context.get('unit')
        source_slot = context.get('source_slot')
        criteria = context.get('criteria')
        
        if not all([unit, source_slot, criteria]):
            return False
            
        instances = unit.get_prop(source_slot, [])
        if not instances:
            return False
            
        interesting = []
        for instance in instances:
            score, matched_criteria = evaluate_instance(instance, criteria)
            
            # Consider instances above 0.4 interestingness score
            if score > 0.4:
                interesting.append((instance, score, matched_criteria))
                
        context['interesting_instances'] = sorted(
            interesting,
            key=lambda x: x[1],
            reverse=True
        )
        return bool(interesting)

    def record_interesting_instances(context: Dict[str, Any]) -> bool:
        """Record discovered interesting instances."""
        unit = context.get('unit')
        task = context.get('task')
        interesting = context.get('interesting_instances')
        
        if not all([unit, task, interesting]):
            return False
            
        # Get target slot for recording interesting instances
        target_slot = task.get('slot', 'int_examples')
        
        # Record interesting instances
        for instance, score, reasons in interesting:
            # Add to appropriate collection
            unit.add_to_prop(target_slot, instance)
            
            # Record why it's interesting
            unit.add_to_prop(
                f'{target_slot}_reasons',
                {
                    'instance': instance,
                    'score': score,
                    'reasons': reasons,
                    'discovered_by': 'h23'
                }
            )
            
        # Update task results
        context['system'].add_task_result(
            'new_values',
            [i[0] for i in interesting]
        )
        return True

    # Configure heuristic slots
    heuristic.set_prop('if_working_on_task', check_task_relevance)
    heuristic.set_prop('then_compute', compute_action)
    heuristic.set_prop('then_print_to_user', print_to_user)
    heuristic.set_prop('then_define_new_concepts', record_interesting_instances)
