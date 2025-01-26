"""Test prevention rule generation heuristics."""
import pytest
from eurisko.heuristics import HeuristicRegistry
from eurisko.unit import Unit

@pytest.fixture
def registry():
    """Create a fresh heuristic registry."""
    return HeuristicRegistry()

def test_h14_entity_type_prevention(registry):
    """Test H14's ability to prevent changes based on entity types."""
    h14 = registry.unit_registry.get_unit('h14')
    
    # Original value was a simple number, changed to a complex function
    original_number = 42
    complex_function = lambda x: x * x + 2 * x - 1
    
    # Create a failed unit that resulted from a problematic type change
    failed_unit = Unit('failed_function')
    failed_unit.set_prop('creditors', ['h6'])
    failed_unit.set_prop('applications', [{
        'task_info': {
            'slot_to_change': 'calculation',
            'old_value': original_number,
            'new_value': complex_function
        },
        'result': ['failed_function']
    }])
    
    # Create the creditor heuristic with application record
    h6 = Unit('h6')
    h6.set_prop('applications', [{
        'task_info': {
            'slot_to_change': 'calculation',
            'old_value': original_number,
            'new_value': complex_function
        },
        'result': ['failed_function']
    }])
    
    # Register necessary units
    registry.unit_registry.register(h6)
    registry.unit_registry.register(failed_unit)
    
    context = {
        'unit': failed_unit,
        'deleted_units': ['failed_function']
    }
    
    # Should create prevention rule
    assert h14.apply(context)
    
    task_results = context.get('task_results', {})
    new_units = task_results.get('new_units', [])
    
    # Should create both type-based and complexity-based rules
    assert len(new_units) == 2
    
    # Check type-based rule
    type_rule = next(r for r in new_units if 'type-prevention' in r.get('type', ''))
    assert type_rule.get('slot_to_avoid') == 'calculation'
    assert type_rule.get('from_type') == 'int'
    assert type_rule.get('to_type') == 'function'
    
    # Check complexity-based rule
    complexity_rule = next(r for r in new_units if 'complexity-prevention' in r.get('type', ''))
    assert complexity_rule.get('slot_to_avoid') == 'calculation'
    assert complexity_rule.get('check') == 'complexity_increase'

def test_h15_multiple_operations(registry):
    """Test H15's ability to find examples through multiple operations."""
    h15 = registry.unit_registry.get_unit('h15')
    
    # Create a test unit in range of multiple operations
    test_unit = Unit('test_range')
    test_unit.set_prop('is_range_of', ['op1', 'op2'])
    
    # Create operations with applications
    op1 = Unit('op1')
    op1.set_prop('applications', [
        {'args': [1], 'result': 'value1'},
        {'args': [2], 'result': 'value2'}
    ])
    
    op2 = Unit('op2')
    op2.set_prop('applications', [
        {'args': [3], 'result': 'value3'},
        {'args': [4], 'result': 'value4'}
    ])
    
    registry.unit_registry.register(op1)
    registry.unit_registry.register(op2)
    registry.unit_registry.register(test_unit)
    
    context = {
        'unit': test_unit,
        'task': {'task_type': 'find_examples'},
        'task_results': {},
        'registry': registry
    }
    
    # Should find examples from both operations
    success = h15.apply(context)
    assert success
    
    task_results = context.get('task_results', {})
    new_examples = task_results.get('new_values', [])
    
    # Verify correct examples were found
    assert len(new_examples) == 4
    assert all(val in new_examples for val in ['value1', 'value2', 'value3', 'value4'])
    
    # Verify source tracking
    source_ops = task_results.get('source_operations', [])
    assert all(op in source_ops for op in ['op1', 'op2'])
    
    # Verify pattern analysis
    pattern_analysis = task_results.get('pattern_analysis', {})
    assert pattern_analysis.get('total_unique') == 4
    assert not pattern_analysis.get('value_overlap')  # No overlapping values
    
    # Verify operation patterns
    op_patterns = pattern_analysis.get('operation_patterns', {})
    for op_name in ['op1', 'op2']:
        op_pattern = op_patterns.get(op_name, {})
        assert op_pattern.get('unique_values') == 2
        assert op_pattern.get('total_values') == 2
        assert 'str' in op_pattern.get('value_types', set())