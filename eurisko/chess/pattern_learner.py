"""Pattern learning system for chess motifs."""
import chess
from typing import Dict, List, Any, Tuple, Set
from dataclasses import dataclass
import math

@dataclass
class PieceRelation:
    """Represents a relationship between two pieces."""
    from_piece: chess.Piece
    from_square: chess.Square
    to_piece: chess.Piece
    to_square: chess.Square
    relation_type: str  # "attacks", "controls", "blocks", "guards"
    
@dataclass
class GeometricPattern:
    """Represents a geometric pattern between pieces."""
    pieces: List[chess.Piece]
    squares: List[chess.Square]
    pattern_type: str  # "line", "diagonal", "knight_move", etc.
    
def get_piece_relations(board: chess.Board) -> List[PieceRelation]:
    """Discover all piece relationships on the board."""
    relations = []
    
    for from_square in chess.SQUARES:
        from_piece = board.piece_at(from_square)
        if not from_piece:
            continue
            
        # Find pieces being attacked
        attacked = board.attacks(from_square)
        for to_square in attacked:
            to_piece = board.piece_at(to_square)
            if to_piece:
                if to_piece.color != from_piece.color:
                    relations.append(PieceRelation(
                        from_piece=from_piece,
                        from_square=from_square,
                        to_piece=to_piece,
                        to_square=to_square,
                        relation_type="attacks"
                    ))
                else:
                    relations.append(PieceRelation(
                        from_piece=from_piece,
                        from_square=from_square,
                        to_piece=to_piece,
                        to_square=to_square,
                        relation_type="guards"
                    ))
                    
        # Find blocked pieces
        if from_piece.piece_type == chess.PAWN:
            continue  # Skip pawns for simplicity
            
        piece_moves = get_piece_movement_squares(from_piece, from_square)
        for move_square in piece_moves:
            blocking_piece, blocking_square = find_first_piece_in_line(board, from_square, move_square)
            if blocking_piece:
                relations.append(PieceRelation(
                    from_piece=from_piece,
                    from_square=from_square,
                    to_piece=blocking_piece,
                    to_square=blocking_square,
                    relation_type="blocks"
                ))
                
    return relations

def get_piece_movement_squares(piece: chess.Piece, square: chess.Square) -> Set[chess.Square]:
    """Get all squares a piece could potentially move to, ignoring other pieces."""
    moves = set()
    rank, file = chess.square_rank(square), chess.square_file(square)
    
    if piece.piece_type == chess.BISHOP:
        # Diagonal moves
        for i in range(1, 8):
            for rank_dir, file_dir in [(1,1), (1,-1), (-1,1), (-1,-1)]:
                new_rank, new_file = rank + i*rank_dir, file + i*file_dir
                if 0 <= new_rank < 8 and 0 <= new_file < 8:
                    moves.add(chess.square(new_file, new_rank))
                    
    elif piece.piece_type == chess.ROOK:
        # Horizontal and vertical moves
        for i in range(8):
            if i != file:
                moves.add(chess.square(i, rank))
            if i != rank:
                moves.add(chess.square(file, i))
                
    elif piece.piece_type == chess.QUEEN:
        # Combine bishop and rook moves
        moves.update(get_piece_movement_squares(chess.Piece(chess.BISHOP, piece.color), square))
        moves.update(get_piece_movement_squares(chess.Piece(chess.ROOK, piece.color), square))
        
    elif piece.piece_type == chess.KNIGHT:
        # Knight moves
        for rank_change, file_change in [(2,1), (2,-1), (-2,1), (-2,-1), 
                                       (1,2), (1,-2), (-1,2), (-1,-2)]:
            new_rank, new_file = rank + rank_change, file + file_change
            if 0 <= new_rank < 8 and 0 <= new_file < 8:
                moves.add(chess.square(new_file, new_rank))
                
    return moves

