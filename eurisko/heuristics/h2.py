"""H2 heuristic implementation: Kill concepts that produce garbage."""
from typing import Any, Dict
from ..unit import Unit

def setup_h2(heuristic) -> None:
    """Configure H2: Kill concepts that produce garbage."""
    def check_task(context: Dict[str, Any]) -> bool:
        """Check for new units from garbage producers."""
        task_results = context.get('task_results', {})
        if not task_results:
            return False
            
        new_units = task_results.get('new_units', [])
        if not new_units:
            return False
            
        for unit in new_units:
            if not isinstance(unit, Unit):
                continue
                
            creditors = unit.get_prop('creditors') or []
            for creditor in creditors:
                creditor_unit = heuristic.unit_registry.get_unit(creditor)
                if not creditor_unit:
                    continue
                    
                applics = creditor_unit.get_prop('applics') or []
                if len(applics) >= 10:
                    # Check if all results lack applications
                    if all(isinstance(app, dict) and
                          all(not hasattr(u, 'get_prop') or not u.get_prop('applics')
                              for u in app.get('result', []))
                          for app in applics):
                        return True
                        
        return False
        
    def reduce_worth(context: Dict[str, Any]) -> bool:
        """Reduce worth of garbage-producing units."""
        task_results = context.get('task_results', {})
        new_units = task_results.get('new_units', [])
        
        reduced = False
        for unit in new_units:
            if isinstance(unit, Unit):
                for creditor in unit.get_prop('creditors') or []:
                    creditor_unit = heuristic.unit_registry.get_unit(creditor)
                    if creditor_unit:
                        current_worth = creditor_unit.worth_value()
                        creditor_unit.set_prop('worth', current_worth // 2)
                        reduced = True
                        
        return reduced

    heuristic.set_prop('if_finished_working_on_task', check_task)
    heuristic.set_prop('then_compute', reduce_worth)