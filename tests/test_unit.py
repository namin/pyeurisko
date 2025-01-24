import pytest
from eurisko.unit import Unit, UnitRegistry

def test_unit_creation():
    """Test basic unit creation and property access."""
    unit = Unit("test_unit", worth=750)
    assert unit.name == "test_unit"
    assert unit.worth_value() == 750

def test_unit_properties():
    """Test property manipulation."""
    unit = Unit("test_unit")
    
    # Test setting and getting properties
    unit.set_prop("test_prop", "test_value")
    assert unit.get_prop("test_prop") == "test_value"
    
    # Test list properties
    unit.add_prop("list_prop", "item1")
    unit.add_prop("list_prop", "item2")
    assert unit.get_prop("list_prop") == ["item1", "item2"]
    
    # Test adding to front of list
    unit.add_prop("list_prop", "item0", to_head=True)
    assert unit.get_prop("list_prop") == ["item0", "item1", "item2"]

def test_unit_isa():
    """Test ISA relationships."""
    unit = Unit("test_unit")
    unit.set_prop("isa", ["category1", "category2"])
    assert set(unit.isa()) == {"category1", "category2"}

def test_unit_registry():
    """Test the unit registry functionality."""
    registry = UnitRegistry()
    
    # Create and register a unit
    unit1 = Unit("unit1", worth=500)
    unit1.set_prop("isa", ["category1"])
    registry.register(unit1)
    
    # Test retrieval
    assert registry.get_unit("unit1") == unit1
    assert "unit1" in registry.get_units_by_category("category1")
    
    # Test unregistration
    registry.unregister("unit1")
    assert registry.get_unit("unit1") is None
    assert "unit1" not in registry.get_units_by_category("category1")

def test_unit_algorithm():
    """Test unit algorithm execution."""
    unit = Unit("test_unit")
    unit.set_prop("fast_alg", lambda x, y: x + y)
    
    result = unit.apply_alg([5, 3])
    assert result == 8

def test_unit_equality():
    """Test unit equality comparison."""
    unit1 = Unit("test_unit", worth=500)
    unit2 = Unit("test_unit", worth=700)  # Different worth, same name
    unit3 = Unit("other_unit", worth=500)  # Same worth, different name
    
    assert unit1 == unit2  # Units with same name are equal
    assert unit1 != unit3  # Units with different names are not equal
    assert len({unit1, unit2}) == 1  # Units with same name are treated as same in sets
