"""H7 heuristic implementation: Find instances for concepts with none.

This heuristic identifies concepts that have no known instances and creates tasks to find
instances for them. It focuses on categories and operations that need empirical data.
"""

import logging
from typing import Any, Dict, Optional
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

def setup_h7(heuristic) -> None:
    """Configure H7: Find instances for concepts that have none.
    
    Sets up the heuristic with appropriate properties and rule functions.
    """
    # Set basic properties
    heuristic.set_prop('worth', 700)
    heuristic.set_prop('english', 
        "IF a concept has no known instances, THEN try to find some")
    heuristic.set_prop('abbrev', "Instantiate a concept having no known instances")
    heuristic.set_prop('arity', 1)
    
    @rule_factory
    def if_potentially_relevant(rule, context: Dict[str, Any]) -> bool:
        """Quick relevance check: unit has no instances.
        
        Args:
            rule: Rule being executed
            context: Current execution context
            
        Returns:
            bool: True if rule should be considered, False otherwise
        """
        logger.debug("H7 checking if_potentially_relevant")
        
        # Validate task
        task = context.get('task')
        if not task:
            logger.debug("H7: No task in context")
            return False
            
        # Initialize results
        task_results = init_task_results(context)
        
        # Check unit
        unit = context.get('unit')
        if not unit:
            logger.debug("H7: No unit in context")
            return False
            
        # Check instances
        instances = unit.get_prop('instances', [])
        has_no_instances = len(instances) == 0
        
        logger.debug(f"H7: Unit {unit.name} has_no_instances={has_no_instances}")
        return has_no_instances

    @rule_factory
    def if_truly_relevant(rule, context: Dict[str, Any]) -> bool:
        """Detailed relevance check: unit is category/operation.
        
        Args:
            rule: Rule being executed 
            context: Current execution context
            
        Returns:
            bool: True if rule should be applied, False otherwise
        """
        logger.debug("H7 checking if_truly_relevant")
        
        unit = context.get('unit')
        if not unit:
            logger.debug("H7: No unit for truly relevant check")
            return False
            
        # Must be category or operation
        unit_type = unit.get_prop('type', '')
        is_valid_type = unit_type in ['category', 'operation']
        
        logger.debug(f"H7: Unit {unit.name} is_valid_type={is_valid_type} (type={unit_type})")
        return is_valid_type

    @rule_factory
    def then_compute(rule, context: Dict[str, Any]) -> bool:
        """Prepare data for finding instances.
        
        Sets up context with information needed for task creation.
        
        Args:
            rule: Rule being executed
            context: Current execution context
            
        Returns:
            bool: True if preparation successful, False otherwise
        """
        logger.debug("H7 starting then_compute")
        
        unit = context.get('unit')
        if not unit:
            logger.debug("H7: No unit in context")
            return False
            
        # Initialize task results
        task_results = init_task_results(context)
        
        # Get instance type
        instance_type = unit.get_prop('instance_type', 'instances')
        context['instance_type'] = instance_type
        
        logger.debug(f"H7: Prepared for {unit.name} with instance_type={instance_type}")
        return True

    @rule_factory
    def then_add_to_agenda(rule, context: Dict[str, Any]) -> bool:
        """Add task to find instances of the unit.
        
        Creates a new task and adds it to the agenda via task manager.
        
        Args:
            rule: Rule being executed
            context: Current execution context
            
        Returns:
            bool: True if task added successfully, False otherwise
        """
        logger.debug("H7 starting then_add_to_agenda")
        
        unit = context.get('unit')
        instance_type = context.get('instance_type')
        if not unit or not instance_type:
            logger.debug("H7: Missing unit or instance_type")
            return False
            
        task_manager = context.get('task_manager')
        if not task_manager:
            logger.debug("H7: No task manager available")
            return False
            
        # Create new task
        task = {
            'priority': unit.get_prop('worth', 500),
            'unit': unit,
            'slot': instance_type,
            'task_type': 'find_instances',  # Explicit task type
            'reasons': [
                f"To properly study {unit.name} we must gather empirical data "
                "about instances of that concept"
            ],
            'supplemental': {
                'credit_to': ['h7'],
                'instance_type': instance_type
            }
        }
        
        # Add task and update results
        success = task_manager.add_task(task)
        if success:
            logger.debug(f"H7: Added task to find instances for {unit.name}")
            task_results = init_task_results(context)
            task_results['status'] = 'completed'
            task_results['success'] = True
            task_results['new_tasks'].append("1 unit must be instantiated")
            return True
        else:
            logger.debug(f"H7: Failed to add task for {unit.name}")
            return False

    @rule_factory
    def then_print_to_user(rule, context: Dict[str, Any]) -> bool:
        """Print explanation of action.
        
        Logs information about the instance finding task.
        
        Args:
            rule: Rule being executed
            context: Current execution context
            
        Returns:
            bool: True if message printed successfully, False otherwise
        """
        unit = context.get('unit')
        if not unit:
            logger.debug("H7: No unit for print")
            return False
            
        instance_type = context.get('instance_type', 'instances')
        message = f"\nSince {unit.name} has no known {instance_type}, it is probably worth looking for some."
        logger.info(message)
        return True

    # Register rule functions
    heuristic.set_prop('if_potentially_relevant', if_potentially_relevant)
    heuristic.set_prop('if_truly_relevant', if_truly_relevant)
    heuristic.set_prop('then_compute', then_compute)
    heuristic.set_prop('then_add_to_agenda', then_add_to_agenda)
    heuristic.set_prop('then_print_to_user', then_print_to_user)