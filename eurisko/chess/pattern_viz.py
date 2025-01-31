"""Visualize and summarize chess patterns."""
import chess
from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class PatternSummary:
    """Summary of common elements across multiple positions."""
    attacking_pieces: List[Tuple[chess.PieceType, Set[chess.Square]]]  # Pieces that commonly attack
    target_pieces: List[Tuple[chess.PieceType, Set[chess.Square]]]     # Pieces commonly attacked
    key_squares: Set[chess.Square]                                      # Important squares 
    common_moves: List[Tuple[chess.Square, chess.Square]]              # Common move patterns
    material_gains: List[int]                                          # Material gains seen
    themes: List[str]                                                  # Common themes

def board_to_ascii(board: chess.Board, highlight_squares: Optional[Set[chess.Square]] = None,
                  arrows: Optional[List[Tuple[chess.Square, chess.Square]]] = None) -> str:
    """Convert a board to ASCII with optional highlights and arrows."""
    piece_symbols = {
        'P': '♙', 'N': '♘', 'B': '♗', 'R': '♖', 'Q': '♕', 'K': '♔',
        'p': '♟', 'n': '♞', 'b': '♝', 'r': '♜', 'q': '♛', 'k': '♚',
        '.': '·'
    }
    
    highlight_squares = highlight_squares or set()
    arrows = arrows or []
    
    # Create the board representation
    lines = []
    lines.append('   a b c d e f g h')
    lines.append('  ─────────────────')
    
    for rank in range(7, -1, -1):
        row = f"{rank + 1} "
        for file in range(8):
            square = chess.square(file, rank)
            piece = board.piece_at(square)
            
            # Add highlighting
            if square in highlight_squares:
                row += '\033[94m' # Bright Blue
                
            if piece:
                symbol = piece_symbols[piece.symbol()]
            else:
                symbol = piece_symbols['.']
                
            row += f"{symbol}"
            
            if square in highlight_squares:
                row += '\033[0m'  # Reset color
                
            row += ' '
            
        # Add any arrows pointing to/from this rank
        arrow_annotations = []
        for from_square, to_square in arrows:
            if chess.square_rank(from_square) == rank or chess.square_rank(to_square) == rank:
                from_coord = chess.square_name(from_square)
                to_coord = chess.square_name(to_square)
                arrow_annotations.append(f"{from_coord}->{to_coord}")
                
        if arrow_annotations:
            row += f"  {'  '.join(arrow_annotations)}"
            
        lines.append(row)
        
    return '\n'.join(lines)

def find_common_elements(positions: List[Tuple[chess.Board, chess.Move]]) -> PatternSummary:
    """Find common elements across multiple pattern instances."""
    all_attacking_pieces = defaultdict(set)
    all_target_pieces = defaultdict(set)
    all_key_squares = set()
    all_moves = []
    material_gains = []
    themes = defaultdict(int)
    
    for board, move in positions:
        # Record the move
        all_moves.append((move.from_square, move.to_square))
        all_key_squares.add(move.from_square)
        all_key_squares.add(move.to_square)
        
        # Track attacking pieces
        moving_piece = board.piece_at(move.from_square)
        if moving_piece:
            all_attacking_pieces[moving_piece.piece_type].add(move.from_square)
            
            # Get squares attacked after move
            board_copy = board.copy()
            board_copy.push(move)
            for square in board_copy.attacks(move.to_square):
                piece = board_copy.piece_at(square)
                if piece and piece.color != moving_piece.color:
                    all_target_pieces[piece.piece_type].add(square)
                    all_key_squares.add(square)
                    
            # Calculate material gain
            captured = board.piece_at(move.to_square)
            if captured:
                values = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3,
                         chess.ROOK: 5, chess.QUEEN: 9}
                material_gains.append(values.get(captured.piece_type, 0))
                
    # Convert to list format
    attacking_pieces = [(pt, squares) for pt, squares in all_attacking_pieces.items()]
    target_pieces = [(pt, squares) for pt, squares in all_target_pieces.items()]
    
    # Sort moves by frequency
    move_counts = defaultdict(int)
    for move in all_moves:
        move_counts[move] += 1
    common_moves = sorted(move_counts.items(), key=lambda x: x[1], reverse=True)[:3]
    
    return PatternSummary(
        attacking_pieces=attacking_pieces,
        target_pieces=target_pieces,
        key_squares=all_key_squares,
        common_moves=common_moves,
        material_gains=material_gains,
        themes=themes
    )

def describe_pattern(pattern_summary: PatternSummary) -> str:
    """Create a human-readable description of a pattern."""
    description = []
    
    # Describe attacking pieces
    for piece_type, squares in pattern_summary.attacking_pieces:
        piece_name = chess.piece_name(piece_type)
        if len(squares) == 1:
            sq = list(squares)[0]
            description.append(f"{piece_name} on {chess.square_name(sq)} attacks")
        else:
            squares_str = ', '.join(chess.square_name(sq) for sq in squares)
            description.append(f"{piece_name}s on {squares_str} attack")
            
    # Describe target pieces
    for piece_type, squares in pattern_summary.target_pieces:
        piece_name = chess.piece_name(piece_type)
        squares_str = ', '.join(chess.square_name(sq) for sq in squares)
        description.append(f"{piece_name} on {squares_str} is targeted")
        
    # Describe material gains
    if pattern_summary.material_gains:
        avg_gain = sum(pattern_summary.material_gains) / len(pattern_summary.material_gains)
        description.append(f"Average material gain: {avg_gain:.1f} pawns")
        
    # Describe common themes
    if pattern_summary.themes:
        themes_str = ', '.join(f"{t}" for t in pattern_summary.themes)
        description.append(f"Common themes: {themes_str}")
        
    return '\n'.join(description)

def show_pattern(pattern_summary: PatternSummary, example_position: Tuple[chess.Board, chess.Move]):
    """Show a pattern with board visualization and description."""
    board, move = example_position
    
    print("Pattern Summary:")
    print(describe_pattern(pattern_summary))
    print("\nExample Position:")
    print(board_to_ascii(board, 
                        highlight_squares=pattern_summary.key_squares,
                        arrows=[(move.from_square, move.to_square)]))
                        
    # Show position after move
    board_after = board.copy()
    board_after.push(move)
    print("\nAfter move:")
    print(board_to_ascii(board_after, highlight_squares=pattern_summary.key_squares))
