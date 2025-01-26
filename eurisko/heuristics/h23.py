"""H23 heuristic implementation: Perform interestingness evaluation."""
from typing import Any, Dict, List, Set, Tuple
from ..units import Unit
import logging
import math
from ..heuristics import rule_factory

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
        """Evaluate an instance against interestingness criteria."""
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

    @rule_factory
    def if_working_on_task(rule, context):
        """Verify task is about finding interesting instances."""
        task = context.get('task')
        if not task:
            return False
            
        # Check if this task came from H22
        supplemental = task.get('supplemental', {})
        if 'h22' not in supplemental.get('credit_to', []):
            return False
            
        # Verify we have evaluation criteria
        criteria = supplemental.get('criteria')
        if not criteria:
            return False
            
        # Verify source instances exist
        source_slot = supplemental.get('source_slot')
        if not source_slot:
            return False
            
        context['source_slot'] = source_slot
        context['criteria'] = criteria
        context['target_slot'] = task.get('slot', 'int_examples')
        return True

    @rule_factory
    def then_compute(rule, context):
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
                interesting.append({
                    'instance': instance,
                    'score': score,
                    'reasons': matched_criteria
                })
                
        if interesting:
            # Sort by score
            interesting.sort(key=lambda x: x['score'], reverse=True)
            context['interesting_instances'] = interesting
            return True
            
        return False

    @rule_factory
    def then_print_to_user(rule, context):
        """Report on interesting instances found."""
        unit = context.get('unit')
        interesting = context.get('interesting_instances', [])
        
        if not unit or not interesting:
            return False
            
        logger.info(f"\nFound {len(interesting)} interesting instances of {unit.name}:")
        
        for item in interesting:
            logger.info(
                f"\n- Score {item['score']:.2f}: {item['instance']}"
                f"\n  Interesting because: {', '.join(item['reasons'])}"
            )
        return True

    @rule_factory
    def then_define_new_concepts(rule, context):
        """Record discovered interesting instances."""
        unit = context.get('unit')
        target_slot = context.get('target_slot')
        interesting = context.get('interesting_instances')
        
        if not all([unit, target_slot, interesting]):
            return False
            
        # Track instances and their evaluations
        instances_added = []
        for item in interesting:
            instance = item['instance']
            
            # Add to target collection
            unit.add_to_prop(target_slot, instance)
            instances_added.append(instance)
            
            # Record evaluation details
            unit.add_to_prop(
                f'{target_slot}_reasons',
                {
                    'instance': instance,
                    'score': item['score'],
                    'reasons': item['reasons'],
                    'discovered_by': 'h23'
                }
            )
            
        if instances_added:
            context['task_results'] = {
                'new_values': instances_added
            }
            return True
            
        return False