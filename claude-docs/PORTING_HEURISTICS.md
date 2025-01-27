# Guide to Porting Eurisko Heuristics

This document describes the process and patterns for porting heuristics from the original Lisp codebase to Python. By following these guidelines, we maintain consistency and ensure proper interaction with the Eurisko task system.

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

    # Add rule functions
    @rule_factory
    def if_potentially_relevant(rule, context):
        """First gate - quick check if rule might apply."""
        pass

    @rule_factory 
    def then_compute(rule, context):
        """Main computation of the rule."""
        pass

    # Additional behaviors as needed
```

## 2. Context Access Pattern

IMPORTANT: Always access context through dictionary pattern for consistency:

DO:
```python
task_type = context.get('task', {}).get('task_type')
supplemental = context.get('task', {}).get('supplemental', {})
task_results = context.get('task_results', {})
```

DON'T:
```python
task_type = context['task'].task_type  # Don't access attributes directly
```

## 3. Rule Functions

Every heuristic needs at least:

1. `if_potentially_relevant`: Quick check if rule might apply
2. One or more action functions (e.g., `then_compute`, `then_add_to_agenda`)

Rules should:
- Take `rule` and `context` parameters
- Return boolean indicating success/failure
- Use rule.unit_registry and rule.task_manager for system access
- Modify context['task_results'] to communicate results

## 4. Task Result Pattern

When modifying task results:
```python
task_results = context.get('task_results', {})
task_results['new_key'] = value
context['task_results'] = task_results  # Always put back in context
```

## 5. Unit Properties Pattern

When working with unit properties:
```python
# Getting properties
value = unit.get_prop('property_name', default_value)
types = unit.get_prop('isa', [])

# Setting properties
unit.set_prop('property_name', value)
unit.add_to_prop('list_property', new_item)
```

## 6. Common Patterns

1. Checking task type:
```python
def if_potentially_relevant(rule, context):
    task = context.get('task')
    if not task:
        return False
    return task.get('task_type') == 'expected_type'
```

2. Creating new tasks:
```python
def then_add_to_agenda(rule, context):
    task_manager = rule.task_manager
    if not task_manager:
        return False
        
    new_task = {
        'priority': VALUE,
        'unit': unit_name,
        'slot': slot_name,
        'task_type': 'task_type',
        'reasons': ['Reason for task'],
        'supplemental': {
            'credit_to': ['hN']
        }
    }
    task_manager.add_task(new_task)
    return True
```

3. Working with new units:
```python
def then_compute(rule, context):
    task_results = context.get('task_results', {})
    new_units = task_results.get('new_units', [])
    
    # Do work with new units
    
    # Update results
    task_results['new_units'] = new_units
    context['task_results'] = task_results
    return True
```

## 7. Testing

After porting a heuristic:

1. Add it to eurisko/heuristics/enabled.py
2. Run the system with -v 2 flag
3. Verify task interactions in logs
4. Check it achieves 100% success rate

## 8. Port Verification Checklist

- [ ] File properly named and located
- [ ] Docstrings present and descriptive
- [ ] Properties correctly set in setup
- [ ] Context accessed via dictionary pattern
- [ ] Task results properly updated
- [ ] Unit properties accessed via get_prop/set_prop
- [ ] Rule functions properly decorated
- [ ] Added to enabled heuristics
- [ ] Tested and verified working

Following these guidelines ensures consistent, maintainable heuristic implementations that properly interact with the Eurisko system.