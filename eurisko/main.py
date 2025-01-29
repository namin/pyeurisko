"""Main entry point for PyEurisko."""

from func_timeout import func_timeout, FunctionTimedOut
import argparse
import logging
from dataclasses import dataclass, field
import time
from typing import Optional, Dict, List, Set, Tuple
from .heuristics import initialize_all_heuristics
from .units import Unit, UnitRegistry, initialize_all_units
from .slots import SlotRegistry, initialize_all_slots
from .tasks import Task, TaskManager, generate_initial_tasks, generate_ongoing_tasks

def cur_time():
    return int(time.time())  # Current time in seconds since epoch

def setup_logging(verbosity: int):
    """Configure logging based on verbosity."""
    log_level = logging.DEBUG if verbosity > 1 else logging.INFO

    # Clear existing handlers
    root = logging.getLogger()
    for handler in root.handlers[:]:
        root.removeHandler(handler)

    # Configure root logger
    logging.basicConfig(
        format='%(levelname)s - %(name)s - %(message)s',
        level=log_level,
        force=True
    )

class Eurisko:
    """Main Eurisko system class."""
    def __init__(self, verbosity):
        self.verbosity = verbosity
        UnitRegistry.reset_instance()
        self.unit_registry = UnitRegistry.get_instance()
        self.slot_registry = SlotRegistry()
        self.task_manager = TaskManager()
        self.task_manager.verbosity = verbosity
        self.task_manager.cycle_start_time = cur_time()
        setup_logging(verbosity)
        self.logger = logging.getLogger(__name__)

    def initialize(self) -> None:
        """Initialize the core concepts and slots."""
        initialize_all_slots(self.slot_registry)
        initialize_all_units(self.unit_registry)
        initialize_all_heuristics(self.unit_registry)
        self.initialize_test_applications(self.unit_registry)
        self._generate_initial_tasks()

    def run(self, eternal_mode: bool = False, max_cycles: Optional[int] = None, max_in_cycle: Optional[int] = None) -> None:
        """Run the main Eurisko loop."""
        self.logger.info("Starting Eurisko")
        self.logger.info(f"Eternal mode: {eternal_mode}")

        cycle_count = 0
        while True:
            cycle_count += 1
            self.task_manager.cycle_stats.clear()  # Reset cycle stats
            self.task_manager.cycle_start_time = cur_time()
            self.logger.info(f"Starting cycle {cycle_count}")

            # Check cycle limit
            if max_cycles and cycle_count > max_cycles:
                self.logger.info(f"Reached maximum cycles ({max_cycles})")
                break

            # Process agenda until empty
            in_cycle_count = 0
            while self.task_manager.has_tasks():
                in_cycle_count += 1
                if max_in_cycle and in_cycle_count > max_in_cycle:
                    self.logger.info(f"Reached maximum count in cycle ({max_in_cycle})")
                    break
                task = self.task_manager.next_task()
                if task:
                    self.logger.info(
                        f"Working on task {task.unit_name}:{task.slot_name} "
                        f"(Priority: {task.priority})")
                    result = self.task_manager.work_on_task(task)
                    self.logger.info(f"Task completed with status: {result.get('status')}")
                
            # Print cycle stats
            self.logger.info(f"Cycle {cycle_count} stats:")
            self.logger.info(f"  Tasks executed: {self.task_manager.cycle_stats['tasks_executed']}")
            self.logger.info(f"  Units created: {self.task_manager.cycle_stats['units_created']}")
            self.logger.info(f"  Units modified: {self.task_manager.cycle_stats['units_modified']}")


            if not eternal_mode:
                self.logger.info("Agenda empty, ending run")
                break

            # In eternal mode, look for new tasks
            self.logger.info("Looking for new tasks...")
            self._generate_new_tasks()

            if not self.task_manager.has_tasks():
                self.logger.info("No new tasks found, ending run")
                break

    def _generate_initial_tasks(self):
        return generate_initial_tasks(self.task_manager, self.unit_registry)

    def _generate_new_tasks(self) -> None:
        return generate_ongoing_tasks(self.task_manager, self.unit_registry)

    def initialize_test_applications(self, registry):
        """Initialize some test applications for units."""
        add = registry.get_unit('add')
        if add:
            applications = [
                {'args': [1, 2], 'result': 3, 'worth': 800},
                {'args': [2, 3], 'result': 5, 'worth': 600},
                {'args': [3, 4], 'result': 7, 'worth': 400}
            ]
            add.set_prop('applics', applications)
            add.set_prop('applications', applications)

        multiply = registry.get_unit('multiply')
        if multiply:
            applications = [
                {'args': [2, 3], 'result': 6, 'worth': 900},
                {'args': [3, 4], 'result': 12, 'worth': 500},
                {'args': [4, 5], 'result': 20, 'worth': 300}
            ]
            multiply.set_prop('applics', applications)
            multiply.set_prop('applications', applications)
