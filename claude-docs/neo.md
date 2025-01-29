# Neo-Eurisko Design Document

## Overview
Neo-Eurisko reimagines Lenat's Eurisko in Python, using LLMs to replace Interlisp's reflection capabilities. The core idea is to maintain Eurisko's self-improving nature while making the system more transparent and inspectable.

## Key Features By Example

### Inspectable System State
The system maintains inspectable state at all levels. For example:

```python
# 1. Examine a unit's complete state
>>> unit = eurisko.units["test-numbers"]
>>> print(unit)
Unit(name='test-numbers', worth=500)
  Slots:
    value1: 4 (type=LIST)
    value2: 8 (type=LIST)
    value3: 16 (type=LIST)

# 2. Track heuristic application
>>> result = eurisko.apply_heuristic(heuristic, unit)
2025-01-29 18:13:45,597 - INFO - Applying find_number_patterns to test-numbers
2025-01-29 18:13:45,599 - INFO - Found patterns: ['all_even', 'powers_of_2', 'geometric']
2025-01-29 18:13:45,599 - INFO - Created specialized unit: test-numbers-numeric-powers_of_2

# 3. Examine evolution history
>>> unit = eurisko.units["test-numbers-numeric-powers_of_2"]
>>> print(unit.get_slot("pattern_details").value)
{
  "confidence": 1.0,
  "powers": [2, 3, 4],
  "evidence": "Numbers are 2^[2, 3, 4]"
}
```

### Pattern Discovery Example
Here's a concrete example of the system discovering multiple patterns:

```python
# Original unit with numerical values
unit = Unit("sequence")
unit.add_slot("v1", 6, SlotType.LIST)
unit.add_slot("v2", 12, SlotType.LIST)
unit.add_slot("v3", 18, SlotType.LIST)
unit.add_slot("v4", 24, SlotType.LIST)

# Apply pattern detection
result = eurisko.apply_heuristic(pattern_heuristic, unit)

# Discovered patterns:
{
  "patterns_found": [
    "all_even",
    "arithmetic",
    "multiples_of_6"
  ],
  "details": {
    "all_even": {
      "confidence": 1.0,
      "evidence": "All numbers [6, 12, 18, 24] divisible by 2"
    },
    "arithmetic": {
      "confidence": 1.0,
      "common_difference": 6,
      "evidence": "Common difference of 6 between consecutive terms"
    },
    "multiples_of_6": {
      "confidence": 1.0,
      "evidence": "All numbers divisible by 6"
    }
  }
}

# Created specialized units
- sequence-numeric-all_even
- sequence-numeric-arithmetic
- sequence-numeric-multiples_of_6
```

### Pattern Composition
Pattern composition allows the system to recognize how patterns interact and combine. For example:

1. Basic Pattern: All numbers are even
2. Basic Pattern: Numbers form arithmetic sequence
3. Composed Pattern: "Even arithmetic sequence with step 6"

The system tracks these relationships:
```python
>>> unit = eurisko.units["sequence-numeric-composed"]
>>> print(unit.get_slot("pattern_composition").value)
{
  "type": "composition",
  "components": ["all_even", "arithmetic"],
  "constraints": {
    "arithmetic": {"step": 6},
    "all_even": {"validity": "all"}
  },
  "emergence": {
    "discovered": "multiples_of_6",
    "evidence": "Step size 6 combined with all-even property"
  }
}
```

### LLM-Guided Evolution
When a heuristic performs poorly, the system uses LLMs to suggest improvements:

```python
# Original heuristic with poor performance
def find_patterns(unit):
    numbers = get_numbers(unit)
    return check_even(numbers)

# LLM analysis
"This heuristic only checks for even numbers. Consider:
1. Add arithmetic sequence detection
2. Add geometric sequence detection
3. Add validation for minimum sequence length"

# Evolved heuristic
def find_patterns_v2(unit):
    numbers = get_numbers(unit)
    if len(numbers) < 2:
        return {"success": False, "reason": "Too few numbers"}
        
    patterns = []
    if check_even(numbers):
        patterns.append("even")
    if check_arithmetic(numbers):
        patterns.append("arithmetic")
    if check_geometric(numbers):
        patterns.append("geometric")
    return {"success": True, "patterns": patterns}
```

### Interactive Debugging
The system provides multiple ways to debug and understand its operation:

1. Logging with context:
```python
2025-01-29 18:13:45,597 - DEBUG - Starting pattern analysis for unit: sequence
2025-01-29 18:13:45,598 - DEBUG - Found numerical values: [6, 12, 18, 24]
2025-01-29 18:13:45,598 - INFO  - Detected pattern: arithmetic (confidence: 1.0)
2025-01-29 18:13:45,599 - INFO  - Creating specialized unit: sequence-numeric-arithmetic
```

2. Pattern Evidence:
```python
>>> unit = eurisko.units["sequence-numeric-arithmetic"]
>>> print(unit.get_slot("evidence").value)
{
  "type": "arithmetic_sequence",
  "values": [6, 12, 18, 24],
  "properties": {
    "first_term": 6,
    "common_difference": 6,
    "terms": 4
  },
  "validation": {
    "differences": [6, 6, 6],
    "regularity": "perfect"
  }
}
```

3. Worth Calculation:
```python
>>> print(unit.get_slot("worth_calculation").value)
{
  "base_worth": 500,
  "adjustments": [
    {"type": "pattern_rarity", "value": 100},
    {"type": "composition_bonus", "value": 50},
    {"type": "evidence_quality", "value": 50}
  ],
  "final_worth": 700
}
```

### Extensible Pattern Types
The system can be extended with new pattern types:

```python
@pattern_detector
def detect_fibonacci(numbers: List[int]) -> PatternResult:
    """Detect Fibonacci-like sequences."""
    if len(numbers) < 3:
        return PatternResult(success=False)
        
    is_fibonacci = all(
        numbers[i+2] == numbers[i] + numbers[i+1]
        for i in range(len(numbers)-2)
    )
    
    if is_fibonacci:
        return PatternResult(
            success=True,
            pattern_type="fibonacci",
            evidence={
                "terms": numbers,
                "verification": [
                    f"{numbers[i]} + {numbers[i+1]} = {numbers[i+2]}"
                    for i in range(len(numbers)-2)
                ]
            }
        )
    return PatternResult(success=False)
```

## Current Limitations

1. Pattern Types
- Currently focused on numerical patterns
- Limited to single-sequence patterns
- No cross-unit pattern detection

2. Heuristic Evolution
- LLM suggestions need human validation
- No automatic code generation yet
- Limited to simple code modifications

3. Performance
- LLM calls can be slow
- Pattern detection is compute-intensive
- No pattern caching yet

## Future Features

1. Advanced Pattern Detection
- Cross-unit pattern discovery
- Temporal patterns in unit evolution
- Meta-patterns in heuristic behavior

2. Autonomous Evolution
- Self-modifying heuristics
- Automatic code generation
- Safety-bounded evolution

3. Performance Optimization
- Pattern result caching
- Parallel pattern detection
- Incremental pattern updates

## Development Roadmap

### Phase 1 (Current)
- ✓ Basic numerical patterns
- ✓ Simple pattern composition
- ✓ LLM integration
- ✓ Logging and inspection

### Phase 2 (In Progress)
- Richer pattern types
- Better composition rules
- Improved worth calculation
- Enhanced debugging tools

### Phase 3 (Planned)
- Cross-unit patterns
- Automatic code generation
- Pattern caching
- Performance optimization
