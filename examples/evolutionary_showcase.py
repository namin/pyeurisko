"""PyEurisko evolutionary showcase demonstrating heuristic discovery and evolution.

This script demonstrates PyEurisko's core capability of evolving its own heuristics
through observation and self-modification. It shows:
- Pattern discovery in mathematical sequences
- Heuristic performance evaluation and adaptation
- Meta-level reasoning about heuristic effectiveness
"""
import logging
from eurisko.main import Eurisko
from eurisko.tasks import Task
from eurisko.heuristics.base import Heuristic
from eurisko.unit import Unit

class SequenceUnit(Unit):
    """Unit representing a sequence of numbers to analyze."""
    
    def __init__(self, name, sequence):
        super().__init__(name)
        self.set_prop('isa', ['sequence'])
        self.set_prop('numbers', sequence)
        self.set_prop('worth', 500)

class PatternDiscoveryHeuristic(Heuristic):
    """Heuristic for discovering patterns in number sequences."""
    
    def __init__(self, name, description):
        super().__init__(name, description)
        self.set_prop('successes', 0)
        self.set_prop('attempts', 0)
    
    def is_relevant(self, unit):
        return 'sequence' in unit.get_prop('isa', [])
        
    def analyze_sequence(self, numbers):
        """Analyze a sequence of numbers to discover patterns."""
        if len(numbers) < 3:
            return {'type': 'unknown', 'confidence': 0}
            
        differences = []
        ratios = []
        
        for i in range(1, len(numbers)):
            differences.append(numbers[i] - numbers[i-1])
            if numbers[i-1] != 0:
                ratios.append(numbers[i] / numbers[i-1])
                
        # Check for arithmetic sequence
        if len(set(round(d, 6) for d in differences)) == 1:
            return {
                'type': 'arithmetic',
                'difference': differences[0],
                'confidence': 0.9
            }
            
        # Check for geometric sequence
        if len(set(round(r, 6) for r in ratios)) == 1:
            return {
                'type': 'geometric',
                'ratio': ratios[0],
                'confidence': 0.9
            }
            
        # Check for fibonacci-like sequence
        fib_like = True
        for i in range(2, len(numbers)):
            if abs((numbers[i] - (numbers[i-1] + numbers[i-2]))) > 0.0001:
                fib_like = False
                break
                
        if fib_like:
            return {
                'type': 'fibonacci',
                'confidence': 0.8
            }
            
        return {'type': 'unknown', 'confidence': 0}
        
    def apply(self, unit):
        sequence = unit.get_prop('numbers', [])
        if not sequence:
            return False
        
        self.set_prop('attempts', self.get_prop('attempts', 0) + 1)
        pattern = self.analyze_sequence(sequence)
        
        if pattern['confidence'] > 0.7:
            # Store the discovered pattern
            unit.set_prop('pattern_type', pattern['type'])
            unit.set_prop('confidence', pattern['confidence'])
            unit.set_prop('discovered_by', self.name)
            
            if pattern['type'] == 'arithmetic':
                unit.set_prop('difference', pattern['difference'])
            elif pattern['type'] == 'geometric':
                unit.set_prop('ratio', pattern['ratio'])
                
            # Increase worth based on confidence
            unit.set_prop('worth', 500 + int(pattern['confidence'] * 300))
            
            # Record success
            self.set_prop('successes', self.get_prop('successes', 0) + 1)
            return True
            
        return False

class HeuristicEvaluator(Heuristic):
    """Meta-heuristic that evaluates and modifies other heuristics."""
    
    def is_relevant(self, unit):
        return isinstance(unit, Heuristic)
        
    def apply(self, unit):
        if not isinstance(unit, Heuristic):
            return False
            
        attempts = unit.get_prop('attempts', 0)
        if attempts == 0:
            return False
            
        # Analyze heuristic performance
        successes = unit.get_prop('successes', 0)
        success_rate = successes / attempts
        current_worth = unit.get_prop('worth', 500)
        
        # Adjust worth based on performance
        if success_rate > 0.8:
            new_worth = min(1000, current_worth * 1.2)
            unit.set_prop('worth', new_worth)
            logging.getLogger('PyEurisko-Evolution').info(
                f"Increased worth of {unit.name} to {new_worth} "
                f"(success rate: {success_rate:.2f})"
            )
        elif success_rate < 0.2:
            new_worth = max(100, current_worth * 0.8)
            unit.set_prop('worth', new_worth)
            logging.getLogger('PyEurisko-Evolution').info(
                f"Decreased worth of {unit.name} to {new_worth} "
                f"(success rate: {success_rate:.2f})"
            )
            
        return True

