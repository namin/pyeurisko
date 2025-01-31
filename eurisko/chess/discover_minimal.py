"""Discover minimal chess patterns."""
import chess
import logging
from typing import Optional
import argparse
from .minimal_patterns import MinimalPatternLearner
import json

logger = logging.getLogger(__name__)

def process_puzzles(filename: str, num_puzzles: Optional[int] = None):
    """Process puzzles to discover minimal patterns."""
    learner = MinimalPatternLearner()
    puzzles_processed = 0
    
    print("Starting minimal pattern discovery...")
    
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
                themes = fields[7].strip('"').split()  # Themes are eighth field
                
                # Set up board
                board = chess.Board(fen)
                
                # Look at first move (key tactical move)
                move_uci = moves[0]
                move = chess.Move.from_uci(move_uci)
                
                # Calculate material gain
                material_gained = 0
                target_piece = board.piece_at(move.to_square)
                if target_piece:
                    piece_values = {
                        chess.PAWN: 1,
                        chess.KNIGHT: 3,
                        chess.BISHOP: 3,
                        chess.ROOK: 5,
                        chess.QUEEN: 9
                    }
                    material_gained = piece_values.get(target_piece.piece_type, 0)
                
                # Learn from position
                learner.learn_from_position(board, move, material_gained)
                
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
    
    # Save discovered patterns
    save_patterns(learner, "discovered_minimal_patterns.json")
    
def show_patterns(learner: MinimalPatternLearner):
    """Show discovered patterns."""
    patterns = learner.get_discovered_patterns()
    
    if not patterns:
        print("No significant patterns found yet")
        return
        
    print(f"\nFound {len(patterns)} minimal patterns:")
    for i, pattern in enumerate(patterns, 1):
        print(f"\nPattern {i}:")
        print(f"Pieces: {' -> '.join(pattern['pieces'])}")
        print(f"Relationship: {pattern['relationship']}")
        if pattern['relative_value'] > 0:
            print(f"Target more valuable by: {pattern['relative_value']} points")
        print(f"Seen {pattern['count']} times")
        print(f"Success rate: {pattern['success_rate']*100:.1f}%")
        print(f"Average material gain: {pattern['avg_gain']:.1f}")
        print("\nExample positions:")
        for ex in pattern['examples']:
            print(f"  FEN: {ex['fen']}")
            print(f"  Move: {ex['move']}")
            print(f"  Gain: {ex['gain']}")
            print()

def save_patterns(learner: MinimalPatternLearner, filename: str):
    """Save discovered patterns to file."""
    patterns = learner.get_discovered_patterns()
    with open(filename, 'w') as f:
        json.dump(patterns, f, indent=2)
    print(f"\nSaved patterns to {filename}")

def main():
    parser = argparse.ArgumentParser(description="Discover minimal chess patterns")
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
