"""Discover meaningful chess tactical patterns."""
import chess
from dataclasses import dataclass
from typing import List, Dict, Set, Optional, Tuple
from collections import defaultdict

@dataclass
class TacticalPattern:
    """A meaningful chess tactical pattern."""
    key_pieces: List[Tuple[int, chess.Square]]  # The important pieces in the pattern
    relationships: List[str]  # How the pieces interact (e.g., "attacks", "controls", "blocks")
    material_gain: float  # Average material gain when this pattern is successful
    success_rate: float  # How often this pattern leads to material gain
    examples: List[Dict]  # Example positions showing this pattern
    common_themes: List[str]  # Common themes in puzzles where this appears

def get_piece_value(piece_type: int) -> int:
    """Get standard piece value."""
    values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9
    }
    return values.get(piece_type, 0)

def piece_name_to_type(name: str) -> int:
    """Convert piece name to type."""
    mapping = {
        'pawn': chess.PAWN,
        'knight': chess.KNIGHT,
        'bishop': chess.BISHOP,
        'rook': chess.ROOK,
        'queen': chess.QUEEN,
        'king': chess.KING
    }
    return mapping[name.lower()]

def piece_type_to_name(piece_type: int) -> str:
    """Convert piece type to name."""
    names = {
        chess.PAWN: 'pawn',
        chess.KNIGHT: 'knight',
        chess.BISHOP: 'bishop',
        chess.ROOK: 'rook',
        chess.QUEEN: 'queen',
        chess.KING: 'king'
    }
    return names.get(piece_type, 'unknown')

