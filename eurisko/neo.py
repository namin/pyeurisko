from dataclasses import dataclass, field
from typing import Dict, List, Any, Callable, Optional
from textwrap import dedent
import inspect
import logging
from enum import Enum
import json
from .llm import generate

logger = logging.getLogger(__name__)

class SlotType(Enum):
    CODE = "code"  
    TEXT = "text"  
    LIST = "list"  
    UNIT = "unit"  

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
    def __init__(self):
        self.default_analysis = {
            "core_concepts": [],
            "key_operations": [],
            "dependencies": [],
            "potential_areas": [],
            "success_criteria": []
        }
        
    def analyze_code(self, code: str) -> Dict[str, Any]:
        prompt = dedent(f'''
        Analyze this Python code and return a JSON object.
        Use this exact format and nothing else:
        {{
          "core_concepts": ["concept1", "concept2"],
          "key_operations": ["op1", "op2"],
          "dependencies": ["dep1", "dep2"],
          "potential_areas": ["area1", "area2"],
          "success_criteria": ["criterion1", "criterion2"]
        }}

        Code to analyze:
        ```python
        {code}
        ```
        ''')
        
        try:
            logger.info("Requesting code analysis")
            response = generate(
                max_tokens=1000,
                temperature=0.2,
                prompt=prompt
            )
            logger.debug(f"Raw response: {response[:200]}")
            
            try:
                # Extract JSON if it's embedded in text
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = response[json_start:json_end]
                    analysis = json.loads(json_str)
                else:
                    logger.warning("No JSON found in response")
                    return self.default_analysis
                    
                # Validate keys
                for key in self.default_analysis:
                    if key not in analysis:
                        analysis[key] = self.default_analysis[key]
                return analysis
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON parse error: {str(e)}")
                return self.default_analysis
                
        except Exception as e:
            logger.error(f"LLM error: {str(e)}")
            return self.default_analysis

class NeoEurisko:
    def __init__(self):
        self.units: Dict[str, Unit] = {}
        self.llm = EuriskoLLM()
        self.agenda: List[Dict] = []
        
    def create_heuristic_from_function(self, func: Callable) -> Unit:
        logger.info(f"Creating heuristic from {func.__name__}")
        
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
        logger.debug(f"Code analysis results: {analysis}")
        
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

    def apply_heuristic(self, heuristic: Unit, target: Unit) -> Dict[str, Any]:
        """Apply a heuristic to a target unit"""
        try:
            # Get code and compile
            logger.info(f"Applying {heuristic.name} to {target.name}")
            code = heuristic.get_slot("code").value
            
            # Create complete namespace with all required types
            namespace = {
                "Unit": Unit,
                "SlotType": SlotType,
                "NeoEurisko": type(self),  # Add the class itself
                "target": target,
                "eurisko": self,
                # Add any other required types from the module
                "Optional": Optional,
                "Dict": Dict,
                "List": List,
                "Any": Any
            }
            
            # First compile the code
            compiled = compile(code, heuristic.name, 'exec')
            # Execute it in our namespace
            exec(compiled, namespace)
            
            # Get the function by name
            func = namespace.get(heuristic.name)
            if not func:
                logger.error(f"Could not find function {heuristic.name} in compiled code")
                return {"success": False, "error": "Function not found"}
                
            logger.debug(f"Executing {heuristic.name} with target={target.name}")
            # Run the function
            result = func(target, self)
            logger.debug(f"Function result: {result}")
            
            # Update performance
            perf = heuristic.get_slot("performance").value
            perf["applications"] += 1
            
            # Check success
            if result.get("success", False):
                logger.info(f"Heuristic {heuristic.name} succeeded")
                perf["successes"] += 1
                worth_generated = result.get("worth_generated", 0)
                perf["worth_generated"] += worth_generated
            else:
                logger.info(f"Heuristic {heuristic.name} failed")
                perf["failures"] += 1
                
            return result
            
        except Exception as e:
            logger.error(f"Error applying {heuristic.name}: {e}", exc_info=True)
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
