"""H15 heuristic implementation: Find examples through multiple operations."""
from typing import Any, Dict, List, Optional, Set
import logging
from ..heuristics import rule_factory

logger = logging.getLogger(__name__)

def setup_h15(heuristic) -> None:
    """Configure H15: Find examples from multiple operations.
    
    This heuristic examines multiple operations that can produce examples
    of a concept, enabling more sophisticated example discovery by analyzing
    patterns across different sources. It builds on H10's capabilities
    by considering multiple operations simultaneously and tracking the
    provenance of each example.
    """
    heuristic.set_prop('worth', 700)
    heuristic.set_prop('english',
        "IF the current task is to find examples of a unit, and it is the "
        "range of multiple operations, THEN gather together the outputs of "
        "all I/O pairs across those operations.")
    heuristic.set_prop('abbrev', "Find examples from multiple operations")

    @rule_factory
    def if_potentially_relevant(rule, context):
        """Verify task is for finding examples with multiple sources."""
        task = context.get('task')
        unit = context.get('unit')
        
        if not task or not unit:
            return False
            
        if task.get('task_type') != 'find_examples':
            return False
            
        # Need multiple operations that produce this type
        operations = unit.get_prop('is_range_of', [])
        if len(operations) < 2:  # Need at least 2 operations
            return False
            
        context['source_ops'] = operations
        return True

    @rule_factory
    def then_compute(rule, context):
        """Find examples from multiple operation outputs."""
        unit = context.get('unit')
        source_ops = context.get('source_ops', [])
        
        if not all([unit, source_ops]):
            return False

        # Get outputs from all operations
        outputs_by_op = {}
        for op_name in source_ops:
            op = rule.unit_registry.get_unit(op_name)
            if not op:
                continue
                
            # Get applications and extract results
            applications = op.get_prop('applications', [])
            if not applications:
                continue
                
            outputs = []
            for app in applications:
                result = app.get('result')
                if result is not None:
                    outputs.append(result)
                    
            if outputs:
                outputs_by_op[op_name] = outputs

        if len(outputs_by_op) < 2:  # Need at least 2 operations with outputs
            return False

        # Analyze output patterns
        all_values = set()
        value_counts = {}
        op_patterns = {}
        
        for op_name, op_outputs in outputs_by_op.items():
            # Track unique values from this operation
            op_values = set(op_outputs)
            all_values.update(op_values)
            
            # Analyze value patterns for this operation
            op_patterns[op_name] = {
                'unique_values': len(op_values),
                'total_values': len(op_outputs),
                'value_types': {
                    type(val).__name__
                    for val in op_outputs
                }
            }
            
            # Update global value counts
            for val in op_outputs:
                value_counts[val] = value_counts.get(val, 0) + 1

        pattern_analysis = {
            'total_unique': len(all_values),
            'value_overlap': {
                val: count
                for val, count in value_counts.items()
                if count > 1  # Values produced by multiple ops
            },
            'operation_patterns': op_patterns
        }

        # Track new examples and their sources
        current_examples = set(unit.get_prop('examples', []))
        new_examples = set()
        example_sources = {}

        # Process outputs from each operation
        for op_name, outputs in outputs_by_op.items():
            for output in outputs:
                if output not in current_examples:
                    new_examples.add(output)
                    sources = example_sources.get(output, set())
                    sources.add(op_name)
                    example_sources[output] = sources

        if new_examples:
            context['task_results'] = context.get('task_results', {})
            context['task_results'].update({
                'new_values': list(new_examples),
                'example_sources': example_sources,
                'pattern_analysis': pattern_analysis,
                'source_operations': list(set(
                    source
                    for sources in example_sources.values()
                    for source in sources
                ))
            })
            return True

        return False

    @rule_factory
    def then_print_to_user(rule, context):
        """Report on examples found through multiple operations."""
        unit = context.get('unit')
        task_results = context.get('task_results', {})
        
        if not unit or not task_results:
            return False
            
        new_examples = task_results.get('new_values', [])
        example_sources = task_results.get('example_sources', {})
        pattern_analysis = task_results.get('pattern_analysis', {})
        
        if not new_examples:
            return False

        # Report new examples and their sources
        logger.info(
            f"\nFound {len(new_examples)} new examples for {unit.name} "
            f"through {len(pattern_analysis['operation_patterns'])} operations:"
        )
        
        for example in sorted(new_examples):
            sources = example_sources.get(example, set())
            logger.info(
                f"- {example} (from {', '.join(sorted(sources))})"
            )
            
        # Report any interesting patterns
        overlaps = pattern_analysis.get('value_overlap', {})
        if overlaps:
            logger.info("\nPattern Analysis:")
            logger.info(
                f"- {len(overlaps)} values produced by multiple operations"
            )
            
        return True