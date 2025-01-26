"""H22 heuristic implementation: Evaluate instance interestingness."""
from typing import Any, Dict, List, Optional
from ..units import Unit
import logging
from ..heuristics import rule_factory

logger = logging.getLogger(__name__)

def setup_h22(heuristic) -> None:
    """Configure H22: Assess interestingness of discovered instances.
    
    This heuristic examines newly discovered instances of concepts to identify
    those that are particularly interesting or noteworthy. It helps guide
    the system's exploration toward promising areas by identifying instances
    that merit further investigation.
    """
    heuristic.set_prop('worth', 500)
    heuristic.set_prop('english',
        "IF instances of a unit have been found, THEN evaluate which ones are "
        "unusually interesting to guide further exploration.")
    heuristic.set_prop('abbrev', "Check instances for interesting cases")
    
    # Initialize record keeping
    heuristic.set_prop('then_add_to_agenda_record', (14, 1))
    heuristic.set_prop('then_print_to_user_record', (38, 1))
    heuristic.set_prop('overall_record', (75, 1))
    heuristic.set_prop('arity', 1)

    def get_interestingness_criteria(unit: Unit) -> List[Dict[str, Any]]:
        """Get criteria for evaluating instance interestingness."""
        base_criteria = [
            {
                'test': lambda x: len(str(x)) > 100,
                'weight': 0.3,
                'description': "Unusually complex structure"
            },
            {
                'test': lambda x: bool(getattr(x, 'worth', 0) > 700),
                'weight': 0.4,
                'description': "High worth"
            }
        ]
        
        # Add any unit-specific criteria
        custom_criteria = unit.get_prop('interestingness', [])
        if custom_criteria:
            base_criteria.extend(custom_criteria)
            
        return base_criteria

    @rule_factory
    def if_finished_working_on_task(rule, context):
        """Check if we've just found new instances that need evaluation."""
        unit = context.get('unit')
        task = context.get('task')
        if not unit or not task:
            return False
            
        # Determine appropriate instance slot
        instance_types = unit.get_prop('instances', ['examples'])
        if not instance_types:
            return False
            
        # Get most specific instance type with content
        instance_slot = None
        for slot in instance_types:
            if unit.get_prop(slot):
                instance_slot = slot
                break
                
        if not instance_slot:
            instance_slot = instance_types[0]
            
        context['instance_slot'] = instance_slot
        
        # Get interestingness criteria
        criteria = get_interestingness_criteria(unit)
        if not criteria:
            return False
            
        context['criteria'] = criteria
        
        # Verify we have new instances to evaluate
        new_values = context.get('task_results', {}).get('new_values')
        return bool(new_values)

    @rule_factory
    def then_print_to_user(rule, context):
        """Report plan to evaluate instance interestingness."""
        unit = context.get('unit')
        instance_slot = context.get('instance_slot')
        criteria = context.get('criteria', [])
        
        if not all([unit, instance_slot]):
            return False
            
        num_instances = len(unit.get_prop(instance_slot, []))
        
        logger.info(
            f"\nWill evaluate the interestingness of {num_instances} instances "
            f"of {unit.name} using {len(criteria)} criteria:"
        )
        
        for criterion in criteria:
            logger.info(f"- {criterion['description']} (weight: {criterion['weight']})")
        
        return True

    @rule_factory
    def then_add_to_agenda(rule, context):
        """Add task to evaluate instance interestingness."""
        unit = context.get('unit')
        instance_slot = context.get('instance_slot')
        criteria = context.get('criteria', [])
        
        if not all([unit, instance_slot, criteria]):
            return False
            
        # Determine target slot for interesting instances
        slot_ranking = {
            'examples': 1,
            'int_examples': 2,
            'very_int_examples': 3
        }
        
        available_slots = [
            instance_slot,
            'int_examples',
            'very_int_examples'
        ]
        
        target_slot = max(available_slots, key=lambda s: slot_ranking.get(s, 0))
        
        if target_slot == instance_slot:
            return False
            
        task = {
            'priority': unit.get_prop('worth', 500),
            'unit': unit.name,
            'slot': target_slot,
            'reasons': [
                f"Evaluate which instances of {unit.name} are particularly "
                f"interesting to guide further exploration"
            ],
            'supplemental': {
                'credit_to': ['h22'],
                'source_slot': instance_slot,
                'criteria': criteria
            }
        }
        
        if not rule.task_manager.add_task(task):
            return False
            
        context['task_results'] = {
            'new_tasks': f"Will evaluate interestingness of {unit.name} instances"
        }
        return True