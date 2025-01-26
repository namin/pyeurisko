"""Task factory for creating well-formed tasks."""
from typing import Any, Dict, List, Optional
from .tasks import Task

def create_task(
    priority: int,
    unit_name: str,
    slot_name: str,
    reasons: List[str],
    supplemental: Optional[Dict[str, Any]] = None,
    task_type: Optional[str] = None
) -> Task:
    """Create a new task with proper structure."""
    if supplemental is None:
        supplemental = {}
    
    if task_type:
        supplemental['task_type'] = task_type
        
    return Task(
        priority=priority,
        unit_name=unit_name,
        slot_name=slot_name,
        reasons=reasons,
        supplemental=supplemental
    )