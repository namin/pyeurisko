"""Core heuristic implementation for PyEurisko."""
from typing import Any, Dict, List, Optional
import random
import time
from .unit import Unit, UnitRegistry
from .heuristic import Heuristic

class HeuristicsManager:
    """Manages application of heuristics."""
    
    debug = True # Turn on debug logging

    def __init__(self, registry: UnitRegistry):
        """Initialize with registry."""
        self.unit_registry = registry
        self._setup_heuristics()

    def _setup_heuristics(self) -> None:
        """Set up all heuristics."""
        for i in range(1, 16):
            name = f'h{i}'
            h = Heuristic(name, self.unit_registry)
            setup_method = getattr(self, f'_setup_{name}', None)
            if setup_method:
                setup_method(h)
            self.unit_registry.add_unit(h)

    def _setup_h1(self, h1: Heuristic) -> None:
        """Configure H1: Look for specialization opportunities."""
        def check_relevance(context: Dict[str, Any]) -> bool:
            """Check if there are any valuable applications that suggest need for specialization."""
            unit = context.get('unit')
            if not unit:
                return False
                
            # Get applications and validate
            applications = unit.get_prop('applications')
            if isinstance(applications, dict):
                applications = [applications]
            if not isinstance(applications, list):
                applications = []

            if HeuristicsManager.debug:
                print(f"\nChecking H1 relevance for {unit.name}", flush=True)
                print(f"Applications: {applications}", flush=True)

            if applications:
                high_worth = [app for app in applications if app.get('worth', 0) > 700]
                total = len(applications)
                success_ratio = len(high_worth) / total

                if HeuristicsManager.debug:
                    print(f"\nAnalyzing {unit.name} applications:")
                    for app in applications:
                        print(f"- Worth {app.get('worth')}: {app}", flush=True)
                    print(f"Found {len(high_worth)}/{total} high-worth apps (ratio {success_ratio:.2f})")
                    print(f"Result: {'PASS' if len(high_worth) > 0 and success_ratio < 0.2 else 'FAIL'}")
                    
                # Want some successes but a low success rate (<20%)
                return len(high_worth) > 0 and success_ratio < 0.2

            if HeuristicsManager.debug:
                print(f"No applications found for {unit.name}")
            return False

        def compute_action(context: Dict[str, Any]) -> bool:
            """Create specialization task for unit with some valuable but many poor applications."""
            unit = context.get('unit')
            if not unit:
                return False

            # Get applications and check ratio
            applications = unit.get_prop('applications')
            if isinstance(applications, dict):
                applications = [applications]
            if not isinstance(applications, list):
                return False

            high_worth = [app for app in applications if app.get('worth', 0) > 700]
            total = len(applications)
            
            if len(high_worth) > 0 and len(high_worth)/total < 0.2:
                if HeuristicsManager.debug:
                    print(f"Creating specialization task for {unit.name}", flush=True)
                    
                # Create specialization task
                task = {
                    'task_type': 'specialization',
                    'unit': unit,
                    'reason': f'Unit has {len(high_worth)}/{total} high-worth applications'
                }
                context['task_results'] = context.get('task_results', {})
                context['task_results']['new_tasks'] = [task]
                return True

            return False
            
        h1.set_prop('if_potentially_relevant', check_relevance)
        h1.set_prop('then_compute', compute_action)

    def _setup_h2(self, h2: Heuristic) -> None:
        """Configure H2: Remove wasteful concepts."""
        pass

    def _setup_h3(self, h3: Heuristic) -> None:
        """Configure H3: Choose slot to specialize."""
        pass

    def _setup_h4(self, h4: Heuristic) -> None:
        """Configure H4: Gather empirical data about new unit."""
        pass

    def _setup_h5(self, h5: Heuristic) -> None:
        """Configure H5: Choose multiple slots to specialize."""
        def check_task(context: Dict[str, Any]) -> bool:
            """Check if we need to choose slots to specialize."""
            unit = context.get('unit')
            task = context.get('task')
            if not unit or not task:
                return False
                
            return (task.get('task_type') == 'specialization' and
                    not task.get('slots_to_change'))

        def compute_action(context: Dict[str, Any]) -> bool:
            """Randomly select slots for specialization."""
            unit = context.get('unit')
            if not unit:
                return False

            # Get available slots
            all_slots = unit.get_prop('slots') or []
            if not all_slots:
                return False

            # Select a subset of slots randomly
            num_slots = min(random.randint(1, 3), len(all_slots))
            selected_slots = random.sample(all_slots, num_slots)
            
            # Set the selected slots in the context
            task = context.get('task')
            if task:
                task['slots_to_change'] = selected_slots
                return True
                
            return False

        h5.set_prop('if_working_on_task', check_task)
        h5.set_prop('then_compute', compute_action)

    def get_applicable_heuristics(self, context: Dict[str, Any]) -> List[Heuristic]:
        """Find all heuristics that could apply to a context."""
        heuristics = []
        for unit_name in self.unit_registry.get_units_by_category('heuristic'):
            unit = self.unit_registry.get_unit(unit_name)
            if isinstance(unit, Heuristic) and unit.is_potentially_relevant(context):
                heuristics.append(unit)
        return heuristics

    def apply_heuristics(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply all relevant heuristics to a context."""
        results = []
        for heuristic in self.get_applicable_heuristics(context):
            start_time = time.time()
            success = heuristic.apply(context)
            elapsed = time.time() - start_time
            
            results.append({
                'heuristic': heuristic.name,
                'success': success,
                'elapsed': elapsed
            })
            
        return results