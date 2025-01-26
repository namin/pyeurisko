"""Test suite for advanced heuristics h6-h13."""
import pytest
from eurisko.heuristics import HeuristicRegistry
from eurisko.unit import Unit

@pytest.fixture
def registry():
    """Create a fresh heuristic registry."""
    return HeuristicRegistry()

@pytest.fixture
def test_unit():
    """Create a test unit with various properties."""
    unit = Unit('test_unit')
    unit.set_prop('slots', ['test_slot', 'other_slot'])
    unit.set_prop('test_slot', [1, 2, 3, 4, 5])
    unit.set_prop('data_type', 'list')
    unit.set_prop('algorithm', lambda x: x * 2)
    unit.set_prop('domain', ['number'])
    return unit

def test_h12_prevention_rule(registry):
    """Test H12's creation of prevention rules from mistakes."""
    h12 = registry.unit_registry.get_unit('h12')
    
    # Create a unit that will be deleted
    failed_unit = Unit('failed_op')
    failed_unit.set_prop('creditors', ['h5'])  # Created by h5
    failed_unit.set_prop('applications', [{
        'task_info': {
            'slot_to_change': 'if_working_on_task'
        },
        'result': ['failed_op']
    }])
    
    # Create the creditor heuristic with application record
    h5 = Unit('h5')
    h5.set_prop('applications', [{
        'task_info': {
            'slot_to_change': 'if_working_on_task'
        },
        'result': ['failed_op']
    }])
    registry.unit_registry.register(h5)
    registry.unit_registry.register(failed_unit)
    
    context = {
        'unit': failed_unit,
        'deleted_units': ['failed_op']
    }
    
    # Should create prevention rule
    assert h12.apply(context)
    
    task_results = context.get('task_results', {})
    new_units = task_results.get('new_units', [])
    assert len(new_units) == 1
    
    # Check prevention rule properties
    rule = new_units[0]
    assert 'prevention-rule' in rule.get('isa')
    assert rule.get('slot_to_avoid') == 'if_working_on_task'
    assert rule.get('learned_from') == 'failed_op'

def test_h13_modification_prevention(registry):
    """Test H13's creation of modification prevention rules."""
    h13 = registry.unit_registry.get_unit('h13')
    
    # Create a unit that will be deleted
    failed_unit = Unit('failed_op')
    failed_unit.set_prop('creditors', ['h6'])  # Created by h6
    failed_unit.set_prop('applications', [{
        'task_info': {
            'slot_to_change': 'algorithm',
            'old_value': 'lambda x: x + 1',
            'new_value': 'lambda x: x * 2'
        },
        'result': ['failed_op']
    }])
    
    # Create the creditor heuristic with application record
    h6 = Unit('h6')
    h6.set_prop('applications', [{
        'task_info': {
            'slot_to_change': 'algorithm',
            'old_value': 'lambda x: x + 1',
            'new_value': 'lambda x: x * 2'
        },
        'result': ['failed_op']
    }])
    registry.unit_registry.register(h6)
    registry.unit_registry.register(failed_unit)
    
    context = {
        'unit': failed_unit,
        'deleted_units': ['failed_op']
    }
    
    # Should create prevention rule
    assert h13.apply(context)
    
    task_results = context.get('task_results', {})
    new_units = task_results.get('new_units', [])
    assert len(new_units) == 1
    
    # Check prevention rule properties
    rule = new_units[0]
    assert 'prevention-rule' in rule.get('isa')
    assert rule.get('slot_to_avoid') == 'algorithm'
    assert rule.get('pattern_from') == 'lambda x: x + 1'
    assert rule.get('pattern_to') == 'lambda x: x * 2'
    assert rule.get('learned_from') == 'failed_op'
    assert rule.get('source_creditor') == 'h6'
    
    # Verify pattern detection in task results
    pattern = task_results.get('pattern_detected', {})
    assert pattern.get('slot') == 'algorithm'
    assert pattern.get('from') == 'lambda x: x + 1'
    assert pattern.get('to') == 'lambda x: x * 2'

def test_h14_entity_type_prevention(registry):
    """Test H14's ability to prevent changes based on entity types."""
    h14 = registry.unit_registry.get_unit('h14')
    
    # Create a failed unit that resulted from a problematic type change
    failed_unit = Unit('failed_function')
    failed_unit.set_prop('creditors', ['h6'])
    
    # Original value was a simple number, changed to a complex function
    original_number = 42
    complex_function = lambda x: x * x + 2 * x - 1
    
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
        'registry': registry
    }
    
    # Should find examples from both operations
    assert h15.apply(context)
    
    task_results = context.get('task_results', {})
    new_examples = task_results.get('new_values', [])
    assert len(new_examples) == 4  # Should find all values
    assert set(new_examples) == {'value1', 'value2', 'value3', 'value4'}