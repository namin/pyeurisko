"""H4 heuristic implementation: Gather data about new units."""
from typing import Any, Dict
from ..unit import Unit

def setup_h4(heuristic) -> None:
    """Configure H4: Gather data about new units."""
    def check_task(context: Dict[str, Any]) -> bool:
        """Check for new units created."""
        task_results = context.get('task_results', {})
        new_units = task_results.get('new_units', [])
        return bool(new_units and isinstance(new_units, list))

    def schedule_analysis(context: Dict[str, Any]) -> bool:
        """Schedule analysis tasks for new units."""
        task_results = context.get('task_results', {})
        new_units = task_results.get('new_units', [])
        
        if not new_units:
            return False
            
        for unit in new_units:
            if isinstance(unit, Unit):
                unit.set_prop('needs_analysis', True)
        return True

    heuristic.set_prop('if_finished_working_on_task', check_task)
    heuristic.set_prop('then_compute', schedule_analysis)