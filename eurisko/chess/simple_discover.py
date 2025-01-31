"""Simple chess pattern discovery."""
import chess
import logging
import argparse
from typing import Optional, Dict, List
from .move_analyzer import analyze_move, PatternCollector

logger = logging.getLogger(__name__)

def process_puzzle_file(filename: str, num_puzzles: Optional[int] = None):
    """Process puzzles to find common patterns."""
    collector = PatternCollector()
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
                themes = fields[7].strip('"').split()  # Themes are eighth field
                
                # Set up board and analyze moves
                board = chess.Board(fen)
                
                # Analyze first move (for now just focus on key tactical move)
                move = chess.Move.from_uci(moves[0])
                pattern = analyze_move(board, move)
                collector.add_pattern(pattern, themes)
                
                puzzles_processed += 1
                if puzzles_processed % 100 == 0:
                    print(f"Processed {puzzles_processed} puzzles")
                    show_current_findings(collector)
                    
            except Exception as e:
                logger.error(f"Error processing puzzle: {e}")
                continue
                
    print("\nDiscovery complete!")
    print("\nFinal findings:")
    show_current_findings(collector)
    
def show_current_findings(collector: PatternCollector):
    """Show what patterns have been found so far."""
    patterns = collector.find_common_patterns()
    if not patterns:
        print("No common patterns found yet")
        return
        
    print("\nCommon patterns found:")
    for pattern in patterns:
        print(f"\nPattern using {pattern['piece']}:")
        print(f"  Captures: {pattern['captures']}")
        print(f"  Creates new attacks: {pattern['attacks']}")
        print(f"  Gives check: {pattern['gives_check']}")
        print(f"  Seen {pattern['count']} times")
        print(f"  Average material gain: {pattern['avg_gain']:.1f}")
        print(f"  Common themes: {', '.join(pattern['themes'])}")

def main():
    parser = argparse.ArgumentParser(description="Simple chess pattern discovery")
    parser.add_argument("--puzzle-file", default="db/lichess_db_puzzle.csv",
                      help="Path to Lichess puzzle database CSV")
    parser.add_argument("--num-puzzles", type=int,
                      help="Number of puzzles to process (default: all)")
    parser.add_argument("--debug", action="store_true",
                      help="Enable debug logging")
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        
    process_puzzle_file(args.puzzle_file, args.num_puzzles)

if __name__ == "__main__":
    main()
