"""Raw chess position analysis without predefined patterns."""
import chess
from dataclasses import dataclass
from typing import List, Dict, Set, Tuple, Optional
import numpy as np
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

@dataclass
class PositionFeature:
    """Raw geometric/tactical features of a position."""
    # Ray features (pieces along same line)
    rays: List[Tuple[chess.Piece, chess.Piece, str]]  # (piece1, piece2, direction)
    
    # Attack relationships
    attacks: List[Tuple[chess.Piece, chess.Square, chess.Piece]]  # (attacker, through_square, target)
    
    # Mobility features
    piece_mobility: Dict[chess.Piece, int]  # piece -> number of legal moves
    
    def __hash__(self):
        return hash(str(self.rays) + str(self.attacks))

def get_ray_direction(sq1: chess.Square, sq2: chess.Square) -> Optional[str]:
    """Get direction of alignment between squares if they're on same rank/file/diagonal."""
    file1, rank1 = chess.square_file(sq1), chess.square_rank(sq1)
    file2, rank2 = chess.square_file(sq2), chess.square_rank(sq2)
    
    if file1 == file2:
        return "vertical"
    if rank1 == rank2:
        return "horizontal"
    if abs(file1 - file2) == abs(rank1 - rank2):
        return "diagonal"
    return None

def get_piece_list(board: chess.Board) -> List[Tuple[chess.Piece, chess.Square]]:
    """Get list of all pieces and their squares."""
    pieces = []
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            pieces.append((piece, square))
    return pieces

def find_piece_between(board: chess.Board, sq1: chess.Square, sq2: chess.Square) -> Optional[chess.Square]:
    """Find if there's a piece between two squares on a line."""
    file1, rank1 = chess.square_file(sq1), chess.square_rank(sq1)
    file2, rank2 = chess.square_file(sq2), chess.square_rank(sq2)
    
    # Get direction
    file_step = 0 if file1 == file2 else (file2 - file1) // abs(file2 - file1)
    rank_step = 0 if rank1 == rank2 else (rank2 - rank1) // abs(rank2 - rank1)
    
    # Check squares between
    curr_file, curr_rank = file1 + file_step, rank1 + rank_step
    while (curr_file, curr_rank) != (file2, rank2):
        square = chess.square(curr_file, curr_rank)
        if board.piece_at(square):
            return square
        curr_file += file_step
        curr_rank += rank_step
    
    return None

def extract_features(board: chess.Board) -> PositionFeature:
    """Extract raw features from a position."""
    pieces = get_piece_list(board)
    
    # Find rays (pieces aligned on same line)
    rays = []
    for i, (piece1, sq1) in enumerate(pieces):
        for piece2, sq2 in pieces[i+1:]:
            direction = get_ray_direction(sq1, sq2)
            if direction:
                rays.append((piece1, piece2, direction))
    
    # Find attack relationships through squares
    attacks = []
    for piece, square in pieces:
        # Get all squares this piece attacks
        for attacked_square in board.attacks(square):
            target = board.piece_at(attacked_square)
            if target and target.color != piece.color:
                # Found an attack - record the square it goes through
                through_square = find_piece_between(board, square, attacked_square)
                attacks.append((piece, through_square, target))
    
    # Calculate piece mobility
    mobility = {}
    for piece, square in pieces:
        moves = len([sq for sq in board.attacks(square) 
                    if not board.piece_at(sq) or 
                    board.piece_at(sq).color != piece.color])
        mobility[piece] = moves
    
    return PositionFeature(rays=rays, attacks=attacks, piece_mobility=mobility)

class PositionPattern:
    """A discovered pattern in chess positions."""
    def __init__(self, name: str):
        self.name = name
        self.ray_patterns = defaultdict(int)  # Count of piece alignments
        self.attack_patterns = defaultdict(int)  # Count of attack relationships
        self.mobility_patterns = defaultdict(list)  # Mobility statistics
        self.examples = []
        self.material_gains = []
        
    def add_example(self, features: PositionFeature, material_gained: int):
        """Add a position example to this pattern."""
        self.examples.append(features)
        self.material_gains.append(material_gained)
        
        # Update ray patterns
        for p1, p2, direction in features.rays:
            self.ray_patterns[(p1.piece_type, p2.piece_type, direction)] += 1
            
        # Update attack patterns
        for attacker, through, target in features.attacks:
            key = (attacker.piece_type, 
                  bool(through),  # Just track if there's an intervening piece
                  target.piece_type)
            self.attack_patterns[key] += 1
            
        # Update mobility patterns
        for piece, moves in features.piece_mobility.items():
            self.mobility_patterns[piece.piece_type].append(moves)
            
    def similarity(self, features: PositionFeature) -> float:
        """Calculate how similar a position is to this pattern."""
        if not self.examples:
            return 0.0
            
        score = 0.0
        # Check ray patterns
        for p1, p2, direction in features.rays:
            key = (p1.piece_type, p2.piece_type, direction)
            if self.ray_patterns[key] > len(self.examples) * 0.5:
                score += 1.0
                
        # Check attack patterns
        for attacker, through, target in features.attacks:
            key = (attacker.piece_type, bool(through), target.piece_type)
            if self.attack_patterns[key] > len(self.examples) * 0.5:
                score += 1.0
                
        return score / (1 + len(features.rays) + len(features.attacks))

class PatternLearner:
    """Learns patterns from position features."""
    def __init__(self):
        self.patterns: List[PositionPattern] = []
        self.min_similarity = 0.7
        
    def add_position(self, before_features: PositionFeature, 
                    after_features: PositionFeature,
                    material_gained: int):
        """Add a position transition to learn from."""
        # Try to match with existing patterns
        best_match = None
        best_score = 0
        
        for pattern in self.patterns:
            score = pattern.similarity(before_features)
            if score > best_score:
                best_score = score
                best_match = pattern
                
        # If good match found, add to that pattern
        if best_match and best_score >= self.min_similarity:
            best_match.add_example(before_features, material_gained)
        else:
            # Create new pattern
            pattern = PositionPattern(f"pattern_{len(self.patterns)}")
            pattern.add_example(before_features, material_gained)
            self.patterns.append(pattern)
            
    def find_patterns(self, min_examples: int = 3, min_success: float = 0.5) -> List[Dict]:
        """Find recurring patterns that often lead to material gain."""
        significant = []
        
        for pattern in self.patterns:
            if len(pattern.examples) < min_examples:
                continue
                
            # Calculate success metrics
            success_rate = sum(1 for g in pattern.material_gains if g > 0) / len(pattern.material_gains)
            if success_rate < min_success:
                continue
                
            # Get common features
            common = {
                'rays': [(p1,p2,d) for (p1,p2,d), count in pattern.ray_patterns.items()
                        if count >= len(pattern.examples) * 0.5],
                'attacks': [(a,t,b) for (a,b,t), count in pattern.attack_patterns.items()
                           if count >= len(pattern.examples) * 0.5],
                'avg_mobility': {
                    piece: sum(moves)/len(moves)
                    for piece, moves in pattern.mobility_patterns.items()
                    if moves
                }
            }
            
            significant.append({
                'name': pattern.name,
                'examples': len(pattern.examples),
                'success_rate': success_rate,
                'avg_gain': sum(pattern.material_gains) / len(pattern.material_gains),
                'features': common
            })
            
        return significant
