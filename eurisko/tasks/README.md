# Task Management System

The task system coordinates Eurisko's learning activities by managing an agenda of tasks created and processed by heuristics.

## Core Components

### Task Structure
```python
{
    'priority': int,      # Execution priority
    'unit': str,         # Target unit name
    'slot': str,         # Relevant slot
    'reasons': List[str], # Explanation of task creation
    'supplemental': Dict  # Additional task-specific data
}
```

### Task Manager
Maintains the task agenda and handles:
- Task prioritization
- Task scheduling
- Result tracking
- Resource management

## Task Types

1. Analysis Tasks
   - Examine unit properties
   - Analyze relationships
   - Evaluate worth

2. Creation Tasks
   - Define new concepts
   - Create specializations/generalizations
   - Form conjectures

3. Modification Tasks
   - Modify existing units
   - Update relationships
   - Adjust worth values

## Integration with Heuristics

Heuristics interact with tasks through:
- Task creation (`then_add_to_agenda`)
- Task completion checking (`if_working_on_task`)
- Result recording (`task_results`)

See the [Heuristics System](../heuristics/README.md) for details on how heuristics create and process tasks.
