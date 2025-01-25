# PyEurisko

PyEurisko is a Python implementation inspired by Douglas Lenat's Eurisko system, designed for heuristic discovery and automated reasoning. The system implements core concepts from the original Eurisko while leveraging modern Python features and design patterns.

## Installation

For development with testing tools:

```bash
pip install -e ".[dev]"
```

For regular installation:

```bash
pip install -e .
```

## Core Concepts

PyEurisko implements several key concepts from the original Eurisko system:

### Units
Units are the fundamental objects in the system, representing concepts, rules, and data. Each unit has:
- Properties stored in a flexible property list
- Worth/importance value
- Category memberships through ISA relationships
- Specialization and generalization relationships

### Slots
Slots define the types and behaviors of properties that units can have:
- Data type validation
- Inheritance relationships
- Criterial vs non-criterial distinctions
- Copy behavior during unit creation

### Heuristics
Heuristics are specialized units that implement reasoning rules:
- Relevance checking mechanisms
- Multi-phase execution
- Performance tracking
- Subsumption relationships

### Tasks
Tasks manage the system's work queue:
- Priority-based scheduling
- Task dependencies
- Result tracking
- Resource management

## Project Structure

```
pyeurisko/
├── eurisko/                     # Core package
│   ├── __init__.py             # Package initialization
│   ├── interfaces.py           # Base classes and interfaces
│   ├── main.py                 # System initialization and control
│   ├── slots.py                # Slot management system
│   ├── unit.py                 # Unit implementation
│   ├── tasks.py                # Task scheduling system
│   ├── heuristics.py           # Heuristic rule system
│   └── heuristics/             # Individual heuristic implementations
│       ├── __init__.py         # Heuristics package initialization
│       ├── base.py             # Base heuristic classes
│       ├── registry.py         # Heuristic registry system
│       └── h1.py - h15.py      # Individual heuristic implementations
│
├── tests/                      # Test suite
│   ├── test_main.py            # System tests
│   ├── test_slots.py           # Slot tests
│   ├── test_tasks.py           # Task system tests
│   ├── test_unit.py            # Unit tests
│   ├── test_heuristics.py      # Basic heuristic tests
│   ├── test_heuristics_advanced.py    # Advanced heuristic tests
│   └── test_heuristics_prevention.py  # Prevention heuristic tests
│
├── examples/                   # Usage examples
│   └── basic_demo.py           # Basic demonstration
│
├── requirements.txt            # Project dependencies
├── setup.py                    # Package configuration
├── RUN.md                      # Setup and run instructions
└── README.md                   # Documentation
```

## Key Components

### Unit System (unit.py)
- EuriskoObject base class
- Property management
- Relationship tracking
- Unit registry

### Slot System (slots.py)
- Slot definition and validation
- Property type system
- Inheritance management
- Slot registry

### Task System (tasks.py)
- Priority queue implementation
- Task execution framework
- Resource management
- Result tracking

### Heuristic System (heuristics/)
- Base heuristic classes and interfaces
- Comprehensive registry system
- Performance monitoring and tracking
- Relevance checking mechanisms
- Core heuristics implementation (H1-H15)
- Advanced reasoning capabilities
- Prevention and optimization strategies

## Usage Examples

### Creating and Using Units

```python
from eurisko.unit import Unit
from eurisko.slots import SlotRegistry

# Create a unit
unit = Unit("example_unit", worth=500)
unit.set_prop("isa", ["category"])

# Add properties
unit.set_prop("examples", ["example1", "example2"])
unit.add_prop("generalizations", "parent_concept")
```

### Defining Heuristics

```python
from eurisko.heuristics import Heuristic

# Create a heuristic
heuristic = Heuristic("example_heuristic", 
                     "Example heuristic description")

# Define relevance checks
heuristic.set_prop("if_potentially_relevant", 
                  lambda ctx: ctx.get('value', 0) > 0)

# Define actions
heuristic.set_prop("then_compute", 
                  lambda ctx: ctx['value'] * 2)
```

### Task Processing

```python
from eurisko.tasks import Task, TaskManager

# Create a task
task = Task(priority=500,
           unit_name="example_unit",
           slot_name="examples",
           reasons=["Finding new examples"])

# Add to task manager
manager = TaskManager()
manager.add_task(task)

# Process tasks
manager.process_agenda()
```

## Testing

Run the test suite:

```bash
pytest tests/
```

Test coverage report:

```bash
pytest tests/ --cov=eurisko
```

## Development

### Requirements

- Python 3.6+
- pytest for testing
- pytest-cov for coverage reporting

### Development Installation

```bash
pip install -e ".[dev]"
```

## License

MIT License

## Contributing

Contributions are welcome. Please ensure:
- Tests pass and coverage maintained
- Documentation updated
- Code follows project style

## Acknowledgments

Based on Douglas Lenat's original Eurisko system, [EUR](https://github.com/white-flame/eurisko/wiki).
Developed by Claude.ai Desktop based on [namin/eurisclo](https://github.com/namin/eurisclo),
using [the filesystem MCP server](https://github.com/namin/servers/tree/exec-reentrant/src/filesystem).