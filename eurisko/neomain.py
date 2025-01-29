"""Neo-Eurisko main execution script."""
import os
import logging
from .neo import NeoEurisko, Unit, SlotType
from typing import Optional
import argparse

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

def find_number_patterns(target: Unit, eurisko: NeoEurisko) -> dict:
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
    details = {}
    
    # Check if all numbers are even
    if all(n % 2 == 0 for n in numbers):
        patterns.append("all_even")
        details["all_even"] = {
            "confidence": 1.0,
            "evidence": f"All numbers ({numbers}) are divisible by 2"
        }
        
    # Check if all numbers are powers of 2
    def is_power_2(n):
        return n > 0 and (n & (n - 1)) == 0
    if all(is_power_2(n) for n in numbers):
        patterns.append("powers_of_2")
        powers = [n.bit_length() - 1 for n in numbers]
        details["powers_of_2"] = {
            "confidence": 1.0,
            "powers": powers,
            "evidence": f"Numbers are 2^{powers}"
        }
        
    # Check for arithmetic sequence
    if len(numbers) > 2:
        diffs = [numbers[i+1] - numbers[i] for i in range(len(numbers)-1)]
        if len(set(diffs)) == 1:
            patterns.append("arithmetic")
            details["arithmetic"] = {
                "confidence": 1.0,
                "common_difference": diffs[0],
                "evidence": f"Common difference of {diffs[0]} between consecutive terms"
            }
            
    # Check for geometric sequence
    if len(numbers) > 2 and all(n > 0 for n in numbers):
        ratios = [numbers[i+1]/numbers[i] for i in range(len(numbers)-1)]
        if len(set(f"{r:.6f}" for r in ratios)) == 1:  # Allow for float imprecision
            patterns.append("geometric")
            details["geometric"] = {
                "confidence": 1.0,
                "common_ratio": ratios[0],
                "evidence": f"Common ratio of {ratios[0]:.2f} between consecutive terms"
            }
    
    # If patterns found, create specialized units
    for pattern in patterns:
        new_name = f"{target.name}-numeric-{pattern}"
        specialized = Unit(new_name)
        specialized.worth = min(1000, target.worth + 100)
        specialized.add_slot("specializes", target.name, SlotType.UNIT)
        specialized.add_slot("pattern_found", pattern, SlotType.TEXT)
        specialized.add_slot("pattern_details", details[pattern], SlotType.LIST)
        
        # Add the numbers that show this pattern
        specialized.add_slot("examples", numbers, SlotType.LIST)
        
        eurisko.units[new_name] = specialized
        result["worth_generated"] += 100
        
    if patterns:
        result["success"] = True
        result["patterns_found"] = patterns
        result["details"] = details
        
    return result

def create_number_theory_heuristic(eurisko: NeoEurisko) -> Unit:
    """Create a simple number theory heuristic to test the system."""
    return eurisko.create_heuristic_from_function(find_number_patterns)

def create_test_unit() -> Unit:
    """Create a test unit with some numerical properties."""
    unit = Unit("test-numbers")
    unit.add_slot("value1", 4, SlotType.LIST)
    unit.add_slot("value2", 8, SlotType.LIST)
    unit.add_slot("value3", 16, SlotType.LIST)
    return unit

def bridge_to_pyeurisko(neo_unit: Unit) -> Optional[EuriskoUnit]:
    """Convert a neo-eurisko unit to pyeurisko format if available."""
    if not HAVE_PYEURISKO:
        return None
        
    py_unit = EuriskoUnit(neo_unit.name)
    
    # Map slots
    for slot in neo_unit.slots.values():
        if slot.type == SlotType.CODE:
            try:
                fn = globals()[slot.value] if isinstance(slot.value, str) else slot.value
                rule = rule_factory(fn)
                py_unit.set_prop(slot.name, rule)
            except Exception as e:
                logger.error(f"Error creating rule for {slot.name}: {e}")
        else:
            py_unit.set_prop(slot.name, slot.value)
            
    return py_unit

def main():
    parser = argparse.ArgumentParser(description='Run Neo-Eurisko examples')
    parser.add_argument('--pyeurisko', action='store_true', 
                       help='Try to integrate with pyeurisko')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug logging')
    parser.add_argument('--test-patterns', action='store_true',
                       help='Run pattern detection tests')
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info("Starting Neo-Eurisko")
    
    # Initialize Neo-Eurisko
    logger.info("Initializing Neo-Eurisko system")
    eurisko = NeoEurisko()
    
    if args.test_patterns:
        from .tests.test_patterns import run_tests
        run_tests()
    else:
        # Regular run
        logger.info("Setting up test components")
        
        # Create and register test heuristic
        heuristic = create_number_theory_heuristic(eurisko)
        print(f"\nCreated heuristic: {heuristic.name}")
        
        # Create test unit
        test_unit = create_test_unit()
        eurisko.units[test_unit.name] = test_unit
        print(f"Created test unit: {test_unit.name}")
        
        # Apply heuristic
        print("\nApplying heuristic...")
        logger.info("Applying heuristic to test unit")
        result = eurisko.apply_heuristic(heuristic, test_unit)
        print(f"Result: {result}")
        
        # Show any new units created
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

if __name__ == '__main__':
    main()