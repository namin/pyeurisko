"""Test suite for EURISKO's prevention heuristics (h14-h15)."""
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
    
    # Create a failed unit that resulted from a problematic type change
    failed_unit = Unit('failed_function')
    failed_unit.set_prop('creditors', ['h6'])
    
    # Create the creditor heuristic with an application record showing the type change
    h6 = Unit('h6')
    
    # Original value was a simple number, changed to a complex function
    original_number = 42
    complex_function = lambda x: x * x + 2 * x - 1
    
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
    
    # Verify task results
    task_results = context.get('task_results', {})
    new_units = task_results.get('new_units', [])
    assert len(new_units) == 1
    
    # Examine prevention rule properties
    rule = new_units[0]
    assert 'prevention-rule' in rule.get_prop('isa')
    assert rule.get_prop('slot_to_avoid') == 'calculation'
    assert rule.get_prop('from_type') == 'number'
    assert rule.get_prop('to_type') == 'function'
    assert rule.get_prop('learned_from') == 'failed_function'
    
    # Test the prevention rule's relevance check
    relevance_check = rule.get_prop('if_potentially_relevant')
    assert callable(relevance_check)
    
    # Should identify similar type conversions
    similar_context = {
        'task': {
            'task_type': 'modification',
            'slot_to_change': 'calculation',
            'new_value': lambda x: x + 1
        },
        'unit': Unit('test_unit', properties={'calculation': 100})
    }
    assert relevance_check(similar_context)
    
    # Should ignore different slots or type changes
    different_slot_context = {
        'task': {
            'task_type': 'modification',
            'slot_to_change': 'different_slot',
            'new_value': lambda x: x + 1
        },
        'unit': Unit('test_unit', properties={'different_slot': 100})
    }
    assert not relevance_check(different_slot_context)
    
    different_types_context = {
        'task': {
            'task_type': 'modification',
            'slot_to_change': 'calculation',
            'new_value': "string value"
        },
        'unit': Unit('test_unit', properties={'calculation': 100})
    }
    assert not relevance_check(different_types_context)

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
        'task': {'task_type': 'find_examples'}
    }
    
    # Should find examples from both operations
    assert h15.apply(context)
    
    task_results = context.get('task_results', {})
    new_examples = task_results.get('new_values', [])
    assert len(new_examples) == 4
    assert 'value1' in new_examples
    assert 'value4' in new_examples
    
    # Should track which operations provided examples
    source_ops = task_results.get('source_operations', [])
    assert 'op1' in source_ops
    assert 'op2' in source_ops
    
    # Test sequential operation chain
    # Create a unit that's the range of an operation that uses the results of another
    chain_unit = Unit('chain_range')
    chain_unit.set_prop('is_range_of', ['composite_op'])
    
    composite_op = Unit('composite_op')
    composite_op.set_prop('applications', [
        {'args': ['value1'], 'result': 'chain1'},  # Uses result from op1
        {'args': ['value3'], 'result': 'chain2'}   # Uses result from op2
    ])
    
    registry.unit_registry.register(composite_op)
    registry.unit_registry.register(chain_unit)
    
    chain_context = {
        'unit': chain_unit,
        'task': {'task_type': 'find_examples'}
    }
    
    # Should find examples through operation chain
    assert h15.apply(chain_context)
    
    chain_results = chain_context.get('task_results', {})
    chain_examples = chain_results.get('new_values', [])
    assert len(chain_examples) == 2
    assert 'chain1' in chain_examples
    assert 'chain2' in chain_examples
    
    # Should identify operation chain
    operation_chain = chain_results.get('operation_chain', [])
    assert len(operation_chain) > 1