"""Test h6 specialization functionality."""
import pytest
from eurisko.tasks import Task
from eurisko.units import UnitRegistry, Unit, initialize_all_units
from eurisko.tasks.task_manager import TaskManager
from eurisko.heuristics.h6 import setup_h6
from eurisko.heuristics import rule_factory

@pytest.fixture
def clean_registry():
    """Provide a clean unit registry for each test."""
    # Reset the global instance
    UnitRegistry.reset_instance()
    # Create a new clean registry
    registry = UnitRegistry.get_instance()
    return registry

def test_h6_specializes_slot(clean_registry):
    """Test that h6 can create a specialized unit when given a valid task."""
    # Set up test environment
    task_manager = TaskManager()
    task_manager.unit_registry = clean_registry
    unit_registry = task_manager.unit_registry
    
    # Skip initialization to avoid lisp_units conflict
    # initialize_all_units(unit_registry)

    # Create test unit 
    unit = Unit("test-unit", 500)
    unit.set_prop('isa', ['math-concept', 'anything'])
    unit.set_prop('domain', ['nnumber', 'nnumber'])
    unit.set_prop('worth', 500)
    assert unit_registry.register(unit)

    # Create specialization task
    task = Task(
        priority=500,
        unit_name="test-unit",
        slot_name="domain",  
        task_type="specialization",
        reasons=["test specialization"],
        supplemental={
            'task_type': 'specialization',
            'slot_to_change': 'domain'
        }
    )

    # Set up minimal test context
    context = {
        'unit': unit,
        'task': task,
        'task_manager': task_manager,
        'task_results': {
            'status': 'in_progress',
            'new_units': [],
            'modified_units': []
        }
    }

    # Create minimally viable specialized value
    context['new_value'] = ['nnumber']  # Specialize from [nnumber, nnumber] to [nnumber]
    context['slot_to_change'] = 'domain'

    # Get h6 rule functions
    h6 = Unit('h6', 700)
    h6.set_prop('isa', ['heuristic', 'anything', 'op'])
    setup_h6(h6)
    assert unit_registry.register(h6)

    # Test just the unit creation part
    h6_define = h6.get_prop('then_define_new_concepts')(h6, context)
    assert h6_define == True

    # Verify unit was created
    new_unit_name = f"test-unit-domain-spec"
    new_unit = unit_registry.get_unit(new_unit_name)
    assert new_unit is not None

    # Verify properties
    assert new_unit.get_prop('domain') == ['nnumber']  # Should be specialized
    assert new_unit.get_prop('worth') == 450  # 90% of original
    assert unit.get_prop('specializations') == [new_unit_name]
    assert new_unit.get_prop('generalizations') == ['test-unit']