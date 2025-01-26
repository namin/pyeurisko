"""H2 heuristic implementation: Kill concepts that produce garbage."""
from typing import Any, Dict, List
from ..units import Unit
import logging

logger = logging.getLogger(__name__)

def setup_h2(heuristic) -> None:
    """Configure H2: Kill concepts that produce garbage."""
    # Set properties from original LISP implementation
    heuristic.set_prop('worth', 700)
    heuristic.set_prop('english', 
        "IF you have just finished a task, and some units were created, and one of "
        "the creators has the property of spewing garbage, THEN stuff that spewer")
    heuristic.set_prop('abbrev', "Kill a concept that leads to lots of garbage")
    heuristic.set_prop('arity', 1)

    def check_task(rule, context):
        """Check if this is the end of a task that created units."""
        task_results = context.get('task_results', {})
        if not task_results:
            return False
            
        # Check for new units created by slot function
        new_units = task_results.get('new_units', [])
        if not new_units:
            return False
            
        # Find potential culprits (creditors that generate garbage)
        potential_culprits = set()
        unit = context['unit']
        
        # Check if the current unit creates mostly garbage
        applications = unit.get_prop('applications', [])
        if len(applications) >= 10:
            # Look at success rate and worth of results
            poor_results = sum(1 for app in applications
                              if not app.get('success', True) or app.get('worth', 0) < 300)
            if poor_results > len(applications) * 0.7:  # Over 70% poor results
                potential_culprits.add(unit.name)
                
        context['culprits'] = list(potential_culprits)
        return bool(potential_culprits)

    def print_to_user(context: Dict[str, Any]) -> bool:
        """Print explanation of punitive actions."""
        culprits = context.get('culprits', [])
        deleted = context.get('deleted_units', [])
        
        if culprits:
            logger.info(f"\n{len(culprits)} units were reduced in Worth, due to "
                       f"excessive generation of mediocre concepts; namely: {culprits}")
            
        if deleted:
            logger.info(f"\n{len(deleted)} had Worths that were now so low, the whole "
                       f"concept was obliterated; namely: {deleted}")
            
        return bool(culprits or deleted)

    def reduce_worth(rule, context):
        """Punish units that generate garbage."""
        unit = context['current_unit']
        applications = unit.get_prop('applications', [])
        if len(applications) >= 10:
            # Check quality of results
            poor_results = sum(1 for app in applications 
                             if not app['success'] or app['worth'] < 300)
            if poor_results > len(applications) * 0.7:  # Mostly poor results
                unit.set_worth(unit.worth // 2)  # Severe punishment
                return True
        return False

    def delete_old_concepts(context: Dict[str, Any]) -> bool:
        """Delete units whose worth has fallen too low."""
        culprits = context.get('culprits', [])
        if not culprits:
            return False
            
        deleted_units = []
        for creditor in culprits:
            creditor_unit = heuristic.unit_registry.get_unit(creditor)
            if creditor_unit and creditor_unit.worth_value() <= 175:
                # Apply any hindsight rules before deletion
                if hasattr(heuristic, 'apply_hindsight_rules'):
                    heuristic.apply_hindsight_rules(creditor_unit)
                    
                # Delete the unit
                heuristic.unit_registry.delete_unit(creditor)
                deleted_units.append(creditor)
                
        if deleted_units:
            context['deleted_units'] = deleted_units
            context['task_results']['deleted_units'] = (
                deleted_units, "because their Worth has fallen so low"
            )
            
        return bool(deleted_units)

    # Set up all the slots
    heuristic.set_prop('if_finished_working_on_task', check_task)
    heuristic.set_prop('then_print_to_user', print_to_user)
    heuristic.set_prop('then_compute', reduce_worth)
    heuristic.set_prop('then_delete_old_concepts', delete_old_concepts)
