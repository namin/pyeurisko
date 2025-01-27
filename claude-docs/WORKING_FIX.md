# Debugging Progress

## Task Access Pattern Issues
1. Different ways of accessing task type:
   - Direct attribute: task.task_type
   - Dict access: task.get('task_type')
   - Supplemental dict: task.supplemental.get('task_type')

2. Data Flow Problems:
   - Task context not properly passed between heuristics
   - Task results not propagating to task manager
   - Task type not consistently set across all code paths

## Current Fixes
1. Standardized task access:
   - Using task.get() interface everywhere
   - Moving supplemental data to task properties
   - Added logging to track task context flow

2. Next Steps:
   - Verify task type flow from task creation to heuristic execution
   - Fix task results propagation in task_manager.py
   - Update h6 to properly consume h5's output

# Original Issues
## Current Issues
1. TaskManager issues:
   - Not handling task context properly - splits task info across 'task_type' and 'supplemental'  
   - Requires both if_potentially_relevant and if_truly_relevant to pass
   - Not tracking successful heuristic executions correctly

## Next Steps
1. Fix TaskManager
   - Rewrite complete task_manager.py
   - Create single cohesive task context
   - Only require if_potentially_relevant to pass

2. Update heuristic relevance checks
   - h4: Only relevant when new units added 
   - h5: Only relevant for specialization tasks without chosen slot
   - h6: Only relevant for specialization tasks with chosen slot
   - Add detailed logging of context

3. Fix task completion tracking
   - Add success and failure counters in TaskManager
   - Update task completion status consistently
   - Track which heuristics actually modified state

4. Test Plan
   - Test each heuristic individually
   - Verify specialization chain: h5 -> h6 -> h4
   - Log all context and state changes

## Key Data Structure Changes
```python
# New task context structure
context = {
    'unit': unit,
    'task': {
        'type': task.task_type,
        'supplemental': task.supplemental,
        'slot': task.slot_name,
        'results': {
            'status': str,
            'success': bool,
            'new_units': [],
            'modified_units': []
        }
    }
}
```