@dataclass
class CycleState:
    """State tracking for adaptive cycle management."""
    productive_tasks: int = 0
    new_units_worth: float = 0
    discovery_rate: float = 0
    stagnation_count: int = 0
    exploration_breadth: float = 0
    last_discoveries: List[str] = field(default_factory=list)

@dataclass
class StateSnapshot:
    """Represents a snapshot of the Eurisko system state."""
    unit_count: int
    unit_worths: Dict[str, int]
    relationship_count: int
    active_tasks: int
    total_worth: float
    unit_relationships: Dict[str, Set[str]]
    recent_modifications: Set[str]
    concept_clusters: Dict[str, Set[str]]

class EnhancedEurisko(Eurisko):
    def __init__(self, verbosity):
        super().__init__(verbosity)
        self.cycle_state = CycleState()
        self.exploration_strategies = self._initialize_exploration_strategies()
        
    def _initialize_exploration_strategies(self):
        """Initialize different exploration strategies."""
        return {
            'deepen': self._deepen_current_knowledge,
            'broaden': self._broaden_exploration,
            'synthesize': self._synthesize_knowledge,
            #'specialize': self._specialize_promising_units,
            #'generalize': self._generalize_patterns
        }
        
    def run(self, eternal_mode: bool = False, max_cycles: Optional[int] = None, max_in_cycle: Optional[int] = None) -> None:
        """Enhanced main Eurisko loop with adaptive exploration."""
        self.logger.info("Starting Enhanced Eurisko")
        
        cycle_count = 0
        while True:
            cycle_count += 1
            self.logger.info(f"Starting cycle {cycle_count}")
            
            if max_cycles and cycle_count > max_cycles:
                break
                
            # Adaptive cycle execution
            self._execute_cycle()
            
            # Analyze cycle results
            cycle_metrics = self._analyze_cycle_results()
            
            # Update exploration strategy
            next_strategy = self._determine_next_strategy(cycle_metrics)
            
            # Generate new tasks based on strategy
            self._generate_strategic_tasks(next_strategy)
            
            if not eternal_mode and not self.task_manager.has_tasks():
                break
                
            if self._should_end_run():
                self.logger.info("Ending run due to sustained lack of progress")
                break
                
    def _execute_cycle(self) -> None:
        """Execute a single cycle with enhanced monitoring."""
        cycle_tasks = []
        while self.task_manager.has_tasks():
            task = self.task_manager.next_task()
            if not task:
                break
                
            # Execute task with detailed result tracking
            result = self._execute_task_with_monitoring(task)
            cycle_tasks.append((task, result))
            
            # Immediate response to significant discoveries
            if self._is_significant_discovery(result):
                self._respond_to_discovery(result)
                
        self._update_cycle_state(cycle_tasks)

    def _update_cycle_state(self, cycle_tasks: List[Tuple[Task, Dict]]) -> None:
        """Update cycle state based on completed tasks and their results.

        Args:
            cycle_tasks: List of (task, result) tuples from the current cycle
        """
        if not cycle_tasks:
            self.cycle_state.stagnation_count += 1
            return

        # Reset metrics for new cycle
        self.cycle_state.productive_tasks = 0
        self.cycle_state.new_units_worth = 0.0
        total_impact = 0.0

        # Track unique areas explored this cycle
        explored_concepts = set()
        explored_slots = set()

        for task, result in cycle_tasks:
            # Track exploration breadth
            if task.unit_name:
                explored_concepts.add(task.unit_name)
            if task.slot_name:
                explored_slots.add(task.slot_name)

            # Analyze task productivity
            if result.get('status') == 'completed':
                impact = result.get('impact_analysis', {})

                # Check if task produced valuable changes
                if impact.get('significance', 0) > 0.3:  # Significant impact threshold
                    self.cycle_state.productive_tasks += 1
                    total_impact += impact.get('significance', 0)

                # Track new knowledge worth
                worth_delta = impact.get('worth_delta', 0)
                if worth_delta > 0:
                    self.cycle_state.new_units_worth += worth_delta

                # Track significant discoveries
                if impact.get('significance', 0) > 0.7:  # High significance threshold
                    for new_cluster in impact.get('cluster_changes', {}).get('new_clusters', []):
                        # Add representative unit from new cluster to discoveries
                        cluster_units = self.cycle_state.concept_clusters.get(new_cluster, set())
                        if cluster_units:
                            discovery = max(
                                cluster_units,
                                key=lambda x: self.unit_registry.get_unit(x).worth_value() 
                                if self.unit_registry.get_unit(x) else 0
                            )
                            if len(self.cycle_state.last_discoveries) >= 10:
                                self.cycle_state.last_discoveries.pop(0)
                            self.cycle_state.last_discoveries.append(discovery)

        # Update cycle metrics
        total_tasks = len(cycle_tasks)
        if total_tasks > 0:
            # Calculate discovery rate (average impact per task)
            self.cycle_state.discovery_rate = total_impact / total_tasks

            # Calculate exploration breadth (unique concepts and slots explored)
            breadth_score = (
                len(explored_concepts) / max(1, len(self.unit_registry.all_units())) +
                len(explored_slots) / max(1, len(self.slot_registry.all_slots()))
            ) / 2
            self.cycle_state.exploration_breadth = breadth_score

            # Update stagnation counter
            if self.cycle_state.productive_tasks > 0 and self.cycle_state.new_units_worth > 0:
                self.cycle_state.stagnation_count = 0
            else:
                self.cycle_state.stagnation_count += 1

            # Log cycle metrics
            self.logger.info(f"Cycle metrics:")
            self.logger.info(f"  Productive tasks: {self.cycle_state.productive_tasks}/{total_tasks}")
            self.logger.info(f"  Discovery rate: {self.cycle_state.discovery_rate:.3f}")
            self.logger.info(f"  Exploration breadth: {self.cycle_state.exploration_breadth:.3f}")
            self.logger.info(f"  New knowledge worth: {self.cycle_state.new_units_worth}")
            self.logger.info(f"  Stagnation count: {self.cycle_state.stagnation_count}")

    def _execute_task_with_monitoring(self, task) -> Dict:
        """Execute task with enhanced monitoring and analysis."""
        initial_state = self._capture_state_snapshot()
        
        result = self.task_manager.work_on_task(task)
        
        # Analyze changes and impact
        changes = self._analyze_changes(initial_state, self._capture_state_snapshot())
        result.update({'impact_analysis': changes})
        
        return result
        
    def _analyze_cycle_results(self) -> Dict:
        """Analyze results of the current cycle."""
        return {
            'productivity': self.cycle_state.productive_tasks / max(1, self.task_manager.cycle_stats['tasks_executed']),
            'discovery_rate': self.cycle_state.discovery_rate,
            'exploration_breadth': self.cycle_state.exploration_breadth,
            'new_knowledge_worth': self.cycle_state.new_units_worth
        }
        
    def _determine_next_strategy(self, metrics: Dict) -> str:
        """Determine next exploration strategy based on cycle metrics."""
        if metrics['discovery_rate'] < 0.1 and metrics['exploration_breadth'] > 0.7:
            return 'deepen'
        elif metrics['productivity'] < 0.3:
            return 'broaden'
        elif len(self.cycle_state.last_discoveries) > 3:
            return 'synthesize'
        elif metrics['new_knowledge_worth'] > 1000:
            return 'specialize'
        return 'generalize'
        
    def _generate_strategic_tasks(self, strategy: str) -> None:
        """Generate new tasks based on selected strategy."""
        if strategy in self.exploration_strategies:
            self.exploration_strategies[strategy]()
            
    def _deepen_current_knowledge(self) -> None:
        """Generate tasks to deepen understanding of current units."""
        for unit_name, unit in self.unit_registry.all_units().items():
            if unit.worth_value() > 600:
                for slot in ['specializations', 'generalizations', 'analogies']:
                    self.task_manager.add_task(Task(
                        priority=unit.worth_value(),
                        unit_name=unit_name,
                        slot_name=slot,
                        reasons=['Deepening knowledge exploration'],
                        task_type='analysis'
                    ))
                    
    def _broaden_exploration(self) -> None:
        """Generate tasks to explore new areas."""
        # Find units with few connections
        for unit_name, unit in self.unit_registry.all_units().items():
            if len(unit.get_prop('relations', [])) < 3:
                self.task_manager.add_task(Task(
                    priority=350,
                    unit_name=unit_name,
                    slot_name='find_relations',
                    reasons=['Broadening knowledge base'],
                    task_type='exploration'
                ))
                
    def _synthesize_knowledge(self) -> None:
        """Generate tasks to combine recent discoveries."""
        recent = self.cycle_state.last_discoveries[-3:]
        for i, unit1 in enumerate(recent):
            for unit2 in recent[i+1:]:
                self.task_manager.add_task(Task(
                    priority=600,
                    unit_name=unit1,
                    slot_name='synthesize',
                    reasons=['Knowledge synthesis'],
                    task_type='synthesis',
                    supplemental={'with_unit': unit2}
                ))
                
    def _should_end_run(self) -> bool:
        """Determine if the run should end based on progress metrics."""
        if self.cycle_state.stagnation_count > 5:
            return True
        return False
        
    def _is_significant_discovery(self, result: Dict) -> bool:
        """Evaluate if a task result represents a significant discovery."""
        if 'new_units' in result:
            for unit in result['new_units']:
                if unit.worth_value() > 800:
                    return True
        return False
        
    def _respond_to_discovery(self, result: Dict) -> None:
        """Immediately respond to significant discoveries."""
        for unit in result.get('new_units', []):
            if unit.worth_value() > 800:
                self.cycle_state.last_discoveries.append(unit.name)
                # Generate immediate follow-up tasks
                self._generate_discovery_followup_tasks(unit)
                
    def _generate_discovery_followup_tasks(self, unit) -> None:
        """Generate immediate follow-up tasks for significant discoveries."""
        high_priority_slots = ['applications', 'specializations', 'analogies']
        for slot in high_priority_slots:
            self.task_manager.add_task(Task(
                priority=900,
                unit_name=unit.name,
                slot_name=slot,
                reasons=['High-value discovery follow-up'],
                task_type='analysis'
            ))

    def _capture_state_snapshot(self) -> StateSnapshot:
        """Capture current state of the Eurisko system.

        Returns:
            StateSnapshot: A snapshot of key system metrics and relationships
        """
        # Capture unit-related information
        unit_count = len(self.unit_registry.all_units())
        unit_worths = {
            name: unit.worth_value() 
            for name, unit in self.unit_registry.all_units().items()
        }

        # Calculate total system worth
        total_worth = sum(unit_worths.values())

        # Capture relationships between units
        unit_relationships = {}
        relationship_count = 0
        for unit_name, unit in self.unit_registry.all_units().items():
            relations = set()
            # Get all units this unit relates to
            for rel_type in ['specializations', 'generalizations', 'analogies', 'applications']:
                related = unit.get_prop(rel_type, [])
                if isinstance(related, list):
                    for rel in related:
                        if isinstance(rel, dict) and 'target' in rel:
                            relations.add(rel['target'])
                        elif isinstance(rel, str):
                            relations.add(rel)
            unit_relationships[unit_name] = relations
            relationship_count += len(relations)

        # Track recently modified units
        recent_modifications = set(
            name for name, unit in self.unit_registry.all_units().items()
            if unit.get_prop('last_modified', 0) > self.task_manager.cycle_start_time
        )

        # Identify concept clusters (units with similar properties or relationships)
        concept_clusters = {}
        for unit_name, unit in self.unit_registry.all_units().items():
            # Get unit's key properties for clustering
            props = set(unit.get_prop('slots', {}).keys())
            worth = unit.worth_value()

            # Find or create appropriate cluster
            cluster_key = None
            for key, cluster in concept_clusters.items():
                sample_unit = self.unit_registry.get_unit(next(iter(cluster)))
                if sample_unit:
                    sample_props = set(sample_unit.get_prop('slots', {}).keys())
                    if len(props | sample_props) > 0 and len(props & sample_props) / len(props | sample_props) > 0.7:  # 70% similarity
                        cluster_key = key
                        break

            if cluster_key is None:
                cluster_key = f"cluster_{len(concept_clusters)}"
                concept_clusters[cluster_key] = set()

            concept_clusters[cluster_key].add(unit_name)

        return StateSnapshot(
            unit_count=unit_count,
            unit_worths=unit_worths,
            relationship_count=relationship_count,
            active_tasks=self.task_manager.task_count(),
            total_worth=total_worth,
            unit_relationships=unit_relationships,
            recent_modifications=recent_modifications,
            concept_clusters=concept_clusters
        )

    def _analyze_changes(self, before: StateSnapshot, after: StateSnapshot) -> Dict:
        """Analyze changes between two system states.

        Args:
            before: StateSnapshot before task execution
            after: StateSnapshot after task execution

        Returns:
            Dict containing analysis of changes
        """
        changes = {
            'new_units': after.unit_count - before.unit_count,
            'worth_delta': after.total_worth - before.total_worth,
            'new_relationships': after.relationship_count - before.relationship_count,
            'modified_units': len(after.recent_modifications - before.recent_modifications),
        }

        # Analyze cluster changes
        cluster_changes = {
            'new_clusters': set(after.concept_clusters.keys()) - set(before.concept_clusters.keys()),
            'modified_clusters': set()
        }

        for cluster_key in set(before.concept_clusters.keys()) & set(after.concept_clusters.keys()):
            if before.concept_clusters[cluster_key] != after.concept_clusters[cluster_key]:
                cluster_changes['modified_clusters'].add(cluster_key)

        changes['cluster_changes'] = cluster_changes

        # Calculate change significance score (0-1)
        significance = (
            0.4 * (changes['worth_delta'] / max(1000, before.total_worth)) +
            0.3 * (changes['new_relationships'] / max(10, before.relationship_count)) +
            0.2 * (len(cluster_changes['new_clusters']) / max(1, len(before.concept_clusters))) +
            0.1 * (changes['modified_units'] / max(1, before.unit_count))
        )
        changes['significance'] = min(1.0, max(0.0, significance))

        return changes

