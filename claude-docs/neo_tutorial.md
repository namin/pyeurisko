# Neo-Eurisko Tutorial

This tutorial walks through using Neo-Eurisko, from basic usage to advanced features.

## Getting Started

### Installation
```bash
# Clone the repository
git clone https://github.com/your-username/pyeurisko.git
cd pyeurisko

# Install in development mode
pip install -e ".[dev]"
```

### Basic Usage
```python
from eurisko.neo import NeoEurisko, Unit, SlotType

# Create a Neo-Eurisko instance
eurisko = NeoEurisko()

# Create your first unit
unit = Unit("my-first-unit")
unit.add_slot("value", 42, SlotType.LIST)
eurisko.units[unit.name] = unit

# Run basic analysis
print(f"Created unit: {unit.name} with worth {unit.worth}")
```

## Pattern Discovery Example

Let's walk through discovering patterns in numerical sequences:

```python
# Create a unit with an interesting sequence
def create_sequence_unit():
    unit = Unit("geometric-sequence")
    # Powers of 2
    values = [2, 4, 8, 16, 32]
    for i, v in enumerate(values):
        unit.add_slot(f"v{i+1}", v, SlotType.LIST)
    return unit

# Create and register the unit
unit = create_sequence_unit()
eurisko.units[unit.name] = unit

# Create and apply pattern detection heuristic
from eurisko.neo import find_number_patterns
heuristic = eurisko.create_heuristic_from_function(find_number_patterns)
result = eurisko.apply_heuristic(heuristic, unit)

# Examine results
print("Discovered patterns:")
for pattern in result["patterns_found"]:
    print(f"- {pattern}")
print("\nDetails:")
for pattern, details in result["details"].items():
    print(f"\n{pattern}:")
    print(f"  Evidence: {details['evidence']}")
```

Expected output:
```
Discovered patterns:
- all_even
- powers_of_2
- geometric

Details:
all_even:
  Evidence: All numbers [2, 4, 8, 16, 32] are divisible by 2

powers_of_2:
  Evidence: Numbers are 2^[1, 2, 3, 4, 5]

geometric:
  Evidence: Common ratio of 2.00 between consecutive terms
```

## Creating Custom Patterns

You can extend Neo-Eurisko with your own pattern detectors:

```python
def detect_perfect_squares(target: Unit, eurisko: NeoEurisko) -> dict:
    """Detect sequences of perfect squares."""
    result = {"success": False, "patterns_found": [], "worth_generated": 0}
    
    # Get numerical values
    numbers = []
    for slot in target.slots.values():
        if isinstance(slot.value, (int, float)):
            numbers.append(slot.value)
            
    if len(numbers) < 2:
        return result
        
    # Check if numbers are perfect squares
    def is_perfect_square(n):
        root = int(n ** 0.5)
        return root * root == n
        
    if all(is_perfect_square(n) for n in numbers):
        result["success"] = True
        result["patterns_found"].append("perfect_squares")
        result["details"] = {
            "perfect_squares": {
                "confidence": 1.0,
                "roots": [int(n ** 0.5) for n in numbers],
                "evidence": f"Numbers are squares of {[int(n ** 0.5) for n in numbers]}"
            }
        }
        
        # Create specialized unit
        new_name = f"{target.name}-numeric-perfect_squares"
        specialized = Unit(new_name)
        specialized.worth = min(1000, target.worth + 100)
        specialized.add_slot("specializes", target.name, SlotType.UNIT)
        specialized.add_slot("pattern_details", 
                           result["details"]["perfect_squares"], 
                           SlotType.LIST)
        eurisko.units[new_name] = specialized
        result["worth_generated"] = 100
        
    return result

# Register and use your pattern detector
heuristic = eurisko.create_heuristic_from_function(detect_perfect_squares)

# Test with perfect squares
unit = Unit("square-sequence")
for i, v in enumerate([1, 4, 9, 16, 25]):
    unit.add_slot(f"v{i+1}", v, SlotType.LIST)
eurisko.units[unit.name] = unit

result = eurisko.apply_heuristic(heuristic, unit)
print(result["details"])
```

## Pattern Composition

Here's how to work with pattern composition:

