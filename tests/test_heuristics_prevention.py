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