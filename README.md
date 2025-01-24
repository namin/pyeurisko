# PyEurisko

PyEurisko is a Python implementation inspired by Douglas Lenat's Eurisko system, designed for heuristic discovery and automated reasoning. The system provides a flexible framework for defining units, slots, and tasks that can be used to model and solve complex problems.

## Installation

To install PyEurisko with development dependencies:

```bash
pip install -e ".[dev]"
```

For regular installation without development tools:

```bash
pip install -e .
```

## Features

- **Unit System**: Flexible object system with dynamic properties
- **Slot Management**: Customizable property definitions with inheritance
- **Task Framework**: Priority-based task scheduling and execution
- **Heuristic Discovery**: Framework for automated learning and optimization

## Usage

### Basic Example

Here's how to run the basic demonstration:

```bash
python examples/basic_demo.py
```

This example demonstrates:
- System initialization
- Task creation and execution
- Basic unit and slot management

The demo processes a simple Fibonacci-related task and displays the final system state, including registered units, slots, and completed tasks.

### Core System

To run the core system:

```bash
python -m eurisko.main
```

The core system initializes with basic components and can be extended for specific use cases.

## Project Structure

```
pyeurisko/
├── eurisko/
│   ├── main.py      # Core system implementation
│   ├── slots.py     # Slot management
│   ├── tasks.py     # Task scheduling and execution
│   └── unit.py      # Unit system implementation
├── examples/
│   └── basic_demo.py # Basic usage demonstration
└── tests/           # Comprehensive test suite
```

## Testing

To run the test suite:

```bash
pytest tests/
```

The test suite includes:
- Unit tests for core functionality
- Integration tests for system components
- Coverage reporting

## Development

### Requirements

- Python 3.6+
- pytest for testing
- pytest-cov for coverage reporting

### Development Installation

Install with development dependencies:

```bash
pip install -e ".[dev]"
```

## License

[License information to be added]

## Contributing

[Contribution guidelines to be added]

## Acknowledgments

Inspired by Douglas Lenat's original Eurisko system.
