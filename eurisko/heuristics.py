"""Core heuristic implementation for PyEurisko."""
[Previous content remains unchanged up to _setup_h4]

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
            import random
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