class PatternFinder:
    """Finds meaningful tactical patterns in chess positions."""
    
    def __init__(self):
        self.patterns = defaultdict(list)  # Group similar patterns
        
    def find_key_pieces(self, board: chess.Board, move: chess.Move) -> List[Tuple[int, chess.Square]]:
        """Find the key pieces involved in a tactical pattern."""
        key_pieces = []
        moved_piece = board.piece_at(move.from_square)
        if not moved_piece:
            return []
            
        # Get the moved piece
        key_pieces.append((moved_piece.piece_type, move.from_square))
        
        # Get captured piece if any
        captured = board.piece_at(move.to_square)
        if captured:
            key_pieces.append((captured.piece_type, move.to_square))
            
        # Get pieces being attacked after move
        board_copy = board.copy()
        board_copy.push(move)
        
        # Find newly attacked valuable pieces
        attacks = board_copy.attacks(move.to_square)
        for square in attacks:
            piece = board_copy.piece_at(square)
            if piece and piece.color != moved_piece.color:
                # Only include if it's a valuable target
                if get_piece_value(piece.piece_type) >= get_piece_value(moved_piece.piece_type):
                    key_pieces.append((piece.piece_type, square))
                    
        # Check for pieces in between (potential pins or discoveries)
        if len(key_pieces) > 1:
            between_squares = get_squares_between(move.from_square, move.to_square)
            for square in between_squares:
                piece = board.piece_at(square)
                if piece:
                    key_pieces.append((piece.piece_type, square))
                    
        return key_pieces

    def analyze_relationships(self, board: chess.Board, key_pieces: List[Tuple[int, chess.Square]]) -> List[str]:
        """Analyze how the key pieces relate to each other."""
        relationships = []
        
        # Check each pair of pieces
        for i, (piece1_type, sq1) in enumerate(key_pieces):
            for piece2_type, sq2 in key_pieces[i+1:]:
                # Are they aligned?
                if is_aligned(sq1, sq2):
                    # What's between them?
                    between = get_squares_between(sq1, sq2)
                    between_pieces = [board.piece_at(sq) for sq in between]
                    
                    if not any(between_pieces):
                        relationships.append("direct_attack")
                    elif len(between_pieces) == 1:
                        relationships.append("attack_through_piece")
                else:
                    # Check for knight patterns
                    file_diff = abs(chess.square_file(sq1) - chess.square_file(sq2))
                    rank_diff = abs(chess.square_rank(sq1) - chess.square_rank(sq2))
                    if (file_diff == 2 and rank_diff == 1) or (file_diff == 1 and rank_diff == 2):
                        relationships.append("knight_pattern")
                        
        return relationships

    def extract_pattern(self, board: chess.Board, move: chess.Move, material_gain: int, 
                       themes: List[str]) -> Optional[Dict]:
        """Extract a meaningful tactical pattern from a position."""
        # Find the key pieces
        key_pieces = self.find_key_pieces(board, move)
        if len(key_pieces) < 2:  # Need at least two pieces for a pattern
            return None
            
        # Analyze their relationships
        relationships = self.analyze_relationships(board, key_pieces)
        if not relationships:  # Need some meaningful relationship
            return None
            
        # Create pattern key for grouping similar patterns
        pattern_key = self.create_pattern_key(key_pieces, relationships)
        
        # Record the example
        example = {
            'fen': board.fen(),
            'move': move.uci(),
            'material_gain': material_gain,
            'themes': themes
        }
        self.patterns[pattern_key].append(example)
        
        return {
            'key_pieces': key_pieces,
            'relationships': relationships,
            'material_gain': material_gain,
            'example': example
        }
        
    def create_pattern_key(self, key_pieces: List[Tuple[int, chess.Square]], 
                          relationships: List[str]) -> str:
        """Create a key for grouping similar patterns."""
        # Sort pieces by value
        pieces = sorted(p[0] for p in key_pieces)
        piece_str = '_'.join(piece_type_to_name(p) for p in pieces)
        
        # Sort relationships
        rel_str = '_'.join(sorted(relationships))
        
        return f"{piece_str}_{rel_str}"
        
    def get_discovered_patterns(self, min_examples: int = 3, 
                              min_success_rate: float = 0.5) -> List[TacticalPattern]:
        """Get the meaningful patterns that were discovered."""
        discovered = []
        
        for pattern_key, examples in self.patterns.items():
            if len(examples) < min_examples:
                continue
                
            # Calculate success metrics
            successful = [ex for ex in examples if ex['material_gain'] > 0]
            if not successful:
                continue
                
            success_rate = len(successful) / len(examples)
            if success_rate < min_success_rate:
                continue
                
            # Get the piece types and relationships from the key
            pieces_str, rels_str = pattern_key.split('_', 1)
            piece_types = [piece_name_to_type(p) for p in pieces_str.split('_')]
            relationships = rels_str.split('_')
            
            # Calculate average material gain
            avg_gain = sum(ex['material_gain'] for ex in successful) / len(successful)
            
            # Find common themes
            theme_counts = defaultdict(int)
            for ex in examples:
                for theme in ex['themes']:
                    theme_counts[theme] += 1
            common_themes = [t for t, c in theme_counts.items() 
                           if c >= len(examples) * 0.3]
            
            pattern = TacticalPattern(
                key_pieces=[(pt, chess.A1) for pt in piece_types],  # Square doesn't matter for pattern
                relationships=relationships,
                material_gain=avg_gain,
                success_rate=success_rate,
                examples=examples[:3],  # Keep top 3 examples
                common_themes=common_themes
            )
            
            discovered.append(pattern)
            
        return discovered

def is_aligned(sq1: chess.Square, sq2: chess.Square) -> bool:
    """Check if two squares are aligned (same rank, file, or diagonal)."""
    file1, rank1 = chess.square_file(sq1), chess.square_rank(sq1)
    file2, rank2 = chess.square_file(sq2), chess.square_rank(sq2)
    
    return (file1 == file2 or  # Same file
            rank1 == rank2 or  # Same rank
            abs(file1 - file2) == abs(rank1 - rank2))  # Same diagonal

def get_squares_between(sq1: chess.Square, sq2: chess.Square) -> List[chess.Square]:
    """Get squares between two aligned squares."""
    file1, rank1 = chess.square_file(sq1), chess.square_rank(sq1)
    file2, rank2 = chess.square_file(sq2), chess.square_rank(sq2)
    
    squares = []
    if not is_aligned(sq1, sq2):
        return squares
        
    # Get step direction
    file_step = 0 if file1 == file2 else (file2 - file1) // abs(file2 - file1)
    rank_step = 0 if rank1 == rank2 else (rank2 - rank1) // abs(rank2 - rank1)
    
    # Get squares in between
    curr_file, curr_rank = file1 + file_step, rank1 + rank_step
    while (curr_file, curr_rank) != (file2, rank2):
        squares.append(chess.square(curr_file, curr_rank))
        curr_file += file_step
        curr_rank += rank_step
        
    return squares