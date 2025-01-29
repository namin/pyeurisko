import os
import logging
from .neo import NeoEurisko, Unit, SlotType
from typing import Optional, Dict, Any
import argparse
import time

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('neo_eurisko')

# Optional pyeurisko integration
try:
    from .units import Unit as EuriskoUnit
    from .heuristics import rule_factory
    logger.info("Successfully imported pyeurisko components")
    HAVE_PYEURISKO = True
except ImportError:
    logger.warning("Could not import pyeurisko - running in standalone mode")
    HAVE_PYEURISKO = False

def find_number_patterns(target: 'Unit', eurisko: 'NeoEurisko') -> Dict[str, Any]:
    '''Look for interesting numerical patterns in unit properties.
    If found, create new specialized units based on those patterns.'''
    result = {"success": False, "patterns_found": [], "worth_generated": 0}
    
    # Get numerical properties
    numbers = []
    for slot in target.slots.values():
        if isinstance(slot.value, (int, float)):
            numbers.append(slot.value)
    
    if len(numbers) < 2:
        return result
        
    # Look for patterns
    patterns = []
    
    # Check if all numbers are even
    if all(n % 2 == 0 for n in numbers):
        patterns.append("all_even")
        
    # Check if all numbers are powers of 2
    def is_power_2(n):
        return n > 0 and (n & (n - 1)) == 0
    if all(is_power_2(n) for n in numbers):
        patterns.append("powers_of_2")
        
    # If patterns found, create specialized unit
    if patterns:
        new_name = f"{target.name}-numeric-{patterns[0]}"
        specialized = Unit(new_name)
        specialized.worth = min(1000, target.worth + 100)
        specialized.add_slot("specializes", target.name, SlotType.UNIT)
        specialized.add_slot("pattern_found", patterns[0], SlotType.TEXT)
        eurisko.units[new_name] = specialized
        
        result["success"] = True
        result["patterns_found"] = patterns
        result["worth_generated"] = 100
        
    return result

def create_number_theory_heuristic(eurisko: NeoEurisko) -> Unit:
    """Create a simple number theory heuristic to test the system."""
    logger.info("Creating number theory heuristic")
    # Instead of eval, pass the function directly
    return eurisko.create_heuristic_from_function(find_number_patterns)

def create_test_unit() -> Unit:
    """Create a test unit with some numerical properties."""
    logger.info("Creating test unit with numerical properties")
    unit = Unit("test-numbers")
    unit.add_slot("value1", 4, SlotType.LIST)
    unit.add_slot("value2", 8, SlotType.LIST)
    unit.add_slot("value3", 16, SlotType.LIST)
    logger.debug(f"Created unit with slots: {unit.slots}")
    return unit

def bridge_to_pyeurisko(neo_unit: Unit) -> Optional[EuriskoUnit]:
    """Convert a neo-eurisko unit to pyeurisko format if available."""
    if not HAVE_PYEURISKO:
        return None
        
    logger.info(f"Converting unit {neo_unit.name} to pyeurisko format")
    py_unit = EuriskoUnit(neo_unit.name)
    
    # Map slots
    for slot in neo_unit.slots.values():
        logger.debug(f"Converting slot {slot.name} of type {slot.type}")
        if slot.type == SlotType.CODE:
            # For code slots, create a rule using rule_factory
            try:
                # Try to get function from globals
                fn = globals()[slot.value] if isinstance(slot.value, str) else slot.value
                rule = rule_factory(fn)
                py_unit.set_prop(slot.name, rule)
                logger.debug(f"Successfully converted code slot {slot.name}")
            except Exception as e:
                logger.error(f"Error creating rule for {slot.name}: {e}")
        else:
            # For other slots, map directly
            py_unit.set_prop(slot.name, slot.value)
            logger.debug(f"Copied slot {slot.name}")
            
    return py_unit

def main():
    start_time = time.time()
    logger.info("Starting Neo-Eurisko")
    
    parser = argparse.ArgumentParser(description='Run Neo-Eurisko examples')
    parser.add_argument('--pyeurisko', action='store_true', 
                       help='Try to integrate with pyeurisko')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug logging')
    args = parser.parse_args()
    
    if args.debug:
        logger.setLevel(logging.DEBUG)
        
    # Initialize Neo-Eurisko
    logger.info("Initializing Neo-Eurisko system")
    eurisko = NeoEurisko()
    
    # Create and register test heuristic
    logger.info("Setting up test components")
    heuristic = create_number_theory_heuristic(eurisko)
    print(f"\nCreated heuristic: {heuristic.name}")
    
    # Create test unit
    test_unit = create_test_unit()
    eurisko.units[test_unit.name] = test_unit
    print(f"Created test unit: {test_unit.name}")
    
    # Apply heuristic
    logger.info("Applying heuristic to test unit")
    print("\nApplying heuristic...")
    result = eurisko.apply_heuristic(heuristic, test_unit)
    print(f"Result: {result}")
    
    # Show any new units created
    logger.info("Checking results")
    print("\nUnits after application:")
    for unit in eurisko.units.values():
        print(f"- {unit.name} (worth: {unit.worth})")
        
    # Try pyeurisko integration if requested
    if args.pyeurisko and HAVE_PYEURISKO:
        logger.info("Starting pyeurisko integration")
        print("\nConverting to pyeurisko format...")
        for unit in eurisko.units.values():
            py_unit = bridge_to_pyeurisko(unit)
            if py_unit:
                print(f"Converted {unit.name} to pyeurisko format")
                
    elapsed = time.time() - start_time
    logger.info(f"Neo-Eurisko run completed in {elapsed:.2f}s")
                
if __name__ == '__main__':
    main()
