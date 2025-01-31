"""Discover meaningful chess tactical patterns with visualization."""
import chess
import logging
from typing import Optional, Dict, List, Tuple
import argparse
import os
import json
from .tactical_patterns import PatternFinder
from .pattern_viz import PatternSummary, find_common_elements, show_pattern, describe_pattern

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('chess_tactics')

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

def create_pattern_summary(examples: List[dict]) -> Tuple[PatternSummary, Tuple[chess.Board, chess.Move]]:
    """Create a pattern summary from example positions."""
    positions = []
    for example in examples:
        board = chess.Board(example['fen'])
        move = chess.Move.from_uci(example['move'])
        positions.append((board, move))

    # Use the first position as the example position
    example_position = positions[0] if positions else None
    
    # Find common elements across positions
    pattern_summary = find_common_elements(positions)
    
    # Add themes from examples
    themes = []
    for example in examples:
        themes.extend(example.get('themes', []))
    pattern_summary.themes = list(set(themes))
    
    return pattern_summary, example_position

def print_discovered_pattern(pattern, show_examples: bool = False):
    """Print a discovered tactical pattern with visualization."""
    print("\n" + "="*50)
    
    if pattern.examples:
        # Create pattern summary from examples
        pattern_summary, example_position = create_pattern_summary(pattern.examples)
        
        # Show visualization
        print("Pattern Visualization:")
        show_pattern(pattern_summary, example_position)
        
        # Print additional pattern information
        print(f"\nSuccess rate: {pattern.success_rate*100:.1f}%")
        print(f"Typical material gain: {pattern.material_gain:.1f} pawns")
        if pattern.common_themes:
            print(f"Common themes: {', '.join(pattern.common_themes)}")
            
        if show_examples and pattern.examples:
            print("\nAdditional examples:")
            for i, example in enumerate(pattern.examples[1:3], 1):  # Show 2 more examples
                print(f"\nExample {i}:")
                print(f"FEN: {example['fen']}")
                print(f"Key move: {example['move']}")
                print(f"Material gained: {example['material_gain']}")
                if example.get('themes'):
                    print(f"Themes: {', '.join(example['themes'])}")
    
    print("="*50)

def square_name(t):
    return "abcdefgh"[t[0]]+str(t[1])

def run_discovery(puzzle_file: str, num_puzzles: Optional[int] = None,
                output_dir: str = "discovered_tactics"):
    """Run tactical pattern discovery on puzzles with visualization."""
    finder = PatternFinder()
    extractor = PuzzleExtractor()
    
    logger.info("Starting tactical pattern discovery")
    
    # Process puzzles
    with open(puzzle_file) as f:
        next(f)  # Skip header
        puzzles_processed = 0
        
        for line in f:
            if num_puzzles and puzzles_processed >= num_puzzles:
                break
                
            try:
                puzzle_id, board, solution, themes = extractor.extract_puzzle(line.strip())
                
                # Look at first move (key tactical move)
                move = chess.Move.from_uci(solution[0])
                
                # Calculate material gain
                piece_captured = board.piece_at(move.to_square)
                material_gain = 0
                if piece_captured:
                    values = {
                        chess.PAWN: 1,
                        chess.KNIGHT: 3,
                        chess.BISHOP: 3,
                        chess.ROOK: 5,
                        chess.QUEEN: 9
                    }
                    material_gain = values.get(piece_captured.piece_type, 0)
                
                # Extract pattern
                finder.extract_pattern(board, move, material_gain, themes)
                
                puzzles_processed += 1
                if puzzles_processed % 100 == 0:
                    logger.info(f"Processed {puzzles_processed} puzzles")
                    patterns = finder.get_discovered_patterns()
                    print(f"\nFound {len(patterns)} tactical patterns so far:")
                    for pattern in patterns:
                        print_discovered_pattern(pattern)
                    
            except Exception as e:
                logger.error(f"Error processing puzzle: {e}")
                continue
                
    logger.info("Discovery complete")
    
    # Show final patterns
    patterns = finder.get_discovered_patterns()
    print(f"\nDiscovered {len(patterns)} significant tactical patterns:")
    for pattern in patterns:
        print_discovered_pattern(pattern, show_examples=True)
        
    # Save patterns
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        patterns_file = os.path.join(output_dir, "tactical_patterns.json")
        
        # Convert patterns to JSON-serializable format
        pattern_data = []
        for pattern in patterns:
            data = {
                'pieces': [chess.piece_name(p[0]) for p in pattern.key_pieces],
                'relationships': pattern.relationships,
                'success_rate': pattern.success_rate,
                'material_gain': pattern.material_gain,
                'common_themes': pattern.common_themes,
                'examples': pattern.examples,
                'visualization': {
                    'board_ascii': None,  # Will be filled in when loaded
                    'key_squares': [square_name(sq) for sq in pattern.key_pieces],
                    'arrows': []  # Will be filled in when loaded
                }
            }
            
            # Add visualization data from example
            if pattern.examples:
                pattern_summary, example_position = create_pattern_summary(pattern.examples)
                board, move = example_position
                data['visualization']['board_ascii'] = board.fen()
                data['visualization']['arrows'].append(
                    [chess.square_name(move.from_square),
                     chess.square_name(move.to_square)]
                )
            
            pattern_data.append(data)
            
        with open(patterns_file, 'w') as f:
            json.dump(pattern_data, f, indent=2)
            
        logger.info(f"Saved patterns to {patterns_file}")

def main():
    parser = argparse.ArgumentParser(description="Discover chess tactical patterns")
    parser.add_argument("--puzzle-file", default="db/lichess_db_puzzle.csv",
                      help="Path to Lichess puzzle database CSV")
    parser.add_argument("--num-puzzles", type=int,
                      help="Number of puzzles to process (default: all)")
    parser.add_argument("--output-dir", default="discovered_tactics",
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
        
    run_discovery(args.puzzle_file, args.num_puzzles, args.output_dir)

if __name__ == "__main__":
    main()
