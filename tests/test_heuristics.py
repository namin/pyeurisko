"""Test suite for heuristics functionality."""
import pytest
from eurisko.heuristics import Heuristic, HeuristicRegistry
from eurisko.unit import Unit, UnitRegistry

@pytest.fixture
def test_heuristic():
    """Create a test heuristic."""
    heuristic = Heuristic("test_heuristic", "Test Description", worth=700)
    heuristic.set_prop("if_potentially_relevant", lambda ctx: ctx.get('value', 0) > 0)
    heuristic.set_prop("if_truly_relevant", lambda ctx: ctx.get('value', 0) > 100)
    heuristic.set_prop("then_compute", lambda ctx: ctx.get('value', 0) < 1000)
    return heuristic

@pytest.fixture
def test_context():
    """Create a test context."""
    return {'value': 500, 'unit': Unit("test_unit")}

def test_heuristic_creation():
    """Test basic heuristic creation and properties."""
    heuristic = Heuristic("test_h", "Test Description")
    assert heuristic.name == "test_h"
    assert heuristic.get_prop("english") == "Test Description"
    assert heuristic.get_prop("isa") == ["heuristic"]
    assert heuristic.worth_value() == 700  # Default worth

def test_heuristic_records():
    """Test heuristic record keeping."""
    heuristic = Heuristic("test_h")
    
    # Check record initialization
    record_types = [
        'overall_record',
        'then_compute_record',
        'then_print_record',
        'then_conjecture_record'
    ]
    
    for record in record_types:
        assert heuristic.get_prop(record) == [0.0, 0]
        assert heuristic.get_prop(f"{record}_failed") == [0.0, 0]

def test_relevance_checks(test_heuristic, test_context):
    """Test relevance checking functions."""
    assert test_heuristic.is_potentially_relevant(test_context)
    assert test_heuristic.is_truly_relevant(test_context)
    
    # Test with failing context
    failing_context = {'value': 50}  # Below truly_relevant threshold
    assert test_heuristic.is_potentially_relevant(failing_context)
    assert not test_heuristic.is_truly_relevant(failing_context)

def test_heuristic_application(test_heuristic, test_context):
    """Test full heuristic application."""
    assert test_heuristic.apply(test_context)
    
    # Check record updates
    overall_record = test_heuristic.get_prop('overall_record')
    assert overall_record[1] == 1  # One successful application
    assert overall_record[0] > 0  # Some time elapsed

def test_heuristic_registry():
    """Test heuristic registry initialization and core rules."""
    registry = HeuristicRegistry()
    
    # Core heuristics should be initialized
    core_heuristics = ['h1', 'h2', 'h3', 'h4', 'h5']
    for name in core_heuristics:
        heuristic = registry.unit_registry.get_unit(name)
        assert heuristic is not None
        assert isinstance(heuristic, Heuristic)
        assert heuristic.get_prop('isa') == ['heuristic']

def test_h1_behavior():
    """Test the specialized behavior of H1."""
    registry = HeuristicRegistry()
    h1 = registry.unit_registry.get_unit('h1')
    
    # H1 checks for units with some good but mostly bad applications
    test_unit = Unit('test_unit')
    test_unit.set_prop('applics', [
        {'worth': 900},  # One good application
        {'worth': 100},  # Many bad applications
        {'worth': 200},
        {'worth': 300},
        {'worth': 150}
    ])
    
    context = {'unit': test_unit}
    assert h1.is_potentially_relevant(context)
    assert h1.is_truly_relevant(context)

def test_h2_behavior():
    """Test the specialized behavior of H2."""
    registry = HeuristicRegistry()
    h2 = registry.unit_registry.get_unit('h2')
    
    # Create a test context with new units from a "garbage" producer
    garbage_producer = Unit('garbage_producer')
    garbage_producer.set_prop('applics', [
        {'result': [Unit('empty1')]} for _ in range(10)
    ])
    
    new_unit = Unit('new_unit')
    new_unit.set_prop('creditors', ['garbage_producer'])
    
    context = {
        'task_results': {
            'new_units': [new_unit]
        }
    }
    
    assert h2.is_potentially_relevant(context)

def test_applicable_heuristics():
    """Test finding applicable heuristics for a context."""
    registry = HeuristicRegistry()
    
    # Create a context that should trigger H4
    context = {
        'task_results': {
            'new_units': [Unit('new_test_unit')]
        }
    }
    
    applicable = registry.get_applicable_heuristics(context)
    assert any(h.name == 'h4' for h in applicable)

def test_heuristic_subsumption(test_heuristic):
    """Test heuristic subsumption relationships."""
    subsuming = Heuristic("better_h", "A better version")
    test_heuristic.set_prop('subsumed_by', ['better_h'])
    
    assert test_heuristic.is_subsumed_by(subsuming)
