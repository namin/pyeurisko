# Heuristics System

The heuristics system implements Eurisko's core learning mechanisms. Each heuristic is a specialized rule that identifies opportunities for learning and guides the system's exploration of its concept space.

## Design Pattern

Heuristics follow a rule-factory pattern that combines setup-time and runtime behavior:

```python
@rule_factory
def if_working_on_task(rule, context):
    # Rule logic here
    return True/False
```

Each heuristic has a setup function that configures properties and rule functions. Rule functions receive both the rule object (for accessing setup-time state) and a context dictionary (for runtime state).

## Rule Types

- `if_working_on_task`: Checks if the heuristic applies to current task
- `if_potentially_relevant`: Initial quick check for relevance
- `if_truly_relevant`: Deeper relevance analysis
- `then_compute`: Main computation logic
- `then_print_to_user`: Logging and explanation
- `then_add_to_agenda`: Creates new tasks
- `then_conjecture`: Forms new hypotheses
- `then_define_new_concepts`: Creates new units

## Heuristic Categories

1. Core Discovery (H1-H5)
   - Identify opportunities for concept specialization and generalization
   - Guide exploration of the concept space

2. Operation Analysis (H6-H10)
   - Compare and analyze operations
   - Find patterns in operation behavior

3. Pattern Recognition (H11-H15)
   - Detect patterns across examples and applications
   - Guide systematic exploration

4. Concept Refinement (H16-H20)
   - Evaluate concept worth
   - Guide concept improvement

5. Meta-Learning (H21-H23)
   - Learn from the system's own behavior
   - Adjust exploration strategies

See the [Task Manager](../tasks/README.md) for details on how heuristics interact with tasks.
