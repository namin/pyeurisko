"""Heuristics for discovering and refining chess patterns."""
from typing import List, Dict, Any
from ..neo import Unit, SlotType
from .motifs import ChessMotif
import logging

logger = logging.getLogger(__name__)

def pattern_specialization(target: Unit, eurisko: 'ChessDiscoverySystem') -> Dict:
    """Specialize a pattern based on success/failure statistics."""
    result = {"success": False, "worth_generated": 0}
    
    # Skip if not a ChessMotif
    is_a = target.get_slot("is_a")
    if not is_a or "ChessMotif" not in is_a.value:
        return result
    
    # Check if we have performance data
    perf = target.get_slot("performance")
    if not perf:
        return result
        
    perf_data = perf.value
    if not perf_data or perf_data["applications"] < 20:
        return result
        
    success_rate = perf_data["successes"] / perf_data["applications"]
    
    if 0.1 < success_rate < 0.4:  # Pattern needs refinement
        try:
            # Look for common features in successful cases
            examples = target.get_slot("examples")
            if not examples:
                return result
                
            success_examples = [ex for ex in examples.value if ex.get("success", False)]
            
            # Create specialized pattern
            pattern_type = target.get_slot("pattern_type")
            if not pattern_type:
                return result
                
            specialized = ChessMotif(f"{pattern_type.value}-specialized")
            specialized.add_slot("specializes", target.name, SlotType.UNIT)
            specialized.add_slot("pattern_type", pattern_type.value, SlotType.TEXT)
            
            # Copy detection function
            detector = target.get_slot("detection_function")
            if detector:
                specialized.add_slot("detection_function", detector.value, SlotType.CODE)
            
            eurisko.motifs[specialized.name] = specialized
            result["worth_generated"] += 100
            result["success"] = True
            
        except Exception as e:
            logger.error(f"Error in pattern specialization: {e}")
            
    return result

def pattern_combination(target: Unit, eurisko: 'ChessDiscoverySystem') -> Dict:
    """Look for combinations of patterns that occur together."""
    result = {"success": False, "worth_generated": 0}
    
    # Check if this is a pattern analysis target
    is_a = target.get_slot("is_a")
    if not is_a or "PatternAnalysis" not in is_a.value:
        return result
        
    try:
        before_patterns = target.get_slot("before_patterns")
        after_patterns = target.get_slot("after_patterns")
        
        if not before_patterns or not after_patterns:
            return result
            
        before = before_patterns.value
        after = after_patterns.value
        
        # Look for patterns that occur together
        if len(before) >= 2:
            pattern_types = [p["type"] for p in before]
            name = f"combined-{'_'.join(pattern_types)}"
            
            # Create new combined pattern if it doesn't exist
            if name not in eurisko.motifs:
                combined = ChessMotif(name)
                combined.add_slot("pattern_type", "combination", SlotType.TEXT)
                combined.add_slot("components", pattern_types, SlotType.LIST)
                
                # Combined detection function
                def detect_combined(board):
                    instances = []
                    found_all = True
                    for pattern_type in pattern_types:
                        if pattern_type in eurisko.motifs:
                            result = eurisko.motifs[pattern_type].detect(board)
                            if not result["instances"]:
                                found_all = False
                                break
                    if found_all:
                        instances.append({
                            "patterns": pattern_types
                        })
                    return {"type": "combination", "instances": instances}
                
                combined.add_slot("detection_function", detect_combined, SlotType.CODE)
                eurisko.motifs[combined.name] = combined
                result["worth_generated"] += 200
                result["success"] = True
                
    except Exception as e:
        logger.error(f"Error in pattern combination: {e}")
        
    return result

def create_basic_heuristics(eurisko: 'ChessDiscoverySystem') -> List[Unit]:
    """Create the basic set of heuristics for the system."""
    heuristics = []
    
    # Pattern specialization heuristic
    spec = eurisko.create_heuristic_from_function(pattern_specialization)
    spec.add_slot("is_a", ["PatternDiscovery"], SlotType.LIST)
    heuristics.append(spec)
    
    # Pattern combination heuristic
    comb = eurisko.create_heuristic_from_function(pattern_combination)
    comb.add_slot("is_a", ["PatternDiscovery"], SlotType.LIST)
    heuristics.append(comb)
    
    return heuristics
