"""Discover minimal tactical patterns in chess positions."""
import chess
from dataclasses import dataclass
from typing import List, Dict, Set, Tuple, Optional
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

@dataclass
class MinimalPattern:
    """A pattern involving 2-3 pieces in a specific relationship."""
    pieces: List[Tuple[chess.Piece, chess.Square]]  # The pieces involved
    relationship: str  # Type of relationship (aligned, knight_move, etc)
    control_squares: Set[chess.Square]  # Squares controlled by these pieces
    relative_value: int  # Value of target piece relative to attacker
    
    def __hash__(self):
        return hash(str(self.pieces) + self.relationship)

def get_piece_value(piece: chess.Piece) -> int:
    """Get standard piece value."""
    values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
        chess.KING: 99
    }
    return values[piece.piece_type]

def find_minimal_patterns(board: chess.Board) -> List[MinimalPattern]:
    """Find all minimal patterns in position."""
    patterns = []
    pieces = [(board.piece_at(sq), sq) for sq in chess.SQUARES if board.piece_at(sq)]
    
    # Look for 2-piece patterns
    for i, (piece1, sq1) in enumerate(pieces):
        for piece2, sq2 in pieces[i+1:]:
            # Skip if same color
            if piece1.color == piece2.color:
                continue
                
            # Get geometric relationship
            file1, rank1 = chess.square_file(sq1), chess.square_rank(sq1)
            file2, rank2 = chess.square_file(sq2), chess.square_rank(sq2)
            
            relationship = None
            control_squares = set()
            
            # Check alignment
            if file1 == file2:
                relationship = "vertical"
                # Get squares between
                min_rank, max_rank = min(rank1, rank2), max(rank1, rank2)
                control_squares = {chess.square(file1, r) for r in range(min_rank + 1, max_rank)}
            elif rank1 == rank2:
                relationship = "horizontal"
                min_file, max_file = min(file1, file2), max(file1, file2)
                control_squares = {chess.square(f, rank1) for f in range(min_file + 1, max_file)}
            elif abs(file1 - file2) == abs(rank1 - rank2):
                relationship = "diagonal"
                # Get squares between
                step_file = 1 if file2 > file1 else -1
                step_rank = 1 if rank2 > rank1 else -1
                f, r = file1 + step_file, rank1 + step_rank
                while (f, r) != (file2, rank2):
                    control_squares.add(chess.square(f, r))
                    f += step_file
                    r += step_rank
            elif abs(file1 - file2) * abs(rank1 - rank2) == 2:  # Knight move pattern
                relationship = "knight_move"
                control_squares = {sq2}  # Just the target square
                
            if relationship:
                patterns.append(MinimalPattern(
                    pieces=[(piece1, sq1), (piece2, sq2)],
                    relationship=relationship,
                    control_squares=control_squares,
                    relative_value=get_piece_value(piece2) - get_piece_value(piece1)
                ))
                
    # Look for 3-piece patterns where middle piece is attacked
    for pat in patterns[:]:  # Work with copy as we'll be adding
        piece1, sq1 = pat.pieces[0]
        piece2, sq2 = pat.pieces[1]
        
        # Check for pieces in between
        for sq in pat.control_squares:
            middle_piece = board.piece_at(sq)
            if middle_piece:
                # Found a piece in between
                patterns.append(MinimalPattern(
                    pieces=[(piece1, sq1), (middle_piece, sq), (piece2, sq2)],
                    relationship=f"{pat.relationship}_through",
                    control_squares=pat.control_squares,
                    relative_value=max(
                        get_piece_value(middle_piece) - get_piece_value(piece1),
                        get_piece_value(piece2) - get_piece_value(piece1)
                    )
                ))
                
    return patterns

class MinimalPatternLearner:
    """Learn minimal tactical patterns from positions."""
    def __init__(self):
        self.pattern_stats = defaultdict(lambda: {
            'count': 0,
            'success_count': 0,
            'material_gains': [],
            'examples': []
        })
        
    def learn_from_position(self, board: chess.Board, next_move: chess.Move,
                          material_gained: int):
        """Learn from a position and its outcome."""
        # Find all minimal patterns
        patterns = find_minimal_patterns(board)
        
        # Track which ones are "activated" by the move
        moving_piece = board.piece_at(next_move.from_square)
        if not moving_piece:
            return
            
        for pattern in patterns:
            # Check if move involves this pattern
            if (moving_piece, next_move.from_square) in pattern.pieces:
                # Pattern was used
                key = (
                    pattern.relationship,
                    tuple(p.piece_type for p, _ in pattern.pieces),
                    pattern.relative_value
                )
                
                self.pattern_stats[key]['count'] += 1
                if material_gained > 0:
                    self.pattern_stats[key]['success_count'] += 1
                self.pattern_stats[key]['material_gains'].append(material_gained)
                self.pattern_stats[key]['examples'].append({
                    'fen': board.fen(),
                    'move': next_move.uci(),
                    'gain': material_gained
                })
                
    def get_discovered_patterns(self, min_examples: int = 3,
                              min_success_rate: float = 0.5) -> List[Dict]:
        """Get patterns that have been discovered."""
        discoveries = []
        
        for key, stats in self.pattern_stats.items():
            if stats['count'] >= min_examples:
                success_rate = stats['success_count'] / stats['count']
                if success_rate >= min_success_rate:
                    relationship, piece_types, rel_value = key
                    pieces = [chess.piece_name(pt) for pt in piece_types]
                    
                    discoveries.append({
                        'pieces': pieces,
                        'relationship': relationship,
                        'relative_value': rel_value,
                        'count': stats['count'],
                        'success_rate': success_rate,
                        'avg_gain': sum(stats['material_gains']) / len(stats['material_gains']),
                        'examples': stats['examples'][:3]  # Just show first 3 examples
                    })
                    
        return discoveries
