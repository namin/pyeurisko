"""H4 heuristic implementation: Gather data about newly synthesized units."""
import logging
from ..heuristics import rule_factory

logger = logging.getLogger(__name__)

def setup_h4(heuristic):
    """Configure H4: Trigger empirical data gathering for new units."""
    heuristic.set_prop('worth', 703)
    heuristic.set_prop('english',
        "IF a new unit has been synthesized, THEN place a task on the Agenda "
        "to gather new empirical data about it")
    heuristic.set_prop('abbrev', "about concepts gather data new empirical")
    heuristic.set_prop('arity', 1)

    # Add record functions that return True
    def then_add_to_agenda_record(rule, context):
        return True
    heuristic.set_prop('then_add_to_agenda_record', then_add_to_agenda_record)

    @rule_factory 
    def if_potentially_relevant(rule, context):
        """Check for new units."""
        task_results = context.get('task_results', {})
        new_units = task_results.get('new_units', [])
        return bool(new_units)

    @rule_factory
    def then_add_to_agenda(rule, context):
        """Add tasks to gather data about units."""
        task_results = context.get('task_results', {})
        new_units = task_results.get('new_units', [])
        task_manager = rule.task_manager
        
        if not new_units or not task_manager:
            return False

        tasks_added = 0
        for unit in new_units:
            # Get appropriate slot based on unit type
            slot = 'applics' if 'op' in unit.get_prop('isa', []) else 'examples'
                
            # Create task
            new_task = {
                'priority': min(800, int(rule.worth_value() * 1.1)),
                'unit': unit.name,
                'slot': slot,
                'task_type': 'find_instances',
                'reasons': [f"Gathering data about new unit {unit.name}"],
                'supplemental': {
                    'credit_to': ['h4']
                }
            }
            task_manager.add_task(new_task)
            tasks_added += 1

        # Update results
        context['task_results'] = {
            'status': 'completed',
            'success': True,
            'new_tasks': [f"Added {tasks_added} data gathering tasks"]
        }
        return True