def main():
    """Command line entry point."""
    parser = argparse.ArgumentParser(description='PyEurisko - A Python implementation of Eurisko')
    parser.add_argument('-v', '--verbosity', type=int, default=1,
                        help='Verbosity level (0-3)')
    parser.add_argument('-e', '--eternal', action='store_true',
                        help='Run in eternal mode')
    parser.add_argument('-p', '--enhanced', action='store_true',
                        help='Run in enhanced mode')
    parser.add_argument('-c', '--max-cycles', type=int,
                        help='Maximum number of cycles to run in eternal mode')
    parser.add_argument('-n', '--max-in-cycle', type=int,
                        help='Maximum number of tasks processed in one cycle')
    parser.add_argument('-t', '--timeout', type=int,
                        help='Global run timeout')
    args = parser.parse_args()

    eurisko = Eurisko(verbosity=args.verbosity) if not args.enhanced else EnhancedEurisko(verbosity=args.verbosity)
    eurisko.initialize()
    def eurisko_run():
        eurisko.run(eternal_mode=args.eternal, max_cycles=args.max_cycles, max_in_cycle=args.max_in_cycle)
    if args.timeout:
        try:
            func_timeout(args.timeout, eurisko_run)
        except FunctionTimedOut:
            eurisko.logger.debug("Function timed out")
    else:
        eurisko_run()
    eurisko.task_manager.print_stats()

if __name__ == '__main__':
    main()
