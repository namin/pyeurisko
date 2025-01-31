"""Main script for running the chess discovery system."""
import chess
import logging
from typing import Optional
import argparse
import os
from .discovery import ChessDiscoverySystem

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('chess_discovery')

class PuzzleExtractor:
    """Extract puzzles from Lichess database."""
    HEADERS = ['PuzzleId', 'FEN', 'Moves', 'Rating', 'RatingDeviation', 
               'Popularity', 'NbPlays', 'Themes', 'GameUrl', 'OpeningTags']
    
    def __init__(self):
        self.header_idx = dict([(self.HEADERS[i], i) for i in range(len(self.HEADERS))])

    def extract_puzzle(self, line: str):
        """Extract board and solution from a puzzle line."""
        xs = line.split(',')
        fen = xs[self.header_idx['FEN']]
        board = chess.Board(fen)
        solution_moves = xs[self.header_idx['Moves']].split(' ')
        themes = xs[self.header_idx['Themes']].strip('"').split(' ')
        return board, solution_moves, themes

def print_status(system: ChessDiscoverySystem):
    """Print current status of the discovery system."""
    print("\nCurrent Motifs:")
    for name, motif in system.motifs.items():
        perf = motif.get_slot("performance").value
        if perf["applications"] > 0:
            success_rate = (perf["successes"] / perf["applications"]) * 100
            print(f"{name}: {perf['applications']} applications, "
                  f"{success_rate:.1f}% success rate")
            
    print("\nActive Heuristics:")
    for name, unit in system.units.items():
        if "PatternDiscovery" in unit.get_slot("is_a").value:
            worth = unit.worth
            print(f"{name}: worth = {worth}")

def run_discovery(puzzle_file: str, num_puzzles: Optional[int] = None):
    """Run the discovery system on puzzles."""
    system = ChessDiscoverySystem()
    extractor = PuzzleExtractor()
    
    logger.info("Starting chess pattern discovery")
    
    # Process puzzles
    with open(puzzle_file) as f:
        next(f)  # Skip header
        puzzles_processed = 0
        
        for line in f:
            if num_puzzles and puzzles_processed >= num_puzzles:
                break
                
            try:
                board, solution, themes = extractor.extract_puzzle(line.strip())
                system.learn_from_puzzle(board, solution)
                puzzles_processed += 1
                
                if puzzles_processed % 100 == 0:
                    logger.info(f"Processed {puzzles_processed} puzzles")
                    print_status(system)
                    
            except Exception as e:
                logger.error(f"Error processing puzzle: {e}")
                continue
                
    logger.info("Discovery complete")
    print_status(system)
    return system

def main():
    parser = argparse.ArgumentParser(description="Run chess pattern discovery system")
    parser.add_argument("--puzzle-file", default="db/lichess_db_puzzle.csv",
                      help="Path to Lichess puzzle database CSV")
    parser.add_argument("--num-puzzles", type=int,
                      help="Number of puzzles to process (default: all)")
    parser.add_argument("--debug", action="store_true",
                      help="Enable debug logging")
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        
    if not os.path.exists(args.puzzle_file):
        print(f"Error: Puzzle file '{args.puzzle_file}' not found")
        print("Please run download_db.sh from the ai-chess-puzzles directory first")
        return
        
    system = run_discovery(args.puzzle_file, args.num_puzzles)

if __name__ == "__main__":
    main()