def run_evolutionary_showcase():
    """Run a showcase of PyEurisko's evolutionary capabilities."""
    # Setup logging
    logging.basicConfig(level=logging.INFO,
                       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger('PyEurisko-Evolution')
    
    # Initialize system
    logger.info("Initializing PyEurisko system with evolutionary capabilities...")
    eurisko = Eurisko(verbosity=1)
    eurisko.initialize()
    
    # Register core heuristics
    pattern_discovery = PatternDiscoveryHeuristic(
        "H-PatternDiscovery",
        "Discovers patterns in number sequences"
    )
    pattern_discovery.set_prop('worth', 600)
    eurisko.unit_registry.register(pattern_discovery)
    
    evaluator = HeuristicEvaluator(
        "H-Evaluator",
        "Evaluates and modifies heuristic performance"
    )
    evaluator.set_prop('worth', 700)
    eurisko.unit_registry.register(evaluator)
    
    # Create test sequences
    test_sequences = [
        ([1, 1, 2, 3, 5, 8, 13], "fibonacci_like"),
        ([2, 4, 6, 8, 10, 12], "arithmetic"),
        ([2, 4, 8, 16, 32, 64], "geometric"),
        ([1, 3, 7, 9, 11], "random"),  # Should fail to find pattern
    ]
    
    logger.info("\nCreating sequence units for analysis...")
    sequence_units = []
    for sequence, name in test_sequences:
        unit = SequenceUnit(f"sequence_{name}", sequence)
        eurisko.unit_registry.register(unit)
        sequence_units.append(unit)
        logger.info(f"Created sequence unit: {unit.name}")
        
        # Create analysis task
        task = Task(
            800,  # priority
            unit.name,  # unit_name 
            'analyze',  # slot_name
            [f'Analyze pattern in {name} sequence']  # reasons
        )
        eurisko.task_manager.add_task(task)
    
    # Add evaluation task for the pattern discovery heuristic
    eval_task = Task(
        900,  # priority
        pattern_discovery.name,  # unit_name
        'evaluate',  # slot_name
        ['Evaluate pattern discovery performance']  # reasons
    )
    eurisko.task_manager.add_task(eval_task)
    
    # Run system
    logger.info("\nRunning PyEurisko evolution cycle...")
    initial_units = len(eurisko.unit_registry.all_units())
    eurisko.run(eternal_mode=False)
    final_units = len(eurisko.unit_registry.all_units())
    
    # Report results
    logger.info("\nEvolution cycle complete.")
    logger.info(f"System state:")
    logger.info(f"- Initial units: {initial_units}")
    logger.info(f"- Final units: {final_units}")
    logger.info(f"- Tasks processed: {eurisko.task_manager.task_num}")
    
    logger.info("\nPattern discovery results:")
    for unit in sequence_units:
        logger.info(f"\nSequence: {unit.name}")
        logger.info(f"- Numbers: {unit.get_prop('numbers')}")
        pattern_type = unit.get_prop('pattern_type')
        confidence = unit.get_prop('confidence')
        logger.info(f"- Pattern type: {pattern_type if pattern_type else 'none'}")
        logger.info(f"- Confidence: {confidence if confidence else 0:.2f}")
        if pattern_type == 'arithmetic':
            logger.info(f"- Difference: {unit.get_prop('difference')}")
        elif pattern_type == 'geometric':
            logger.info(f"- Ratio: {unit.get_prop('ratio')}")
    
    # Report heuristic performance
    logger.info("\nHeuristic performance:")
    h_pattern = eurisko.unit_registry.get_unit('H-PatternDiscovery')
    attempts = h_pattern.get_prop('attempts')
    successes = h_pattern.get_prop('successes')
    if attempts:
        success_rate = successes / attempts if successes else 0
        logger.info(f"Pattern Discovery Heuristic:")
        logger.info(f"- Attempts: {attempts}")
        logger.info(f"- Successes: {successes if successes else 0}")
        logger.info(f"- Success rate: {success_rate:.2f}")
        logger.info(f"- Final worth: {h_pattern.get_prop('worth')}")

if __name__ == '__main__':
    run_evolutionary_showcase()