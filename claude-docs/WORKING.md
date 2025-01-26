# Working Patterns for PyEurisko Development

## Heuristic Implementation
Essential components:

1. Setup Function
```python
def setup_h<N>(heuristic):
    # Basic properties
    heuristic.set_prop('worth', value)
    heuristic.set_prop('english', description)
    heuristic.set_prop('abbrev', short_description)
    
    # Record functions for tracking
    def record_func(rule, context):
        return True
    heuristic.set_prop('then_compute_record', record_func)
    heuristic.set_prop('then_define_new_concepts_record', record_func)
    heuristic.set_prop('overall_record', record_func)
```

2. Context Access
```python
# Always use get() for context access
unit = context.get('unit')
task = context.get('task')

# Check required context items
if not all([unit, task]):
    return False
```

3. Property Handling
```python
# Check existence before access
if unit.has_prop(key):
    value = unit.get_prop(key)
    
# Add to property lists
unit.add_to_prop('specializations', new_value)
```

4. Task Structure
```python
task = {
    'priority': priority_value,
    'unit': unit.name,  # Use name not object
    'slot': slot_name,
    'reasons': [reason_string],
    'task_type': type_string,
    'supplemental': {
        'key': value,
        'credit_to': ['h<N>'] + existing_credits
    }
}
```

5. Task Results
```python
task_results = context.get('task_results', {})
task_results['new_tasks'] = ["Description of tasks created"]
context['task_results'] = task_results
```

## Common Issues
- Missing record functions in setup
- Using direct attribute access on context
- Not checking property existence before access
- Passing unit objects instead of names in tasks
- Not maintaining task_results properly

## Testing
Run with:
```bash
python -m eurisko.main
```

Watch heuristic performance metrics for success rates.