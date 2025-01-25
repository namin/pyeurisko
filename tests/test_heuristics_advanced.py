"""Test suite for advanced heuristics h6-h11."""
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

def test_h6_specialization(registry, test_unit):
    """Test H6's slot specialization capability."""
    h6 = registry.unit_registry.get_unit('h6')
    
    context = {
        'unit': test_unit,
        'task': {
            'task_type': 'specialization',
            'slot_to_change': 'test_slot'
        }
    }
    
    # Should recognize relevant task
    assert h6.is_potentially_relevant(context)
    assert h6.is_truly_relevant(context)
    
    # Should create specialized unit
    result = h6.apply(context)
    assert result
    
    # Check task results
    task_results = context.get('task_results', {})
    new_units = task_results.get('new_units', [])
    assert len(new_units) == 1
    
    # New unit should be a specialization
    new_unit = new_units[0]
    assert new_unit.get_prop('test_slot') != test_unit.get_prop('test_slot')
    assert len(new_unit.get_prop('test_slot')) <= len(test_unit.get_prop('test_slot'))

def test_h7_instance_finding(registry):
    """Test H7's instance finding for empty concepts."""
    h7 = registry.unit_registry.get_unit('h7')
    
    # Create unit with no instances
    test_unit = Unit('empty_concept')
    test_unit.set_prop('isa', ['category'])
    test_unit.set_prop('instances_slot', 'examples')
    
    context = {'unit': test_unit}
    
    # Should recognize need for instances
    assert h7.is_truly_relevant(context)
    
    # Should create task to find instances
    result = h7.apply(context)
    assert result
    
    task = context.get('task', {})
    assert task.get('task_type') == 'find_instances'
    assert task.get('target_unit') == 'empty_concept'

def test_h8_application_finding(registry, test_unit):
    """Test H8's application finding through generalizations."""
    h8 = registry.unit_registry.get_unit('h8')
    
    # Create generalization with known applications
    general_unit = Unit('general_op')
    general_unit.set_prop('applications', [
        {'args': [1], 'result': 2},
        {'args': [2], 'result': 4}
    ])
    test_unit.set_prop('generalizations', ['general_op'])
    registry.unit_registry.register(general_unit)
    
    context = {
        'unit': test_unit,
        'task': {'task_type': 'find_applications'}
    }
    
    # Should find applications from generalization
    assert h8.apply(context)
    
    task_results = context.get('task_results', {})
    new_values = task_results.get('new_values', [])
    assert len(new_values) > 0

def test_h9_example_finding(registry):
    """Test H9's example finding through generalizations."""
    h9 = registry.unit_registry.get_unit('h9')
    
    # Create test unit with definition
    test_unit = Unit('test_concept')
    test_unit.set_prop('definition', lambda x: x > 5)
    
    # Create generalization with examples
    general = Unit('general_concept')
    general.set_prop('examples', [3, 6, 8, 10])
    test_unit.set_prop('generalizations', ['general_concept'])
    registry.unit_registry.register(general)
    
    context = {
        'unit': test_unit,
        'task': {'task_type': 'find_examples'}
    }
    
    # Should find valid examples
    assert h9.apply(context)
    
    task_results = context.get('task_results', {})
    new_values = task_results.get('new_values', [])
    assert all(x > 5 for x in new_values)

def test_h10_range_examples(registry):
    """Test H10's example finding through operation ranges."""
    h10 = registry.unit_registry.get_unit('h10')
    
    # Create test unit in range of operation
    test_unit = Unit('test_range')
    test_unit.set_prop('is_range_of', ['test_op'])
    
    # Create operation with applications
    operation = Unit('test_op')
    operation.set_prop('applications', [
        {'args': [1], 'result': 'value1'},
        {'args': [2], 'result': 'value2'}
    ])
    registry.unit_registry.register(operation)
    
    context = {
        'unit': test_unit,
        'task': {'task_type': 'find_examples'}
    }
    
    # Should find examples from operation results
    assert h10.apply(context)
    
    task_results = context.get('task_results', {})
    new_values = task_results.get('new_values', [])
    assert len(new_values) > 0

def test_h11_domain_applications(registry):
    """Test H11's application finding using algorithm and domain."""
    h11 = registry.unit_registry.get_unit('h11')
    
    # Create domain with examples
    number_domain = Unit('number')
    number_domain.set_prop('examples', [1, 2, 3, 4, 5])
    number_domain.set_prop('definition', lambda x: isinstance(x, (int, float)))
    registry.unit_registry.register(number_domain)
    
    # Create test unit with algorithm
    test_unit = Unit('doubler')
    test_unit.set_prop('algorithm', lambda x: x * 2)
    test_unit.set_prop('domain', ['number'])
    
    context = {
        'unit': test_unit,
        'task': {'task_type': 'find_applications'}
    }
    
    # Should find applications using algorithm
    assert h11.apply(context)
    
    task_results = context.get('task_results', {})
    new_values = task_results.get('new_values', [])
    assert len(new_values) > 0
    # Check that results are doubles of inputs
    for app in new_values:
        assert app['result'] == app['args'][0] * 2