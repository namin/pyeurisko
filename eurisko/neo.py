from dataclasses import dataclass, field
from typing import Dict, List, Any, Callable, Optional
from textwrap import dedent
import inspect
import logging
from enum import Enum
from .llm import generate

class SlotType(Enum):
    CODE = "code"  # Executable Python code
    TEXT = "text"  # Natural language description
    LIST = "list"  # List of values
    UNIT = "unit"  # Reference to another unit

@dataclass
class Slot:
    name: str
    type: SlotType
    value: Any
    meta: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Unit:
    name: str
    slots: Dict[str, Slot] = field(default_factory=dict)
    worth: int = 500

    def add_slot(self, name: str, value: Any, slot_type: SlotType, meta: Dict = None):
        self.slots[name] = Slot(name, slot_type, value, meta or {})

    def get_slot(self, name: str) -> Optional[Slot]:
        return self.slots.get(name)

class EuriskoLLM:
    """LLM interface for introspection and code generation"""
    
    def __init__(self):
        pass
        
    def analyze_code(self, code: str) -> Dict[str, Any]:
        """Analyze Python code to extract key features and relationships"""
        prompt = dedent(f"""
        Analyze this Python code to extract key features and relationships:
        ```python
        {code}
        ```
        Return a JSON object with:
        1. Core concepts/objects manipulated
        2. Key operations performed
        3. Dependencies and relationships
        4. Potential areas for specialization
        5. Suggested criteria for success/failure
        """)
        
        response_text = generate(
            max_tokens=1000,
            temperature=0.2,
            prompt=prompt
        )
        return response_text

    def suggest_modifications(self, unit: Unit, context: str) -> List[Dict]:
        """Suggest modifications to a unit based on its performance"""
        # Get code and documentation
        code = unit.get_slot("code")
        docs = unit.get_slot("documentation")
        performance = unit.get_slot("performance")
        
        prompt = dedent(f"""
        Given this unit:
        Name: {unit.name}
        Documentation: {docs.value if docs else 'None'}
        Code: 
        ```python
        {code.value if code else 'None'}
        ```
        Performance: {performance.value if performance else 'No data'}
        Context: {context}

        Suggest 2-3 specific modifications that could improve its performance.
        Format each as a JSON object with:
        1. What to modify
        2. How to modify it
        3. Expected benefit
        4. Potential risks
        """)
        
        content = generate(
            max_tokens=1000,
            temperature=0.5,
            prompt=prompt
        )
        return content

