"""Main script for running the chess discovery system."""
import chess
import logging
from typing import Optional
import argparse
import os
from .discovery import ChessDiscoverySystem
import json

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
        puzzle_id = xs[self.header_idx['PuzzleId']]
        fen = xs[self.header_idx['FEN']]
        board = chess.Board(fen)
        solution_moves = xs[self.header_idx['Moves']].split(' ')
        themes = xs[self.header_idx['Themes']].strip('"').split(' ')
        return puzzle_id, board, solution_moves, themes

def print_discovered_concepts(system: ChessDiscoverySystem):
    """Print the discovered chess concepts."""
    concepts = system.discover_concepts()
    
    print("\nDiscovered Chess Concepts:")
    for i, concept in enumerate(concepts, 1):
        print(f"\nConcept {i}: {concept['name']}")
        print(f"Based on {concept['patterns']} related patterns")
        print(f"Success rate: {concept['success_rate']*100:.1f}%")
        print(f"Average material gain: {concept['avg_gain']:.1f}")
        print("\nCore Features:")
        for feature, value in concept['core_features'].items():
            if isinstance(value, set):
                value = list(value)
            print(f"  {feature}: {value}")

def print_novel_patterns(system: ChessDiscoverySystem):
    """Print novel patterns that don't match common chess concepts."""
    novel = system.find_novel_patterns()
    
    print("\nNovel Patterns Discovered:")
    for i, pattern in enumerate(novel, 1):
        print(f"\nPattern {i}:")
        print(f"Pieces: {' -> '.join(pattern['pieces'])}")
        print(f"Relationship: {pattern['relationship']}")
        print(f"Success rate: {pattern['success_rate']*100:.1f}%")
        print(f"Average material gain: {pattern['avg_gain']:.1f}")
        if pattern['examples']:
            print("\nExample position:")
            ex = pattern['examples'][0]
            print(f"FEN: {ex['board'].fen()}")
            print(f"Moves: {' '.join(m.uci() for m in ex['moves'])}")
            print(f"Material gain: {ex['material_gain']}")

def save_discoveries(system: ChessDiscoverySystem, output_dir: str):
    """Save discovered concepts and patterns to files."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Save concepts
    concepts_file = os.path.join(output_dir, "discovered_concepts.json")
    with open(concepts_file, 'w') as f:
        json.dump(system.discover_concepts(), f, indent=2, default=str)
        
    # Save novel patterns
    patterns_file = os.path.join(output_dir, "novel_patterns.json")
    with open(patterns_file, 'w') as f:
        # Convert chess objects to strings for JSON
        novel = []
        for pattern in system.find_novel_patterns():
            pattern = pattern.copy()
            examples = []
            for ex in pattern['examples']:
                examples.append({
                    'fen': ex['board'].fen(),
                    'moves': [m.uci() for m in ex['moves']],
                    'material_gain': ex['material_gain']
                })
            pattern['examples'] = examples
            novel.append(pattern)
        json.dump(novel, f, indent=2)

def run_discovery(puzzle_file: str, output_dir: str = "chess_discoveries",
                num_puzzles: Optional[int] = None):
    """Run the discovery system on puzzles."""
    system = ChessDiscoverySystem()
    extractor = PuzzleExtractor()
    
    logger.info("Starting pattern discovery")
    
    # Process puzzles
    with open(puzzle_file) as f:
        next(f)  # Skip header
        puzzles_processed = 0
        
        for line in f:
            if num_puzzles and puzzles_processed >= num_puzzles:
                break
                
            try:
                puzzle_id, board, solution, themes = extractor.extract_puzzle(line.strip())
                
                # Learn from the puzzle
                system.learn_from_puzzle(board, solution)
                
                puzzles_processed += 1
                if puzzles_processed % 100 == 0:
                    logger.info(f"Processed {puzzles_processed} puzzles")
                    # Show intermediate discoveries
                    print_discovered_concepts(system)
                    print_novel_patterns(system)
                    
            except Exception as e:
                logger.error(f"Error processing puzzle: {e}")
                continue
                
    logger.info("Discovery complete")
    
    # Show final discoveries
    print_discovered_concepts(system)
    print_novel_patterns(system)
    
    # Save discoveries
    save_discoveries(system, output_dir)
    logger.info(f"Saved discoveries to {output_dir}")
    
    return system

def main():
    parser = argparse.ArgumentParser(description="Run chess pattern discovery")
    parser.add_argument("--puzzle-file", default="db/lichess_db_puzzle.csv",
                      help="Path to Lichess puzzle database CSV")
    parser.add_argument("--num-puzzles", type=int,
                      help="Number of puzzles to process (default: all)")
    parser.add_argument("--output-dir", default="chess_discoveries",
                      help="Directory to save discoveries")
    parser.add_argument("--debug", action="store_true",
                      help="Enable debug logging")
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        
    if not os.path.exists(args.puzzle_file):
        print(f"Error: Puzzle file '{args.puzzle_file}' not found")
        print("Please run download_db.sh from the ai-chess-puzzles directory first")
        return
        
    system = run_discovery(
        args.puzzle_file, 
        args.output_dir,
        args.num_puzzles
    )

if __name__ == "__main__":
    main()
