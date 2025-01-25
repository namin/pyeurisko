"""Implementation of the H1 heuristic from the original Eurisko."""

from typing import Dict, Any, List
from .heuristic import Heuristic
from .unit import Unit

class H1(Heuristic):
    """H1: If an op has some good applications but >80% are bad, try specializing it."""
    
    def __init__(self):
        super().__init__('h1')
        self.worth = 724
        self.isa = ['heuristic', 'op', 'anything']
        self.english = ("IF an op F (e.g., a mathematical function, a heuristic, etc.) "
                       "has had some good applications, but over 4/5 are bad, "
                       "THEN conjecture that some Specializations of F may be superior to F, "
                       "and add tasks to specialize F to the Agenda.")
        self.abbrev = "Specialize a sometimes-useful action"

    def is_potentially_relevant(self, context: Dict[str, Any]) -> bool:
        """Check if F has any recorded applications."""
        unit = context.get('unit')
        if not unit:
            return False
        
        # Check for applications
        applications = unit.get_prop('applications')
        return bool(applications)

    def is_truly_relevant(self, context: Dict[str, Any]) -> bool:
        """Check if some applications have high worth but most have low worth."""
        unit = context.get('unit')
        if not unit:
            return False
            
        applications = unit.get_prop('applications') or []
        if not applications:
            return False

        # Check for at least one high-worth application
        has_good = False
        total = 0
        good_count = 0
        
        for app in applications:
            results = app.get('results', [])
            total += len(results)
            for result in results:
                worth = getattr(result, 'worth', 0)
                if worth > 700:  # High worth threshold
                    has_good = True
                    good_count += 1
                    
        if not has_good or total == 0:
            return False
            
        # Less than 20% good applications
        fraction_good = good_count / total
        return fraction_good < 0.2 and not unit.get_prop('subsumed_by')

    def then_conjecture(self, context: Dict[str, Any]) -> bool:
        """Create a conjecture about specializing the unit."""
        system = context.get('system')
        unit = context.get('unit')
        if not system or not unit:
            return False
            
        # Create new conjecture unit
        conjec_name = system.new_name('conjec')
        conjec = system.create_unit(conjec_name, 'proto-conjec')
        
        # Set conjecture properties
        fraction = getattr(self, '_fraction', 0)
        english = (f"Specializations of {unit.name} may be more useful than it is, "
                  f"since it has some good instances but many more poor ones. "
                  f"({(1.0 - fraction)*100:.1f}% are losers)")
        
        conjec.set_prop('english', english)
        conjec.set_prop('abbrev', 
                       f"{unit.name} sometimes wins, usually loses, so specializations may win big")
        
        # Calculate worth based on fraction and average worths
        worth = int((1.0 - abs(fraction - 0.1)) * 
                   self.average_worths([unit.worth, self.worth]))
        conjec.set_prop('worth', worth)
        
        # Add to conjectures list
        conjectures = system.get_prop('conjectures') or []
        conjectures.append(conjec)
        system.set_prop('conjectures', conjectures)
        
        return True

    def then_add_to_agenda(self, context: Dict[str, Any]) -> bool:
        """Add task to specialize the unit to the agenda."""
        system = context.get('system')
        unit = context.get('unit')
        if not system or not unit:
            return False
            
        # Calculate priority based on worths
        priority = self.average_worths([unit.worth, self.worth])
        
        # Add specialization task
        task = {
            'priority': priority,
            'unit': unit,
            'slot': 'specializations',
            'reasons': [context.get('conjecture')],
            'credit_to': ['h1']
        }
        
        system.add_to_agenda(task)
        system.add_prop('new_tasks', "1 unit must be specialized")
        return True

    @staticmethod
    def average_worths(worths: List[float]) -> float:
        """Calculate average of worth values."""
        if not worths:
            return 0
        return sum(worths) / len(worths)