"""Task type definitions and compatibility mappings."""

# Map of task types to compatible heuristic types
TASK_HEURISTIC_COMPATIBILITY = {
    'application_discovery': [
        'application_finder',
        'pattern_matcher',
        'value_generator',
        'algorithm_specializer'
    ],
    'pattern_analysis': [
        'pattern_finder',
        'data_analyzer',
        'value_generalizer'
    ],
    'analysis': [
        'analyzer',
        'value_generator',
        'pattern_finder',
        'relationship_discoverer'
    ],
    'examination': [
        'examiner',
        'analyzer',
        'value_generalizer',
        'pattern_finder'
    ],
    'relationship_discovery': [
        'relationship_finder',
        'pattern_matcher',
        'value_analyzer'
    ],
    'find_applications': [
        'application_finder',
        'value_generator',
        'pattern_matcher'
    ],
    'specialization': [
        'specializer',
        'value_generator',
        'pattern_matcher'
    ],
    'value_generation': [
        'value_generator',
        'application_finder',
        'algorithm_specializer'
    ]
}

# Map of heuristic types to their base capabilities
HEURISTIC_CAPABILITIES = {
    'application_finder': {
        'can_generate_values': True,
        'can_find_patterns': True,
        'requires_existing_applications': False
    },
    'pattern_finder': {
        'can_find_patterns': True,
        'can_generalize': True,
        'requires_existing_values': True
    },
    'value_generator': {
        'can_generate_values': True,
        'can_modify_existing': True,
        'requires_algorithm': True
    },
    'analyzer': {
        'can_analyze': True,
        'can_find_patterns': True,
        'requires_existing_values': True
    },
    'relationship_finder': {
        'can_find_relationships': True,
        'can_analyze': True,
        'requires_multiple_units': True
    },
    'specializer': {
        'can_specialize': True,
        'can_generate_values': True,
        'requires_existing_values': True
    },
    'value_analyzer': {
        'can_analyze': True,
        'can_find_patterns': True,
        'requires_existing_values': True
    }
}