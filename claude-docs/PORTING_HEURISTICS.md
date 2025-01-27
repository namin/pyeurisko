# Guide to Porting Eurisko Heuristics

This document describes the process and patterns for porting heuristics from the original Lisp codebase to Python. By following these guidelines, we maintain consistency and ensure proper interaction with the Eurisko task system.

## 0. Key Insights from Debugging

### Task Chain Dependencies
When porting heuristics that work together in chains (like h3->h6), pay attention to:

1. Context Passing
   - Tasks created by one heuristic must include all necessary info in their supplemental field
   - The receiving heuristic must know how to extract this info from supplemental
   - Never rely on heuristic context to persist between tasks

2. Registry Access 
   - Heuristics should get the unit_registry from task_manager in context, not from their rule object
   - All unit creation must go through the shared registry in task_manager
   - Always verify unit registration succeeded before continuing

3. Task Results
   - Initialize task_results if missing AND add required lists (new_units, modified_units) if missing
   - Tasks expecting 'new_units' or 'modified_units' should explicitly create those lists
   - Verify task_results updates are reflected in the context object

4. Task Types vs Subtasks
   - A heuristic may handle both main tasks (e.g., 'specialization') and subtasks (e.g., specializing a specific slot)
   - Check task.supplemental for additional context like 'slot_to_change'
   - Exit cleanly (return True) for task types you recognize but aren't meant to handle

5. Logging Strategy
   - Log context state at start and end of major functions
   - Log all unit registry operations (creation, registration, verification)
   - Log task_results modifications
   - Include enough detail to trace value transformations

## 1. Basic Structure

Each heuristic should be in its own file named `hN.py` where N is the heuristic number. The file should contain:

1. A docstring describing the heuristic's purpose
2. A setup function named `setup_hN` 
3. Rule factory decorated functions for each behavior

Example template:
```python
"""HN heuristic implementation: Brief description."""
import logging
from ..heuristics import rule_factory

logger = logging.getLogger(__name__)

def setup_hN(heuristic):
    """Configure HN: Detailed description."""
    # Setup core properties
    heuristic.set_prop('worth', VALUE)
    heuristic.set_prop('english', "IF ... THEN ...")
    heuristic.set_prop('abbrev', "Short description")
    heuristic.set_prop('arity', N)  # Usually 1

    # Add rule functions with decorators
    @rule_factory
    def if_potentially_relevant(rule, context):
        """Quick relevance check."""
        pass

    @rule_factory 
    def then_compute(rule, context):
        """Main computation."""
        pass
```

## 2. Rule Function Patterns

### Basic Rules

Every heuristic needs at least:

1. `if_potentially_relevant`: Quick check if rule might apply
2. One or more action functions (e.g., `then_compute`, `then_add_to_agenda`)

Rules should:
- Take `rule` and `context` parameters 
- Return boolean indicating success/failure
- Use rule.unit_registry and rule.task_manager for system access
- Update task_results in context appropriately

### Relevance Checking

Two common patterns for checking relevance:

1. Single-stage check (most common):
```python
@rule_factory
def if_potentially_relevant(rule, context):
    """Check task_results for needed data."""
    task_results = context.get('task_results', {})
    needed_data = task_results.get('key', [])
    return bool(needed_data)
```

2. Two-stage check:
```python
@rule_factory
def if_potentially_relevant(rule, context):
    """First gate - check task type."""
    task = context.get('task')
    return task.get('task_type') == 'expected_type'

@rule_factory
def if_truly_relevant(rule, context):
    """Second gate - detailed check."""
    # More specific checks
    return True
```

Choose based on:
- Single-stage for processing task results 
- Two-stage for task type filtering + detailed checks

## 3. Context Access Pattern

Always access context through dictionary pattern for consistency:

```python
# Get task info
task = context.get('task', {})
task_type = task.get('task_type')
supplemental = task.get('supplemental', {})

# Get/update results
task_results = context.get('task_results', {})
task_results['new_key'] = value  
task_results['status'] = 'completed'
task_results['success'] = True
context['task_results'] = task_results
```

## 4. Common Task Result Patterns

1. Success with new tasks:
```python
context['task_results'] = {
    'status': 'completed',
    'success': True,
    'new_tasks': ['Description of tasks added']
}
```

2. Success with modified units:
```python
context['task_results'] = {
    'status': 'completed', 
    'success': True,
    'new_units': [...],
    'modified_units': [...]
}
```

3. Failed operation:
```python
return False  # Function return
# Or explicit results:
context['task_results'] = {
    'status': 'failed',
    'reason': 'Explanation'
}
```

4. Chained heuristic tasks:
```python
# Creating subtasks for another heuristic
new_task = Task(
    priority=task.priority - 10,  # Keep priority chain intact
    unit_name=unit.name,
    slot_name=slot,  # The slot to work on
    task_type='specialization',  # Main task type
    reasons=[f'H3 selected {slot} for specialization'],
    supplemental={  # Include ALL info needed by receiving heuristic
        'task_type': 'specialization',
        'slot_to_change': slot
    }
)

# Store in results
context['task_results'] = {
    'status': 'completed',
    'success': True,
    'new_tasks': [new_task]
}
```

## 5. Creating New Tasks

```python
def then_add_to_agenda(rule, context):
    task_manager = rule.task_manager
    if not task_manager:
        return False
        
    new_task = {
        'priority': min(800, int(rule.worth_value() * 1.1)),
        'unit': unit_name,
        'slot': slot_name,
        'task_type': 'task_type',
        'reasons': ['Reason for task'],
        'supplemental': {
            'credit_to': ['hN']
        }
    }
    task_manager.add_task(new_task)
    
    # Update results
    context['task_results'] = {
        'status': 'completed',
        'success': True,
        'new_tasks': ['Description of tasks added']
    }
    return True
```

## 6. Testing

After porting a heuristic:

1. Add it to eurisko/heuristics/enabled.py
2. Run the system with -v 2 flag
3. Watch task interactions in logs:
   - Check if_potentially_relevant triggers appropriately
   - Verify context access and updates
   - Confirm task result patterns
4. Verify it achieves 100% success rate

## 7. Port Verification Checklist

- [ ] File properly named and located
- [ ] Docstrings present and descriptive
- [ ] Properties correctly set in setup
- [ ] Context accessed via dictionary pattern
- [ ] Task results properly structured and updated
- [ ] Rule functions properly decorated
- [ ] Uses appropriate relevance checking pattern
- [ ] Added to enabled heuristics
- [ ] Tested and verified working
- [ ] Success rate above 0%

Following these guidelines ensures consistent, maintainable heuristic implementations that properly interact with the Eurisko system.