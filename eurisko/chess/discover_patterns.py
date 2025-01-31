"""Discover chess patterns from raw positions."""
import chess
import logging
from typing import Optional
import argparse
from .position_learner import PatternLearner, extract_features

logger = logging.getLogger(__name__)

def describe_pattern(pattern: dict) -> str:
    """Create human-readable description of a pattern."""
    desc = []
    
    # Describe ray alignments
    for piece1, piece2, direction in pattern['features']['rays']:
        desc.append(f"- {chess.piece_name(piece1)} and {chess.piece_name(piece2)} aligned {direction}ly")
        
    # Describe attacks
    for attacker, target, through in pattern['features']['attacks']:
        base = f"- {chess.piece_name(attacker)} attacks {chess.piece_name(target)}"
        if through:
            base += " through another piece"
        desc.append(base)
        
    # Describe mobility
    for piece, moves in pattern['features']['avg_mobility'].items():
        desc.append(f"- {chess.piece_name(piece)} averages {moves:.1f} possible moves")
        
    return "\n".join(desc)

def process_puzzles(filename: str, num_puzzles: Optional[int] = None):
    """Process puzzles to discover patterns."""
    learner = PatternLearner()
    puzzles_processed = 0
    
    print("Starting pattern discovery...")
    
    with open(filename) as f:
        # Skip header
        next(f)
        
        for line in f:
            if num_puzzles and puzzles_processed >= num_puzzles:
                break
                
            try:
                # Parse puzzle
                fields = line.strip().split(',')
                fen = fields[1]  # FEN is second field
                moves = fields[2].split()  # Moves are third field
                board = chess.Board(fen)
                
                # For each move, analyze position before and after
                for move_uci in moves:
                    try:
                        # Extract features before move
                        before_features = extract_features(board)
                        
                        # Make the move
                        move = chess.Move.from_uci(move_uci)
                        piece_captured = board.piece_at(move.to_square)
                        
                        # Calculate material gain
                        material_gained = 0
                        if piece_captured:
                            piece_values = {
                                chess.PAWN: 1,
                                chess.KNIGHT: 3,
                                chess.BISHOP: 3,
                                chess.ROOK: 5,
                                chess.QUEEN: 9
                            }
                            material_gained = piece_values.get(piece_captured.piece_type, 0)
                            
                        board.push(move)
                        
                        # Extract features after move
                        after_features = extract_features(board)
                        
                        # Add to learner
                        learner.add_position(before_features, after_features, material_gained)
                        
                    except Exception as e:
                        logger.error(f"Error processing move: {e}")
                        continue
                    
                puzzles_processed += 1
                if puzzles_processed % 100 == 0:
                    print(f"\nProcessed {puzzles_processed} puzzles")
                    show_patterns(learner)
                    
            except Exception as e:
                logger.error(f"Error processing puzzle: {e}")
                continue
                
    print("\nDiscovery complete!")
    print("\nFinal patterns discovered:")
    show_patterns(learner)
    
def show_patterns(learner: PatternLearner):
    """Show discovered patterns."""
    patterns = learner.find_patterns(min_examples=3, min_success=0.5)
    
    if not patterns:
        print("No significant patterns found yet")
        return
        
    print(f"\nFound {len(patterns)} significant patterns:")
    for i, pattern in enumerate(patterns, 1):
        print(f"\nPattern {i}:")
        print(f"Seen in {pattern['examples']} positions")
        print(f"Success rate: {pattern['success_rate']*100:.1f}%")
        print(f"Average material gain: {pattern['avg_gain']:.1f}")
        print("\nFeatures:")
        print(describe_pattern(pattern))

def main():
    parser = argparse.ArgumentParser(description="Discover chess patterns")
    parser.add_argument("--puzzle-file", default="db/lichess_db_puzzle.csv",
                      help="Path to Lichess puzzle database CSV")
    parser.add_argument("--num-puzzles", type=int,
                      help="Number of puzzles to process (default: all)")
    parser.add_argument("--debug", action="store_true",
                      help="Enable debug logging")
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        
    process_puzzles(args.puzzle_file, args.num_puzzles)

if __name__ == "__main__":
    main()
