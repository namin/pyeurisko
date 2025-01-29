# Neo-Eurisko Design Document

## Overview
Neo-Eurisko is a Python reimagining of Lenat's original Eurisko system, designed to explore how modern LLMs can replace the reflection capabilities that were originally provided by Interlisp. The goal is to maintain Eurisko's core ideas about self-improving heuristics while leveraging modern tools and practices.

## Core Concepts

### Units
- Basic building blocks, similar to original Eurisko
- Each unit has:
  - Name (string identifier)
  - Slots (key-value storage)
  - Worth (numeric value 0-1000)
- Units can represent:
  - Heuristics (executable code)
  - Concepts (collections of properties)
  - Patterns (discovered regularities)

### Slots
- Typed storage mechanism
- Four fundamental types:
  - CODE: Executable Python code
  - TEXT: Natural language descriptions
  - LIST: Collections of values
  - UNIT: References to other units
- Slots carry metadata to support reflection

### LLM Integration
- LLMs replace Interlisp's reflection capabilities
- Used for:
  - Code analysis
  - Pattern discovery
  - Heuristic evolution
  - Success criteria evaluation
- Always has fallback behavior if LLM fails

## Key Components

### NeoEurisko Class
- Central system coordinator
- Maintains unit registry
- Manages heuristic application
- Coordinates LLM interactions

### EuriskoLLM Class
- Handles all LLM interactions
- Provides robust error handling
- Ensures consistent JSON responses
- Maintains default responses for failures

### Unit Class
- Immutable after creation (except for slots)
- Maintains type safety
- Provides slot access methods
- Tracks worth and relationships

## Design Principles

### 1. Robustness
- System should never crash
- Graceful degradation when LLM fails
- Default behaviors for all operations
- Comprehensive error handling

### 2. Type Safety
- All slots have explicit types
- Type checking on slot assignment
- Safe execution of code slots
- Clean separation of concerns

### 3. Debuggability
- Comprehensive logging
- Clear error messages
- Traceable execution paths
- Inspectable state

### 4. Extensibility
- Easy to add new slot types
- Pluggable LLM backend
- Extensible heuristic system
- Modular design

## Core Invariants

1. Unit Identity
   - Names are unique
   - Worth is always 0-1000
   - Must have at least one slot

2. Slot Consistency
   - Values match declared types
   - No null values (empty containers okay)
   - Metadata always present

3. Heuristic Execution
   - Must return result dictionary
   - Must not modify other units directly
   - Must maintain atomicity

4. LLM Integration
   - Must have fallback behavior
   - Must parse responses safely
   - Must validate outputs

## Integration with pyeurisko

### Bridge Mechanism
- Converts Neo units to pyeurisko units
- Maintains slot mappings
- Preserves relationships
- Handles rule conversion

### Compatibility Layer
- Optional pyeurisko dependency
- Clean fallback to standalone
- Consistent API surface
- Type compatibility

## Current Focus Areas

1. Pattern Discovery
   - Numerical pattern detection
   - Pattern composition
   - Worth calculation
   - Evidence tracking

2. Heuristic Evolution
   - Performance tracking
   - LLM-guided modification
   - Success criteria
   - Combination detection

3. Testing Infrastructure
   - Unit test suite
   - Pattern test cases
   - Integration tests
   - Performance benchmarks

## Future Directions

1. Enhanced Pattern Types
   - More numerical patterns
   - Structural patterns
   - Relationship patterns
   - Meta-patterns

2. Deeper LLM Integration
   - Pattern discovery
   - Heuristic generation
   - Code improvement
   - Concept learning

3. Better pyeurisko Integration
   - Two-way conversion
   - Shared heuristics
   - Compatible worth system
   - Event synchronization

## Command Line Interface

```bash
# Basic usage
python -m eurisko.neomain

# Run pattern tests
python -m eurisko.neomain --test-patterns

# Enable debug logging
python -m eurisko.neomain --debug

# Enable pyeurisko integration
python -m eurisko.neomain --pyeurisko
```

## Project Structure
```
eurisko/
├── __init__.py
├── neo.py          # Core implementation
├── neomain.py      # CLI and runner
├── llm.py          # LLM integration
└── tests/
    ├── __init__.py
    └── test_patterns.py
```

## Development Guidelines

1. Always maintain fallbacks
2. Add comprehensive logging
3. Keep LLM interactions isolated
4. Maintain type safety
5. Write clear documentation
6. Include test cases
7. Consider failure modes
8. Preserve Eurisko's spirit

## Version Goals

### v0.1 (Current)
- Basic unit system
- Simple pattern discovery
- LLM integration
- Test framework

### v0.2 (Planned)
- More pattern types
- Better heuristic evolution
- Improved pyeurisko integration
- Enhanced testing

### v0.3 (Future)
- Pattern composition
- Automatic heuristic generation
- Deep learning integration
- Performance optimization
