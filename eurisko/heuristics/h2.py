"""H2 heuristic implementation: Kill concepts that produce garbage."""
from typing import Any, Dict
import logging
from ..heuristics import rule_factory

logger = logging.getLogger(__name__)

def setup_h2(heuristic) -> None:
    """Configure H2: Kill concepts that produce garbage."""
    # Set basic properties
    heuristic.set_prop('worth', 700)
    heuristic.set_prop('english', 
        "IF you have just finished a task, and some units were created, and one "
        "of the creators has the property of spewing garbage, THEN stuff that spewer")
    heuristic.set_prop('abbrev', "Kill a concept that leads to lots of garbage")
    heuristic.set_prop('arity', 1)
    
    # Initialize record properties as functions
    def record_func(rule, context):
        return True
    heuristic.set_prop('then_compute_record', record_func)
    heuristic.set_prop('then_delete_old_concepts_record', record_func)
    heuristic.set_prop('then_print_to_user_record', record_func)
    heuristic.set_prop('overall_record', record_func)

    @rule_factory
    def if_finished_working_on_task(rule, context):
        """Check if this is the end of a task that created garbage units."""
        task_results = context.get('task_results', {})
        new_units = task_results.get('new_units', [])
        if not new_units:
            return False
            
        # Find units that are producing garbage
        doomed_units = []
        for unit in new_units:
            if not unit:
                continue
                
            # Check if unit has sufficient applications
            applications = unit.get_prop('applications', [])
            if len(applications) < 10:
                continue
                
            # Check if all applications produce concepts with no valid applications
            all_garbage = True
            for app in applications:
                if not isinstance(app, dict):
                    all_garbage = False
                    break
                    
                results = app.get('results', [])
                if not isinstance(results, list):
                    all_garbage = False
                    break
                    
                for result in results:
                    # Check if result has any valid applications
                    if result and result.get_prop('applications'):
                        all_garbage = False
                        break
                        
            if all_garbage:
                doomed_units.append(unit)
                
        context['doomed_units'] = doomed_units
        return bool(doomed_units)

    @rule_factory 
    def then_compute(rule, context):
        """Update the task results and worth of the doomed units."""
        doomed_units = context.get('doomed_units', [])
        if not doomed_units:
            return False
            
        # Punish the doomed units severely
        for unit in doomed_units:
            current_worth = unit.get_prop('worth', 0)
            unit.set_prop('worth', max(0, current_worth - 100))
            
        # Update task results
        task_results = context.get('task_results', {})
        task_results['punished_units'] = {
            'units': doomed_units,
            'reason': "because they've led to so many questionable units being created!"
        }
        context['task_results'] = task_results
        return True

    @rule_factory
    def then_delete_old_concepts(rule, context):
        """Delete units whose worth has dropped too low."""
        doomed_units = context.get('doomed_units', [])
        if not doomed_units:
            return False
            
        deleted = []
        for unit in doomed_units:
            if unit.get_prop('worth', 0) <= 175:
                deleted.append(unit)
                system = rule.unit_registry
                system.delete_unit(unit.name)
                
        if deleted:
            task_results = context.get('task_results', {})
            task_results['deleted_units'] = {
                'units': deleted,
                'reason': "because their Worth has fallen so low"
            }
            context['task_results'] = task_results
            
        return True

    @rule_factory
    def then_print_to_user(rule, context):
        """Print message about killed units."""
        doomed_units = context.get('doomed_units', [])
        if not doomed_units:
            return False
            
        names = [u.name for u in doomed_units]
        logger.info(f"{len(doomed_units)} units were reduced in Worth, due to "
                   f"excessive generation of mediocre concepts by them; namely: {names}")
        
        deleted = context.get('task_results', {}).get('deleted_units', {}).get('units', [])
        if deleted:
            deleted_names = [u.name for u in deleted]
            logger.info(f"{len(deleted)} had Worths that were now so low, the whole concept "
                       f"was obliterated; namely: {deleted_names}")
            
        return True