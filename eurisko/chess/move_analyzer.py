"""Basic chess move analysis."""
import chess
from dataclasses import dataclass
from typing import List, Dict, Set, Optional
import logging

logger = logging.getLogger(__name__)

@dataclass
class MovePattern:
    """A pattern found in a chess move."""
    piece_type: chess.PieceType  # What piece moved
    captured_piece: Optional[chess.PieceType]  # What was captured (if anything)
    attacked_pieces: List[chess.PieceType]  # What pieces are now attacked
    distance: int  # How far the piece moved
    is_check: bool  # Did it give check?
    material_gain: int  # Material gained by the move

def analyze_move(board: chess.Board, move: chess.Move) -> MovePattern:
    """Analyze a single move to extract its key features."""
    # Get the moving piece
    from_square = move.from_square
    to_square = move.to_square
    moving_piece = board.piece_at(from_square)
    
    # Get captured piece if any
    captured_piece = board.piece_at(to_square)
    
    # Calculate move distance
    from_rank = chess.square_rank(from_square)
    from_file = chess.square_file(from_square)
    to_rank = chess.square_rank(to_square)
    to_file = chess.square_file(to_square)
    distance = max(abs(from_rank - to_rank), abs(from_file - to_file))
    
    # Make the move on a copy to analyze the resulting position
    board_copy = board.copy()
    board_copy.push(move)
    
    # Get pieces now attacked by the moved piece
    attacked_pieces = []
    attacked = board_copy.attacks(to_square)
    for square in attacked:
        piece = board_copy.piece_at(square)
        if piece and piece.color != moving_piece.color:
            attacked_pieces.append(piece.piece_type)
            
    # Calculate material change
    material_gain = 0
    if captured_piece:
        piece_values = {
            chess.PAWN: 1,
            chess.KNIGHT: 3,
            chess.BISHOP: 3,
            chess.ROOK: 5,
            chess.QUEEN: 9
        }
        material_gain = piece_values.get(captured_piece.piece_type, 0)
    
    return MovePattern(
        piece_type=moving_piece.piece_type,
        captured_piece=captured_piece.piece_type if captured_piece else None,
        attacked_pieces=attacked_pieces,
        distance=distance,
        is_check=board_copy.is_check(),
        material_gain=material_gain
    )

class PatternCollector:
    """Collects and groups similar move patterns."""
    def __init__(self):
        self.patterns = []  # List of all patterns seen
        self.successful_patterns = []  # Patterns that led to material gain
        
    def add_pattern(self, pattern: MovePattern, themes: List[str]):
        """Add a new pattern example."""
        self.patterns.append((pattern, themes))
        if pattern.material_gain > 0 or pattern.is_check:
            self.successful_patterns.append((pattern, themes))
            
    def find_common_patterns(self, min_examples: int = 3) -> List[Dict]:
        """Find patterns that appear multiple times."""
        # Group patterns by piece type and outcome
        groups = {}
        for pattern, themes in self.successful_patterns:
            key = (
                pattern.piece_type,
                bool(pattern.captured_piece),
                bool(pattern.attacked_pieces),
                pattern.is_check
            )
            if key not in groups:
                groups[key] = {
                    'count': 0,
                    'examples': [],
                    'themes': set(),
                    'total_gain': 0
                }
            groups[key]['count'] += 1
            groups[key]['examples'].append(pattern)
            groups[key]['themes'].update(themes)
            groups[key]['total_gain'] += pattern.material_gain
            
        # Keep groups with enough examples
        common_patterns = []
        for key, group in groups.items():
            if group['count'] >= min_examples:
                piece_type, has_capture, has_attacks, gives_check = key
                pattern_desc = {
                    'piece': chess.piece_name(piece_type),
                    'captures': has_capture,
                    'attacks': has_attacks,
                    'gives_check': gives_check,
                    'count': group['count'],
                    'avg_gain': group['total_gain'] / group['count'],
                    'themes': list(group['themes'])
                }
                common_patterns.append(pattern_desc)
                
        return common_patterns
