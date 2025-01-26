"""H2 heuristic implementation: Kill concepts that produce garbage."""
from typing import Any, Dict
import logging
from ..heuristics import rule_factory

logger = logging.getLogger(__name__)

def setup_h2(heuristic) -> None:
    """Configure H2: Kill concepts that produce garbage."""
    heuristic.set_prop('worth', 700)
    heuristic.set_prop('abbrev', "Kill concepts that produce garbage")
    heuristic.set_prop('arity', 1)
    
    @rule_factory
    def if_finished_working_on_task(rule, context):
        """Check if this is the end of a task that created units."""
        task_results = context.get('task_results', {})
        if 'new_units' not in task_results:
            return False
            
        new_units = task_results['new_units']
        if not new_units:
            return False
            
        # Find units that are producing garbage
        doomed_units = []
        for unit in new_units:
            if not unit:
                continue
            applications = unit.get_prop('applics', [])
            if len(applications) < 10:
                continue
                
            # Check if all applications produce concepts with no valid applications
            all_garbage = True
            for app in applications:
                if not isinstance(app[1], list):
                    all_garbage = False
                    break
                for result in app[1]:
                    if result and result.get_prop('applics'):
                        all_garbage = False
                        break
            if all_garbage:
                doomed_units.append(unit)
                
        context['killed_units'] = doomed_units
        return bool(doomed_units)

    @rule_factory
    def then_print_to_user(rule, context):
        """Print message about killed units."""
        units = context.get('killed_units', [])
        if not units:
            return False
            
        logger.info(f"Killed {len(units)} garbage units")
        return True