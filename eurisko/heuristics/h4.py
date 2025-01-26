"""H4 heuristic implementation: Gather data about new units."""
from typing import Any, Dict
import logging
from ..heuristics import rule_factory

logger = logging.getLogger(__name__)

def setup_h4(heuristic) -> None:
    """Configure H4: Gather data about new units."""
    # Basic properties
    heuristic.set_prop('worth', 703)
    heuristic.set_prop('english', 
        "IF a new unit has been synthesized, THEN place a task on the Agenda to "
        "gather new empirical data about it")
    heuristic.set_prop('abbrev', "Gather empirical data about new concepts")
    heuristic.set_prop('arity', 1)
    
    # Record functions for tracking success/failure
    def record_func(rule, context):
        return True
    heuristic.set_prop('then_compute_record', record_func)
    heuristic.set_prop('then_define_new_concepts_record', record_func)
    heuristic.set_prop('then_print_to_user_record', record_func)
    heuristic.set_prop('overall_record', record_func)

    @rule_factory 
    def if_working_on_task(rule, context):
        """Check for new units during task execution."""
        # Get current unit and task type
        task_type = context.get('task_type')
        task_results = context.get('task_results', {})
        
        logger.debug(f"H4 checking task_type: {task_type}")
        logger.debug(f"H4 checking task_results: {task_results}")
        
        # Skip data gathering tasks to prevent recursion
        if task_type == 'data_gathering':
            logger.debug("H4: Skipping data gathering task")
            return False
            
        # Get any new units from task results
        new_units = task_results.get('new_units', [])
        logger.debug(f"H4: Found new_units: {new_units}")
        
        # Validate units have required name attribute
        valid_units = []
        for unit in new_units:
            if hasattr(unit, 'name'):
                valid_units.append(unit)
                logger.debug(f"H4: Added valid unit: {unit.name}")
        
        # Store valid units in context
        context['valid_units'] = valid_units
        return bool(valid_units)

    @rule_factory
    def then_print_to_user(rule, context):
        """Print information about data gathering tasks."""
        valid_units = context.get('valid_units', [])
        if not valid_units:
            return False
            
        unit_names = [u.name for u in valid_units]
        logger.info(
            f"\n{len(valid_units)} new units (namely: {unit_names}) were defined. "
            f"New tasks are being added to the agenda to gather empirical data."
        )
        return True

    @rule_factory
    def then_add_to_agenda(rule, context):
        """Create data gathering tasks for new units."""
        valid_units = context.get('valid_units', [])
        task_manager = rule.task_manager
        
        if not all([valid_units, task_manager]):
            logger.debug("H4: Missing valid_units or task_manager")
            return False
            
        # Track new tasks created
        new_task_count = 0
        
        for unit in valid_units:
            # Always use 'examples' slot for gathering instances
            instance_slot = 'examples'
                
            # Calculate priority based on unit and rule worth
            priority = int((unit.worth_value() + rule.worth_value()) / 2)
            
            # Create data gathering task
            task = {
                'priority': priority,
                'unit': unit.name,
                'slot': instance_slot,
                'reasons': [
                    f"Gathering empirical data about {unit.name} after synthesis"
                ],
                'task_type': 'data_gathering',
                'supplemental': {
                    'credit_to': ['h4']
                }
            }
            task_manager.add_task(task)
            new_task_count += 1
            logger.debug(f"H4: Created task for unit {unit.name}")
            
        # Update task results with count of new tasks
        task_results = context.get('task_results', {})
        task_results['new_tasks'] = [
            f"{new_task_count} new units requiring instance data collection"
        ]
        context['task_results'] = task_results
        
        return True