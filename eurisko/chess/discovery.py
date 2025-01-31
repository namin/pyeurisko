"""Chess discovery system built on Neo-Eurisko."""
import chess
import logging
from typing import Dict, List, Any, Optional, Tuple
from ..neo import NeoEurisko, Unit, SlotType
from .motifs import ChessMotif, create_basic_motifs
from .pattern_learner import analyze_position_change
from .pattern_concepts import ConceptDiscoverer
from collections import defaultdict

logger = logging.getLogger(__name__)

class ChessDiscoverySystem(NeoEurisko):
    """A system for discovering and evolving chess tactical patterns."""
    
    def __init__(self):
        super().__init__()
        self.patterns = []
        self.pattern_examples = defaultdict(list)
        self.concept_discoverer = ConceptDiscoverer()
        self.min_examples_for_pattern = 3
        
    def analyze_position(self, board: chess.Board) -> List[Dict[str, Any]]:
        """Analyze a position for tactical patterns."""
        findings = []
        try:
            relationships = analyze_position_change(board, board.copy(), None)
            findings.extend(self.extract_patterns(relationships))
        except Exception as e:
            logger.error(f"Error analyzing position: {e}")
        return findings
        
    def extract_patterns(self, relationships: Dict) -> List[Dict]:
        """Extract potential patterns from position relationships."""
        patterns = []
        
        # Look at piece relationships
        for rel in relationships.get('new_relations', []):
            pattern = {
                'pieces': [chess.piece_name(rel.from_piece.piece_type),
                          chess.piece_name(rel.to_piece.piece_type)],
                'relationship': rel.relation_type,
                'squares': [rel.from_square, rel.to_square]
            }
            patterns.append(pattern)
            
        # Look at geometric patterns
        for geo in relationships.get('new_patterns', []):
            pattern = {
                'pieces': [chess.piece_name(p.piece_type) for p in geo.pieces],
                'relationship': geo.pattern_type,
                'squares': geo.squares
            }
            patterns.append(pattern)
            
        return patterns
        
    def learn_from_puzzle(self, board: chess.Board, solution: List[str]):
        """Learn from a puzzle by analyzing positions and moves."""
        try:
            board_copy = board.copy()
            current_patterns = []
            moves = []
            
            # Analyze each move in the solution
            for move_uci in solution:
                move = chess.Move.from_uci(move_uci)
                moves.append(move)
                
                # Get patterns before move
                before_patterns = self.analyze_position(board_copy)
                
                # Make the move
                piece_captured = board_copy.piece_at(move.to_square)
                material_gain = self.calculate_material_gain(piece_captured)
                board_copy.push(move)
                
                # Get patterns after move
                after_patterns = self.analyze_position(board_copy)
                
                # Look for new or changed patterns
                new_patterns = self.find_new_patterns(before_patterns, after_patterns)
                for pattern in new_patterns:
                    pattern_key = self.get_pattern_key(pattern)
                    self.pattern_examples[pattern_key].append({
                        'board': board_copy.copy(),
                        'moves': moves.copy(),
                        'material_gain': material_gain
                    })
                    
                # Add to concept discoverer
                self.concept_discoverer.add_pattern_sequence(
                    pattern_key, moves.copy(), material_gain
                )
                
            # Update patterns database
            self.update_patterns()
            
        except Exception as e:
            logger.error(f"Error learning from puzzle: {e}")
            
    def calculate_material_gain(self, captured_piece: Optional[chess.Piece]) -> int:
        """Calculate material gain from a capture."""
        if not captured_piece:
            return 0
            
        values = {
            chess.PAWN: 1,
            chess.KNIGHT: 3,
            chess.BISHOP: 3,
            chess.ROOK: 5,
            chess.QUEEN: 9
        }
        return values.get(captured_piece.piece_type, 0)
        
    def find_new_patterns(self, before: List[Dict], after: List[Dict]) -> List[Dict]:
        """Find patterns that are new or changed after a move."""
        new_patterns = []
        before_keys = {self.get_pattern_key(p) for p in before}
        
        for pattern in after:
            key = self.get_pattern_key(pattern)
            if key not in before_keys:
                new_patterns.append(pattern)
                
        return new_patterns
        
    def get_pattern_key(self, pattern: Dict) -> str:
        """Generate a unique key for a pattern."""
        pieces = '_'.join(sorted(pattern['pieces']))
        return f"{pieces}_{pattern['relationship']}"
        
    def update_patterns(self):
        """Update the database of discovered patterns."""
        self.patterns = []
        
        for pattern_key, examples in self.pattern_examples.items():
            if len(examples) < self.min_examples_for_pattern:
                continue
                
            # Calculate success metrics
            successful = [ex for ex in examples if ex['material_gain'] > 0]
            success_rate = len(successful) / len(examples)
            avg_gain = sum(ex['material_gain'] for ex in examples) / len(examples)
            
            # Parse pattern info
            pieces = pattern_key.split('_')[:-1]  # Last part is relationship
            relationship = pattern_key.split('_')[-1]
            
            pattern = {
                'name': pattern_key,
                'pieces': pieces,
                'relationship': relationship,
                'success_rate': success_rate,
                'avg_gain': avg_gain,
                'examples': examples[:5]  # Keep top 5 examples
            }
            
            self.patterns.append(pattern)
            
    def discover_concepts(self) -> List[Dict]:
        """Discover higher-level chess concepts from patterns."""
        concepts = self.concept_discoverer.discover_concepts(self.patterns)
        return [
            {
                'name': concept.name,
                'patterns': len(concept.patterns),
                'success_rate': concept.success_rate,
                'avg_gain': concept.avg_material_gain,
                'core_features': concept.core_features
            }
            for concept in concepts
        ]
        
    def find_novel_patterns(self) -> List[Dict]:
        """Find successful patterns that don't match common chess concepts."""
        return self.concept_discoverer.get_novel_patterns()
