"""Analyze discovered chess patterns."""
import chess
from .pattern_viz import find_common_elements, show_pattern, PatternSummary
from typing import List, Dict

def analyze_discovered_pattern(pattern: Dict):
    """Analyze a pattern found by the system."""
    # Load example positions
    positions = []
    for example in pattern['examples']:
        board = chess.Board(example['fen'])
        move = chess.Move.from_uci(example['move'])
        positions.append((board, move))
        
    # Find common elements
    summary = find_common_elements(positions)
    
    # Show pattern with example
    print(f"Pattern with {pattern['success_rate']*100:.1f}% success rate")
    print(f"Material gain: {pattern['material_gain']} pawns")
    print(f"Common themes: {', '.join(pattern['common_themes'])}\n")
    
    show_pattern(summary, positions[0])
    
# Example usage:
if __name__ == "__main__":
    # Example pattern to analyze
    pattern = {
        'success_rate': 1.0,
        'material_gain': 9.0,
        'common_themes': ['endgame', 'mate', 'mateIn1'],
        'examples': [{
            'fen': '4r1k1/1p2R1p1/p2p2Hp/P1pP4/5q2/1R3p2/1P1Q3P/5B1K',
            'move': 'f4d2'
        }]
    }
    
    analyze_discovered_pattern(pattern)
