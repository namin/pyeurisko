"""H22 heuristic implementation: Evaluate instance interestingness."""
from typing import Any, Dict, List, Optional
from ..units import Unit
import logging

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

    def get_instance_slot(unit: Unit) -> Optional[str]:
        """Determine appropriate instance slot for the unit."""
        instance_types = unit.get_prop('instances', ['examples'])
        if not instance_types:
            return None
            
        # Get most specific instance type
        for slot in instance_types:
            if unit.get_prop(slot):
                return slot
                
        return instance_types[0]

    def get_interestingness_criteria(unit: Unit) -> List[Dict[str, Any]]:
        """Get criteria for evaluating instance interestingness.
        
        Returns a list of criteria, each with:
        - test: Function to evaluate the criterion
        - weight: Relative importance (0-1)
        - description: Human-readable explanation
        """
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

    def check_task_completion(context: Dict[str, Any]) -> bool:
        """Check if we've just found new instances that need evaluation."""
        unit = context.get('unit')
        task = context.get('task')
        if not unit or not task:
            return False
            
        # Get instance slot and verify we have instances
        instance_slot = get_instance_slot(unit)
        if not instance_slot:
            return False
            
        context['instance_slot'] = instance_slot
        
        # Need interestingness criteria
        criteria = get_interestingness_criteria(unit)
        if not criteria:
            return False
            
        context['criteria'] = criteria
        
        # Check if this task found new instances
        new_values = context.get('system').get_task_result('new_values')
        return bool(new_values)

    def get_more_interesting_slot(slots: List[str]) -> Optional[str]:
        """Determine which slot represents more interesting instances."""
        slot_ranking = {
            'examples': 1,
            'int_examples': 2,
            'very_int_examples': 3
        }
        
        return max(slots, key=lambda s: slot_ranking.get(s, 0))

    def print_to_user(context: Dict[str, Any]) -> bool:
        """Report plan to evaluate instance interestingness."""
        unit = context.get('unit')
        instance_slot = context.get('instance_slot')
        num_instances = len(unit.get_prop(instance_slot, []))
        
        if not all([unit, instance_slot]):
            return False
            
        logger.info(
            f"\nWill evaluate the interestingness of {num_instances} instances "
            f"of {unit.name} using {len(context.get('criteria', []))} criteria."
        )
        return True

    def add_to_agenda(context: Dict[str, Any]) -> bool:
        """Add task to evaluate instance interestingness."""
        unit = context.get('unit')
        system = context.get('system')
        instance_slot = context.get('instance_slot')
        
        if not all([unit, system, instance_slot]):
            return False
            
        # Determine appropriate slot for more interesting instances
        target_slot = get_more_interesting_slot([
            instance_slot,
            'int_examples',
            'very_int_examples'
        ])
        
        if target_slot == instance_slot:
            return False
            
        task = {
            'priority': unit.get_prop('worth', 500),
            'unit': unit,
            'slot': target_slot,
            'reasons': [
                f"Evaluate which instances of {unit.name} are particularly "
                f"interesting to guide further exploration"
            ],
            'supplemental': {
                'credit_to': ['h22'],
                'source_slot': instance_slot,
                'criteria': context.get('criteria', [])
            }
        }
        
        system.task_manager.add_task(task)
        system.add_task_result(
            'new_tasks',
            f"Will evaluate interestingness of {unit.name} instances"
        )
        return True

    # Configure heuristic slots
    heuristic.set_prop('if_finished_working_on_task', check_task_completion)
    heuristic.set_prop('then_print_to_user', print_to_user)
    heuristic.set_prop('then_add_to_agenda', add_to_agenda)