def find_first_piece_in_line(board: chess.Board, from_square: chess.Square, 
                            to_square: chess.Square) -> Tuple[chess.Piece, chess.Square]:
    """Find the first piece encountered when moving from one square to another."""
    from_rank = chess.square_rank(from_square)
    from_file = chess.square_file(from_square)
    to_rank = chess.square_rank(to_square)
    to_file = chess.square_file(to_square)
    
    # Get direction
    rank_dir = 0 if from_rank == to_rank else (to_rank - from_rank) // abs(to_rank - from_rank)
    file_dir = 0 if from_file == to_file else (to_file - from_file) // abs(to_file - from_file)
    
    curr_rank, curr_file = from_rank + rank_dir, from_file + file_dir
    while 0 <= curr_rank < 8 and 0 <= curr_file < 8:
        square = chess.square(curr_file, curr_rank)
        piece = board.piece_at(square)
        if piece:
            return (piece, square)
            
        if (curr_rank, curr_file) == (to_rank, to_file):
            break
            
        curr_rank += rank_dir
        curr_file += file_dir
        
    return (None, None)

def find_geometric_patterns(relations: List[PieceRelation]) -> List[GeometricPattern]:
    """Identify geometric patterns from piece relationships."""
    patterns = []
    
    # Look for aligned pieces (3 or more pieces in a line)
    pieces_by_rank = {}
    pieces_by_file = {}
    pieces_by_diagonal = {}  # Key will be (rank-file) for one diagonal family
    pieces_by_antidiagonal = {}  # Key will be (rank+file) for other diagonal family
    
    for rel in relations:
        # Record both ends of each relation
        for piece, square in [(rel.from_piece, rel.from_square), 
                            (rel.to_piece, rel.to_square)]:
            rank = chess.square_rank(square)
            file = chess.square_file(square)
            
            # Record in each line type
            pieces_by_rank.setdefault(rank, []).append((piece, square))
            pieces_by_file.setdefault(file, []).append((piece, square))
            pieces_by_diagonal.setdefault(rank-file, []).append((piece, square))
            pieces_by_antidiagonal.setdefault(rank+file, []).append((piece, square))
    
    # Find aligned pieces
    for pieces_dict, pattern_type in [
        (pieces_by_rank, "horizontal"),
        (pieces_by_file, "vertical"),
        (pieces_by_diagonal, "diagonal"),
        (pieces_by_antidiagonal, "antidiagonal")
    ]:
        for line_pieces in pieces_dict.values():
            if len(line_pieces) >= 3:
                patterns.append(GeometricPattern(
                    pieces=[p[0] for p in line_pieces],
                    squares=[p[1] for p in line_pieces],
                    pattern_type=pattern_type
                ))
                
    return patterns

def analyze_position_change(before_board: chess.Board, after_board: chess.Board, 
                          move: chess.Move) -> Dict[str, Any]:
    """Analyze how a move changes piece relationships and patterns."""
    # Get relationships before and after
    before_relations = get_piece_relations(before_board)
    after_relations = get_piece_relations(after_board)
    
    # Get geometric patterns before and after
    before_patterns = find_geometric_patterns(before_relations)
    after_patterns = find_geometric_patterns(after_relations)
    
    # Analyze what changed
    new_relations = []
    for rel in after_relations:
        if rel not in before_relations:
            new_relations.append(rel)
            
    new_patterns = []
    for pattern in after_patterns:
        if pattern not in before_patterns:
            new_patterns.append(pattern)
            
    return {
        "move": move,
        "new_relations": new_relations,
        "new_patterns": new_patterns,
        "material_change": count_material_change(before_board, after_board)
    }

def count_material_change(before_board: chess.Board, after_board: chess.Board) -> int:
    """Calculate material change from a move."""
    piece_values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9
    }
    
    def count_material(board: chess.Board, color: bool) -> int:
        return sum(
            len(board.pieces(piece_type, color)) * value
            for piece_type, value in piece_values.items()
        )
    
    before_material = count_material(before_board, before_board.turn) - \
                     count_material(before_board, not before_board.turn)
                     
    after_material = count_material(after_board, before_board.turn) - \
                    count_material(after_board, not before_board.turn)
                    
    return after_material - before_material
