"""Chess discovery system built on Neo-Eurisko."""
import chess
import logging
from typing import Dict, List, Any, Optional, Tuple
from ..neo import NeoEurisko, Unit, SlotType
from .motifs import ChessMotif, create_motif_from_analysis
from .pattern_learner import analyze_position_change, PieceRelation, GeometricPattern
from collections import defaultdict

logger = logging.getLogger(__name__)

class ChessDiscoverySystem(NeoEurisko):
    """A system for discovering and evolving chess tactical patterns."""
    
    def __init__(self):
        super().__init__()
        self.motifs: Dict[str, ChessMotif] = {}
        self.pattern_examples = defaultdict(list)  # Collects examples for pattern discovery
        self.min_examples_for_motif = 3  # Reduced from 5 to be more lenient
        
    def analyze_position(self, board: chess.Board) -> List[Dict[str, Any]]:
        """Apply all known motif detection heuristics to a position."""
        findings = []
        for motif in self.motifs.values():
            try:
                result = motif.detect(board)
                if result["instances"]:
                    findings.append(result)
            except Exception as e:
                logger.error(f"Error detecting motif {motif.name}: {e}")
        return findings
        
    def learn_from_puzzle(self, board: chess.Board, solution: List[str], themes: List[str]):
        """Learn from a puzzle by analyzing the positions and moves."""
        try:
            board_copy = board.copy()
            all_analyses = []
            
            # Analyze each move in the solution
            for move_uci in solution:
                move = chess.Move.from_uci(move_uci)
                
                # Analyze position before and after move
                analysis = analyze_position_change(board_copy, board_copy.copy(), move)
                analysis['themes'] = themes
                analysis['position'] = board_copy.fen()
                
                # Add to collected analyses
                all_analyses.append(analysis)
                
                # Store the analysis for pattern learning
                self.collect_pattern_example(analysis)
                
                # Make the move
                board_copy.push(move)
                
            # Try to discover new patterns after collecting all analyses
            self.discover_patterns(all_analyses)
                
        except Exception as e:
            logger.error(f"Error learning from puzzle: {e}")
            
    def collect_pattern_example(self, analysis: Dict):
        """Collect an example of a potential pattern."""
        # Extract key features from the analysis
        features = self.extract_key_features(analysis)
        
        for feature_set in features:
            # Create a pattern key from the features
            pattern_key = tuple(sorted(feature_set))
            
            # Store the complete analysis with these features
            self.pattern_examples[pattern_key].append(analysis)
            
    def extract_key_features(self, analysis: Dict) -> List[set]:
        """Extract key features that might indicate a tactical pattern."""
        features = []
        
        # Look at new piece relations
        for relation in analysis.get("new_relations", []):
            # Basic relation features
            relation_features = {
                f"relation_{relation.relation_type}",
                f"from_{chess.piece_name(relation.from_piece.piece_type)}",
                f"to_{chess.piece_name(relation.to_piece.piece_type)}"
            }
            features.append(relation_features)
            
            # Add theme-based features if present
            if analysis.get('themes'):
                for theme in analysis['themes']:
                    relation_features.add(f"theme_{theme}")
            
        # Look at new geometric patterns
        for pattern in analysis.get("new_patterns", []):
            pattern_features = {
                f"geometry_{pattern.pattern_type}",
                f"piece_count_{len(pattern.pieces)}"
            }
            # Add piece types involved
            for piece in pattern.pieces:
                pattern_features.add(f"uses_{chess.piece_name(piece.piece_type)}")
            features.append(pattern_features)
            
        return features
        
    def discover_patterns(self, analyses: List[Dict]):
        """Try to discover new patterns from collected examples."""
        for feature_key, examples in self.pattern_examples.items():
            if len(examples) >= self.min_examples_for_motif:
                # Create a descriptive name from the features
                pattern_name = self.create_pattern_name(feature_key)
                
                if pattern_name not in self.motifs:
                    # Try to create a new motif
                    motif = create_motif_from_analysis(pattern_name, examples)
                    if motif:
                        # Calculate success metrics
                        material_gains = [ex.get("material_change", 0) for ex in examples]
                        successful_gains = [g for g in material_gains if g > 0]
                        
                        if len(successful_gains) > 0:
                            success_rate = len(successful_gains) / len(examples)
                            if success_rate > 0.3:  # At least 30% success rate
                                logger.info(f"Discovered new pattern: {pattern_name}")
                                self.motifs[pattern_name] = motif
                                self.units[pattern_name] = motif
                                
    def create_pattern_name(self, feature_key: tuple) -> str:
        """Create a descriptive name for a pattern based on its features."""
        # Extract main components
        relations = [f for f in feature_key if f.startswith("relation_")]
        geometries = [f for f in feature_key if f.startswith("geometry_")]
        pieces = [f for f in feature_key if f.startswith("from_") or f.startswith("to_")]
        themes = [f for f in feature_key if f.startswith("theme_")]
        
        name_parts = []
        
        # Add main relation type if present
        if relations:
            name_parts.append(relations[0].replace("relation_", ""))
            
        # Add geometry if present
        if geometries:
            name_parts.append(geometries[0].replace("geometry_", ""))
            
        # Add piece types if present
        if pieces:
            piece_names = [p.split("_")[1] for p in pieces]
            name_parts.extend(piece_names[:2])  # Just take first two pieces
            
        # Add theme if present
        if themes:
            name_parts.append(themes[0].replace("theme_", ""))
            
        return "_".join(name_parts)
        
    def get_pattern_statistics(self) -> Dict[str, Dict]:
        """Get statistics about discovered patterns."""
        stats = {}
        for name, motif in self.motifs.items():
            perf = motif.get_slot("performance").value
            success_rate = motif.get_slot("success_rate").value
            avg_gain = motif.get_slot("average_gain").value
            examples = motif.get_slot("examples").value
            
            stats[name] = {
                "success_rate": success_rate,
                "average_gain": avg_gain,
                "total_applications": perf["applications"],
                "examples_count": len(examples),
                "themes": list(set(
                    theme for ex in examples 
                    for theme in ex.get('themes', [])
                ))
            }
        return stats
