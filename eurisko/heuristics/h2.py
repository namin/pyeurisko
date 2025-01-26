"""H2 heuristic implementation: Kill concepts that produce garbage."""
from typing import Any, Dict, List
from ..unit import Unit
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

    def check_task(context: Dict[str, Any]) -> bool:
        """Check for new units from garbage producers."""
        task_results = context.get('task_results', {})
        if not task_results:
            return False
            
        new_units = task_results.get('new_units', [])
        if not new_units:
            return False

        # Find potential culprits (creditors that generate garbage)
        potential_culprits = set()
        for unit in new_units:
            if not isinstance(unit, Unit):
                continue
                
            creditors = unit.get_prop('creditors') or []
            for creditor in creditors:
                creditor_unit = heuristic.unit_registry.get_unit(creditor)
                if not creditor_unit:
                    continue
                    
                applications = creditor_unit.get_prop('applications') or []
                if len(applications) >= 10:
                    # Check if all results lack applications
                    if all(isinstance(app, dict) and
                          all(not hasattr(u, 'get_prop') or not u.get_prop('applications')
                              for u in app.get('result', []))
                          for app in applications):
                        potential_culprits.add(creditor)

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

    def reduce_worth(context: Dict[str, Any]) -> bool:
        """Severely punish garbage-producing units."""
        culprits = context.get('culprits', [])
        if not culprits:
            return False
            
        for creditor in culprits:
            creditor_unit = heuristic.unit_registry.get_unit(creditor)
            if creditor_unit:
                # Severe punishment - reduce worth significantly
                current_worth = creditor_unit.worth_value()
                new_worth = max(50, current_worth // 4)  # Prevent worth from going too low
                creditor_unit.set_prop('worth', new_worth)
                
        # Record the punishment in task results
        context['task_results']['punished_units'] = (
            culprits, "because they've led to so many questionable units being created!"
        )
        return True

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
