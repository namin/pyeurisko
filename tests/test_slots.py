import pytest
from eurisko.slots import Slot, SlotRegistry

def test_slot_creation():
    """Test basic slot creation."""
    slot = Slot("test_slot", is_criterial=True, data_type="number")
    assert slot.name == "test_slot"
    assert slot.is_criterial
    assert slot.data_type == "number"

def test_slot_validation():
    """Test slot value validation."""
    number_slot = Slot("number_slot", data_type="number")
    assert number_slot.validate_value(42)
    assert number_slot.validate_value(3.14)
    assert not number_slot.validate_value("not a number")

    bit_slot = Slot("bit_slot", data_type="bit")
    assert bit_slot.validate_value(True)
    assert bit_slot.validate_value(False)
    assert bit_slot.validate_value(1)
    assert bit_slot.validate_value(0)
    assert not bit_slot.validate_value(2)

def test_slot_registry():
    """Test the slot registry functionality."""
    registry = SlotRegistry()
    
    # Test core slots initialization
    assert registry.exists("worth")
    assert registry.exists("isa")
    assert registry.exists("examples")
    
    # Test criterial vs non-criterial sorting
    criterial = registry.criterial_slots()
    non_criterial = registry.non_criterial_slots()
    
    assert "alg" in criterial
    assert "worth" in non_criterial

def test_slot_relationships():
    """Test slot relationship handling."""
    slot = Slot("parent_slot", 
                sub_slots=["child1", "child2"],
                super_slots=["super1", "super2"])
    
    assert "child1" in slot.sub_slots
    assert "super1" in slot.super_slots

def test_slot_registry_singleton():
    """Test that SlotRegistry maintains singleton pattern."""
    registry1 = SlotRegistry()
    registry2 = SlotRegistry()
    assert registry1 is registry2

def test_custom_slot_registration():
    """Test registering custom slots."""
    registry = SlotRegistry()
    
    new_slot = Slot("custom_slot", 
                    is_criterial=True,
                    data_type="text",
                    dont_copy=True)
    
    registry.register(new_slot)
    retrieved = registry.get_slot("custom_slot")
    
    assert retrieved is not None
    assert retrieved.is_criterial
    assert retrieved.data_type == "text"
    assert retrieved.dont_copy