class NeoEurisko:
    def __init__(self):
        self.units: Dict[str, Unit] = {}
        self.llm = EuriskoLLM()
        self.agenda: List[Dict] = []
        
    def create_heuristic_from_function(self, func: Callable) -> Unit:
        """Create a heuristic unit from a Python function"""
        # Extract code and docs
        source = inspect.getsource(func)
        docs = inspect.getdoc(func) or ""
        
        # Create unit
        unit = Unit(func.__name__)
        unit.add_slot("code", source, SlotType.CODE)
        unit.add_slot("documentation", docs, SlotType.TEXT)
        unit.add_slot("is_a", ["Heuristic"], SlotType.LIST)
        
        # Use LLM to analyze code
        analysis = self.llm.analyze_code(source)
        
        # Add extracted features as slots
        unit.add_slot("features", analysis["core_concepts"], SlotType.LIST)
        unit.add_slot("operations", analysis["key_operations"], SlotType.LIST)
        unit.add_slot("dependencies", analysis["dependencies"], SlotType.LIST)
        unit.add_slot("specialization_opportunities", 
                     analysis["potential_areas"], SlotType.LIST)
        unit.add_slot("success_criteria", 
                     analysis["success_criteria"], SlotType.LIST)
        
        # Initialize performance tracking
        unit.add_slot("performance", {
            "applications": 0,
            "successes": 0,
            "failures": 0,
            "worth_generated": 0
        }, SlotType.LIST)
        
        self.units[unit.name] = unit
        return unit

    def evolve_heuristic(self, unit: Unit) -> Optional[Unit]:
        """Evolve a heuristic based on its performance"""
        if "Heuristic" not in unit.get_slot("is_a").value:
            return None
            
        # Get performance context
        perf = unit.get_slot("performance").value
        context = f"Applied {perf['applications']} times, {perf['successes']} successes"
        
        # Get modification suggestions
        suggestions = self.llm.suggest_modifications(unit, context)
        
        # Create new version with modifications
        new_name = f"{unit.name}-evolved-{len(self.units)}"
        new_unit = Unit(new_name)
        
        # Copy basic slots
        for slot_name in ["documentation", "is_a", "features", "operations"]:
            if slot := unit.get_slot(slot_name):
                new_unit.add_slot(slot_name, slot.value, slot.type, slot.meta)
        
        # Modify code based on suggestions
        orig_code = unit.get_slot("code").value
        modified_code = self._apply_modifications(orig_code, suggestions)
        new_unit.add_slot("code", modified_code, SlotType.CODE)
        
        # Add evolution record
        new_unit.add_slot("evolved_from", unit.name, SlotType.UNIT)
        new_unit.add_slot("evolution_context", {
            "parent_performance": perf,
            "modifications": suggestions
        }, SlotType.LIST)
        
        self.units[new_name] = new_unit
        return new_unit

    def apply_heuristic(self, heuristic: Unit, target: Unit) -> Dict[str, Any]:
        """Apply a heuristic to a target unit"""
        try:
            # Get code and compile
            code = heuristic.get_slot("code").value
            func = compile(code, heuristic.name, 'exec')
            
            # Create namespace and run
            namespace = {"target": target, "eurisko": self}
            exec(func, namespace)
            
            # Update performance
            perf = heuristic.get_slot("performance").value
            perf["applications"] += 1
            
            # Check success criteria
            criteria = heuristic.get_slot("success_criteria").value
            success = self._evaluate_criteria(criteria, namespace.get("result", {}))
            
            if success:
                perf["successes"] += 1
                worth_generated = namespace.get("result", {}).get("worth_generated", 0)
                perf["worth_generated"] += worth_generated
            else:
                perf["failures"] += 1
                
            # Consider evolution if needed
            if perf["applications"] > 10 and perf["failures"] / perf["applications"] > 0.7:
                task = {
                    "type": "evolve",
                    "unit": heuristic.name,
                    "priority": heuristic.worth,
                    "reason": "High failure rate"
                }
                self.agenda.append(task)
                
            return namespace.get("result", {})
            
        except Exception as e:
            logging.error(f"Error applying {heuristic.name}: {e}")
            return {"success": False, "error": str(e)}

    def _apply_modifications(self, code: str, suggestions: List[Dict]) -> str:
        """Use LLM to apply suggested modifications to code"""
        prompt = dedent(f"""
        Modify this code according to the suggestions:
        Original code:
        ```python
        {code}
        ```
        
        Suggestions:
        {suggestions}
        
        Return the modified code that implements these changes.
        Preserve the core functionality while making the suggested improvements.
        """)
        
        content = generate(
            max_tokens=2000,
            temperature=0.2,
            prompt=prompt
        )
        return content

    def _evaluate_criteria(self, criteria: List[str], result: Dict) -> bool:
        """Use LLM to evaluate if result meets success criteria"""
        prompt = dedent(f"""
        Evaluate if the result meets the success criteria:
        
        Criteria:
        {criteria}
        
        Result:
        {result}
        
        Return True if the criteria are met, False otherwise.
        Explain your reasoning.
        """)
        
        content = generate(
            max_tokens=500,
            temperature=0.2,
            prompt=prompt
        )
        return "true" in content.lower()

# Example usage:
def example_heuristic(target: Unit, eurisko: NeoEurisko) -> Dict:
    """Find opportunities to specialize a unit based on its features.
    
    If a unit has some successful applications but many failures,
    look for ways to specialize it into more focused versions.
    """
    result = {"success": False, "worth_generated": 0}
    
    # Check applicability
    if not (features := target.get_slot("features")):
        return result
        
    if not (perf := target.get_slot("performance")):
        return result
        
    # Look for specialization opportunities
    if perf.value["applications"] > 5:
        success_rate = perf.value["successes"] / perf.value["applications"]
        
        if 0.1 < success_rate < 0.3:  # Some successes but mostly failures
            # Create specialized versions
            for feature in features.value:
                new_name = f"{target.name}-by-{feature}"
                specialized = Unit(new_name)
                specialized.worth = min(1000, target.worth + 100)
                specialized.add_slot("specializes", target.name, SlotType.UNIT)
                specialized.add_slot("specialized_on", feature, SlotType.TEXT)
                eurisko.units[new_name] = specialized
                result["worth_generated"] += 100
                
            result["success"] = True
            
    return result