```python
def analyze_mixed_patterns(unit: Unit, eurisko: NeoEurisko) -> dict:
    """Analyze how patterns combine in a sequence."""
    # First get individual patterns
    pattern_results = []
    for detector in [find_number_patterns, detect_perfect_squares]:
        heuristic = eurisko.create_heuristic_from_function(detector)
        result = eurisko.apply_heuristic(heuristic, unit)
        if result["success"]:
            pattern_results.append(result)
            
    # Look for compositions
    compositions = []
    if len(pattern_results) > 1:
        # Example: Perfect squares that are also even
        patterns = set()
        for result in pattern_results:
            patterns.update(result["patterns_found"])
            
        if "perfect_squares" in patterns and "all_even":
            compositions.append({
                "type": "even_perfect_squares",
                "components": ["perfect_squares", "all_even"],
                "evidence": "Numbers are both perfect squares and even"
            })
            
    return {
        "success": bool(compositions),
        "compositions": compositions
    }
```

## Debugging and Inspection

Neo-Eurisko provides several debugging tools:

### 1. Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Now you'll see detailed logs
result = eurisko.apply_heuristic(heuristic, unit)
```

### 2. Unit Inspection
```python
def inspect_unit(unit: Unit):
    """Print detailed unit information."""
    print(f"\nUnit: {unit.name} (worth: {unit.worth})")
    print("\nSlots:")
    for name, slot in unit.slots.items():
        print(f"  {name}: {slot.value} (type={slot.type.name})")
        if slot.meta:
            print(f"    metadata: {slot.meta}")
            
    print("\nRelationships:")
    if "specializes" in unit.slots:
        print(f"  Specializes: {unit.get_slot('specializes').value}")
    
    print("\nPatterns:")
    if "pattern_details" in unit.slots:
        details = unit.get_slot("pattern_details").value
        print(f"  {details}")
```

### 3. Pattern Verification
```python
def verify_pattern(unit: Unit, pattern: str):
    """Verify a claimed pattern in a unit."""
    numbers = []
    for slot in unit.slots.values():
        if isinstance(slot.value, (int, float)):
            numbers.append(slot.value)
            
    verifications = {
        "all_even": lambda nums: all(n % 2 == 0 for n in nums),
        "perfect_squares": lambda nums: all(int(n**0.5)**2 == n for n in nums),
        "geometric": lambda nums: len(set(
            nums[i+1]/nums[i] for i in range(len(nums)-1)
        )) == 1
    }
    
    if pattern in verifications:
        result = verifications[pattern](numbers)
        print(f"Pattern '{pattern}' verification: {result}")
        if not result:
            print(f"Failed on numbers: {numbers}")
    else:
        print(f"No verification rule for pattern: {pattern}")
```

## Advanced Topics

### 1. LLM Integration
```python
# The LLM can suggest pattern improvements
result = eurisko.llm.suggest_modifications(
    unit=heuristic,
    context="Pattern detector missing some obvious cases"
)
print(result)  # Get suggestions for improvement
```

### 2. Worth Calculation
```python
def calculate_pattern_worth(patterns: list, basic_worth: int = 500):
    """Calculate unit worth based on patterns."""
    # Rarity values (lower = rarer = more valuable)
    rarity = {
        "all_even": 0.5,      # Common
        "perfect_squares": 0.2,# Rare
        "geometric": 0.3      # Uncommon
    }
    
    # Base worth
    worth = basic_worth
    
    # Add value for each pattern
    for pattern in patterns:
        pattern_rarity = rarity.get(pattern, 0.4)
        worth += int((1 - pattern_rarity) * 200)
        
    # Bonus for multiple patterns
    if len(patterns) > 1:
        worth += 50 * len(patterns)
        
    return min(1000, worth)
```

## Error Handling

Neo-Eurisko is designed to fail gracefully:

```python
def safe_pattern_detection(unit: Unit, eurisko: NeoEurisko):
    """Demonstrate error handling."""
    try:
        result = eurisko.apply_heuristic(heuristic, unit)
        return result
    except Exception as e:
        logger.error(f"Pattern detection failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "patterns_found": [],
            "worth_generated": 0
        }
```

## Next Steps

1. Try creating more pattern detectors
2. Experiment with pattern composition
3. Add your own worth calculation rules
4. Explore LLM-guided evolution
5. Build more sophisticated debugging tools

## Common Issues

1. LLM Availability
   - Always check LLM connection
   - Use fallback patterns if LLM fails

2. Performance
   - Cache pattern results for large units
   - Use batch processing for many units

3. Pattern Validation
   - Always verify discovered patterns
   - Keep track of confidence levels

## Additional Resources

- Main documentation: [neo.md](neo.md)
- Source code: [eurisko/neo.py](eurisko/neo.py)
- Test suite: [eurisko/tests/test_patterns.py](eurisko/tests/test_patterns.py)
