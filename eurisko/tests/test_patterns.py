"""Pattern discovery and analysis tests for Neo-Eurisko."""
import logging
from typing import List, Dict, Any
from ..neo import NeoEurisko, Unit, SlotType

logger = logging.getLogger(__name__)

def create_test_units() -> List[Unit]:
    """Create a diverse set of test units with numerical patterns."""
    units = []
    
    # Simple sequence [4, 8, 16] - powers of 2, even, geometric
    simple = Unit("simple-numbers")
    simple.add_slot("value1", 4, SlotType.LIST)
    simple.add_slot("value2", 8, SlotType.LIST)
    simple.add_slot("value3", 16, SlotType.LIST)
    units.append(simple)
    
    # Fibonacci sequence [1, 1, 2, 3, 5, 8] - additive pattern
    fibonacci = Unit("fibonacci-numbers")
    for i, v in enumerate([1, 1, 2, 3, 5, 8]):
        fibonacci.add_slot(f"value{i+1}", v, SlotType.LIST)
    units.append(fibonacci)
    
    # Perfect squares [1, 4, 9, 16, 25] - quadratic pattern
    squares = Unit("square-numbers")
    for i, v in enumerate([1, 4, 9, 16, 25]):
        squares.add_slot(f"value{i+1}", v, SlotType.LIST)
    units.append(squares)
    
    # Mixed patterns [6, 12, 18, 24] - even, arithmetic (d=6), multiples of 6
    mixed = Unit("mixed-numbers")
    for i, v in enumerate([6, 12, 18, 24]):
        mixed.add_slot(f"value{i+1}", v, SlotType.LIST)
    units.append(mixed)
    
    return units

def test_patterns(debug: bool = False):
    """Run comprehensive pattern detection tests."""
    if debug:
        logger.setLevel(logging.DEBUG)
        
    logger.info("Initializing Neo-Eurisko pattern tests")
    eurisko = NeoEurisko()
    
    # Create and register test units
    test_units = create_test_units()
    logger.info(f"Created {len(test_units)} test units")
    
    results = []
    for unit in test_units:
        logger.info(f"\nAnalyzing patterns in {unit.name}")
        eurisko.units[unit.name] = unit
        
        # Create heuristic function
        from ..neomain import find_number_patterns
        heuristic = eurisko.create_heuristic_from_function(find_number_patterns)
        
        # Apply heuristic
        result = eurisko.apply_heuristic(heuristic, unit)
        results.append({
            'unit': unit.name,
            'patterns': result.get('patterns_found', []),
            'worth': result.get('worth_generated', 0),
            'details': result.get('details', {})
        })
    
    return results

def run_tests():
    """Run all pattern tests and display results."""
    results = test_patterns()
    
    print("\nPattern Detection Results:")
    print("=" * 50)
    for r in results:
        print(f"\nUnit: {r['unit']}")
        print(f"Patterns: {', '.join(r['patterns'])}")
        print(f"Worth Generated: {r['worth']}")
        if r['details']:
            print("Details:")
            for pattern, info in r['details'].items():
                print(f"  {pattern}: {info['evidence']}")
                
    return results

if __name__ == '__main__':
    run_tests()
