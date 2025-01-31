"""Main script for running the chess discovery system."""
import chess
import logging
from typing import Optional, Dict, List
import argparse
import os
import csv
import json
from collections import defaultdict
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
        self.themes_by_puzzle = defaultdict(list)

    def extract_puzzle(self, line: str):
        """Extract board and solution from a puzzle line."""
        xs = line.split(',')
        puzzle_id = xs[self.header_idx['PuzzleId']]
        fen = xs[self.header_idx['FEN']]
        board = chess.Board(fen)
        solution_moves = xs[self.header_idx['Moves']].split(' ')
        themes = xs[self.header_idx['Themes']].strip('"').split(' ')
        self.themes_by_puzzle[puzzle_id] = themes
        return puzzle_id, board, solution_moves, themes

def print_status(system: ChessDiscoverySystem, stats_by_theme: Dict):
    """Print current status of the discovery system."""
    print("\nDiscovered Patterns:")
    pattern_stats = system.get_pattern_statistics()
    
    if not pattern_stats:
        print("No patterns discovered yet")
    else:
        for name, stats in pattern_stats.items():
            print(f"\n{name}:")
            print(f"  Success rate: {stats['success_rate']*100:.1f}%")
            print(f"  Average material gain: {stats['average_gain']:.1f}")
            print(f"  Total applications: {stats['total_applications']}")
            print(f"  Examples collected: {stats['examples_count']}")
            print(f"  Associated themes: {', '.join(stats['themes'])}")

    print("\nPattern Success by Puzzle Theme:")
    for theme, stats in stats_by_theme.items():
        if stats['total'] > 0:
            success_rate = (stats['discovered'] / stats['total']) * 100
            print(f"{theme}: {success_rate:.1f}% led to discoveries ({stats['discovered']}/{stats['total']})")

def save_discovered_patterns(system: ChessDiscoverySystem, output_dir: str):
    """Save discovered patterns to files."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Save pattern statistics
    stats_file = os.path.join(output_dir, "pattern_statistics.json")
    with open(stats_file, 'w') as f:
        json.dump(system.get_pattern_statistics(), f, indent=2)
        
    # Save example positions for each pattern
    examples_file = os.path.join(output_dir, "pattern_examples.csv")
    with open(examples_file, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(["Pattern", "FEN", "Move", "Themes", "Material_Change"])
        for name, motif in system.motifs.items():
            for example in motif.get_slot("examples").value:
                writer.writerow([
                    name,
                    example.get('position', ''),
                    example.get('move', ''),
                    ','.join(example.get('themes', [])),
                    example.get('material_change', 0)
                ])

def run_discovery(puzzle_file: str, output_dir: str = "discovered_patterns",
                num_puzzles: Optional[int] = None):
    """Run the discovery system on puzzles."""
    system = ChessDiscoverySystem()
    extractor = PuzzleExtractor()
    
    # Track statistics
    stats_by_theme = defaultdict(lambda: {"discovered": 0, "total": 0})
    
    logger.info("Starting chess pattern discovery")
    
    # Process puzzles
    with open(puzzle_file) as f:
        next(f)  # Skip header
        puzzles_processed = 0
        
        for line in f:
            if num_puzzles and puzzles_processed >= num_puzzles:
                break
                
            try:
                puzzle_id, board, solution, themes = extractor.extract_puzzle(line.strip())
                
                # Update theme counts
                for theme in themes:
                    stats_by_theme[theme]["total"] += 1
                
                # Count patterns before
                patterns_before = len(system.motifs)
                
                # Learn from the puzzle
                system.learn_from_puzzle(board, solution, themes)
                
                # Check if new patterns were discovered
                patterns_after = len(system.motifs)
                if patterns_after > patterns_before:
                    for theme in themes:
                        stats_by_theme[theme]["discovered"] += 1
                
                puzzles_processed += 1
                
                if puzzles_processed % 100 == 0:
                    logger.info(f"Processed {puzzles_processed} puzzles")
                    print_status(system, stats_by_theme)
                    
            except Exception as e:
                logger.error(f"Error processing puzzle: {e}")
                continue
                
    logger.info("Discovery complete")
    print_status(system, stats_by_theme)
    
    # Save discovered patterns
    save_discovered_patterns(system, output_dir)
    
    return system

def main():
    parser = argparse.ArgumentParser(description="Run chess pattern discovery system")
    parser.add_argument("--puzzle-file", default="db/lichess_db_puzzle.csv",
                      help="Path to Lichess puzzle database CSV")
    parser.add_argument("--num-puzzles", type=int,
                      help="Number of puzzles to process (default: all)")
    parser.add_argument("--output-dir", default="discovered_patterns",
                      help="Directory to save discovered patterns")
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
