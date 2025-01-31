"""Chess tactical motifs learned from analysis."""
import chess
import logging
from typing import Dict, List, Any, Optional, Tuple, Callable
from ..neo import Unit, SlotType
from .pattern_learner import (
    PieceRelation, GeometricPattern, analyze_position_change,
    get_piece_relations, find_geometric_patterns
)

logger = logging.getLogger(__name__)

class ChessMotif(Unit):
    """A learned chess tactical pattern."""
    def __init__(self, name: str):
        super().__init__(name)
        self.add_slot("pattern_type", "", SlotType.TEXT)
        self.add_slot("detection_conditions", [], SlotType.LIST)  # List of conditions that define this pattern
        self.add_slot("examples", [], SlotType.LIST)  # FEN positions showing this motif
        self.add_slot("success_rate", 0.0, SlotType.UNIT)  # How often this leads to material gain
        self.add_slot("average_gain", 0.0, SlotType.UNIT)  # Average material gain when successful
        self.add_slot("is_a", ["ChessMotif"], SlotType.LIST)
        self.add_slot("performance", {
            "applications": 0,
            "successes": 0,
            "failures": 0,
            "worth_generated": 0,
            "total_material_gain": 0
        }, SlotType.LIST)
        
    def detect(self, board: chess.Board) -> Dict[str, Any]:
        """Check if this motif is present in the position."""
        try:
            # Get current position properties
            relations = get_piece_relations(board)
            patterns = find_geometric_patterns(relations)
            
            # Check each condition
            matches = []
            conditions = self.get_slot("detection_conditions").value
            
            for condition in conditions:
                condition_type = condition["type"]
                
                if condition_type == "piece_relation":
                    # Look for specific piece relationships
                    for rel in relations:
                        if matches_relation_condition(rel, condition):
                            matches.append({
                                "relation": rel,
                                "condition": condition
                            })
                            
                elif condition_type == "geometric":
                    # Look for specific geometric patterns
                    for pattern in patterns:
                        if matches_geometric_condition(pattern, condition):
                            matches.append({
                                "pattern": pattern,
                                "condition": condition
                            })
            
            return {
                "type": self.get_slot("pattern_type").value,
                "instances": matches
            }
            
        except Exception as e:
            logger.error(f"Error detecting motif {self.name}: {e}")
            return {"type": self.get_slot("pattern_type").value, "instances": []}

def matches_relation_condition(relation: PieceRelation, condition: Dict) -> bool:
    """Check if a piece relation matches a condition."""
    if condition.get("relation_type") and condition["relation_type"] != relation.relation_type:
        return False
        
    if condition.get("from_piece_type") and \
       condition["from_piece_type"] != relation.from_piece.piece_type:
        return False
        
    if condition.get("to_piece_type") and \
       condition["to_piece_type"] != relation.to_piece.piece_type:
        return False
        
    return True

def matches_geometric_condition(pattern: GeometricPattern, condition: Dict) -> bool:
    """Check if a geometric pattern matches a condition."""
    if condition.get("pattern_type") and condition["pattern_type"] != pattern.pattern_type:
        return False
        
    if condition.get("min_pieces") and len(pattern.pieces) < condition["min_pieces"]:
        return False
        
    if condition.get("piece_types"):
        required_types = set(condition["piece_types"])
        actual_types = {p.piece_type for p in pattern.pieces}
        if not required_types.issubset(actual_types):
            return False
            
    return True

def find_common_conditions(examples: List[Dict]) -> List[Dict]:
    """Find common patterns across multiple examples."""
    if not examples:
        return []
        
    common_relations = []
    common_patterns = []
    
    # Collect all relations and patterns
    all_relations = []
    all_patterns = []
    
    for example in examples:
        relations = example.get("new_relations", [])
        patterns = example.get("new_patterns", [])
        all_relations.extend(relations)
        all_patterns.extend(patterns)
    
    # Find common relation types
    relation_counts = {}
    for rel in all_relations:
        key = (rel.relation_type, rel.from_piece.piece_type, rel.to_piece.piece_type)
        relation_counts[key] = relation_counts.get(key, 0) + 1
    
    # Keep relations that appear in at least 50% of examples
    min_occurrences = len(examples) * 0.5
    for (rel_type, from_type, to_type), count in relation_counts.items():
        if count >= min_occurrences:
            common_relations.append({
                "type": "piece_relation",
                "relation_type": rel_type,
                "from_piece_type": from_type,
                "to_piece_type": to_type
            })
            
    # Find common geometric patterns
    pattern_counts = {}
    for pattern in all_patterns:
        key = (pattern.pattern_type, len(pattern.pieces))
        pattern_counts[key] = pattern_counts.get(key, 0) + 1
    
    for (pattern_type, piece_count), count in pattern_counts.items():
        if count >= min_occurrences:
            common_patterns.append({
                "type": "geometric",
                "pattern_type": pattern_type,
                "min_pieces": piece_count
            })
            
    return common_relations + common_patterns

def create_motif_from_analysis(name: str, examples: List[Dict]) -> Optional[ChessMotif]:
    """Create a new motif by analyzing common patterns in examples."""
    if not examples:
        return None
        
    try:
        # Create the motif
        motif = ChessMotif(name)
        
        # Analyze the examples to find common patterns
        common_conditions = find_common_conditions(examples)
        if not common_conditions:
            return None
            
        # Set up the motif
        motif.add_slot("pattern_type", name, SlotType.TEXT)
        motif.add_slot("detection_conditions", common_conditions, SlotType.LIST)
        motif.add_slot("examples", examples, SlotType.LIST)
        
        # Calculate initial statistics
        material_gains = [ex.get("material_gain", 0) for ex in examples]
        successful = [gain > 0 for gain in material_gains]
        
        if any(successful):
            success_rate = sum(successful) / len(examples)
            avg_gain = sum(gain for gain in material_gains if gain > 0) / sum(successful)
            
            motif.add_slot("success_rate", success_rate, SlotType.UNIT)
            motif.add_slot("average_gain", avg_gain, SlotType.UNIT)
            
            perf = motif.get_slot("performance").value
            perf["applications"] = len(examples)
            perf["successes"] = sum(successful)
            perf["failures"] = len(examples) - sum(successful)
            perf["total_material_gain"] = sum(material_gains)
            
        return motif
        
    except Exception as e:
        logger.error(f"Error creating motif {name}: {e}")
        return None
