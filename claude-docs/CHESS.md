# Chess Pattern Discovery System

## Goal
Build a system that can discover chess tactical patterns (like pins, forks, etc.) from examples, rather than having these patterns pre-programmed. This follows the spirit of Eurisko - discovering concepts rather than being given them.

## Current Implementation

### Core Components
1. `tactical_patterns.py` - Pattern detection and analysis
   - `PatternFinder` - Analyzes positions for tactical patterns
   - `TacticalPattern` - Represents a discovered pattern
   - Geometric analysis tools (alignments, piece relationships)

2. `discover_tactics.py` - Main pattern discovery pipeline
   - Processes chess puzzles
   - Extracts patterns
   - Groups similar patterns
   - Calculates success metrics

### How It Works

1. Pattern Detection:
```python
def find_key_pieces(board: chess.Board, move: chess.Move):
    """Find key pieces involved in a tactical pattern."""
    key_pieces = []
    # Get moved piece
    moved_piece = board.piece_at(move.from_square)
    key_pieces.append((moved_piece.piece_type, move.from_square))
    
    # Get captured piece if any
    captured = board.piece_at(move.to_square)
    if captured:
        key_pieces.append((captured.piece_type, move.to_square))
        
    # Find newly attacked valuable pieces
    board_copy = board.copy()
    board_copy.push(move)
    attacks = board_copy.attacks(move.to_square)
    ...
```

2. Relationship Analysis:
```python
def analyze_relationships(board: chess.Board, key_pieces):
    """Analyze how pieces relate to each other."""
    relationships = []
    for piece1, sq1 in key_pieces:
        for piece2, sq2 in key_pieces:
            if is_aligned(sq1, sq2):
                # Check what's between them
                between = get_squares_between(sq1, sq2)
                if not any(between):
                    relationships.append("direct_attack")
                elif len(between) == 1:
                    relationships.append("attack_through_piece")
```

3. Pattern Learning:
- Groups similar positions based on:
  - Piece relationships (alignments, attacks)
  - Material gains
  - Common themes from puzzles

### Current Issues

1. Pattern Clarity
   - The system finds patterns but doesn't explain them clearly
   - Need better visualization of what makes each pattern work
   - Should show the "before" and "after" positions

2. Pattern Complexity
   - Currently looks at too many pieces at once
   - Should focus on minimal patterns (2-3 pieces)
   - Need to identify the essential pieces in each tactic

3. Lack of Validation
   - No systematic way to test if discovered patterns are meaningful
   - Need to validate against known chess concepts
   - Should verify patterns work in new positions

### Example Discoveries

Here's a pattern the system found:

```
Success rate: 100.0%
Typical material gain: 9.0 pawns
Common themes: endgame, hangingPiece, mate, mateIn1

Example position:
FEN: 4r1k1/1p2R1p1/p2p2Pp/P1pP4/5q2/1R3p2/1P1Q3P/5B1K b - - 0 34
Key move: f4d2
```

What makes this interesting:
1. Very high success rate (100%)
2. Large material gain (9 pawns = queen)
3. Leads to immediate mate
4. Multiple themes involved (hanging piece + mate threat)

But the system doesn't clearly show:
1. What's the key relationship between pieces?
2. Why does the pattern work?
3. Is this a known tactic or novel?

## Needed Improvements

1. Pattern Visualization
```python
def visualize_pattern(pattern: TacticalPattern):
    """Show a pattern with ASCII board."""
    board = """
    8 . . . . . . . .
    7 . . . . . . . .
    6 . . . B . . . .
    5 . . . . . . . .
    4 . . . . . . . .
    3 . . . . . . . .
    2 . . R . . . . .
    1 . . . . . . . .
      a b c d e f g h
    """
    # Highlight key pieces and relationships
    # Show movement arrows
    # Indicate attacks
```

2. Pattern Analysis
```python
def analyze_pattern(pattern: TacticalPattern):
    """Explain why a pattern works."""
    # Identify key tactical elements
    # Compare to known patterns
    # Show material imbalances
    # Explain winning idea
```

3. Minimal Pattern Detection
```python
def find_minimal_pattern(board: chess.Board, move: chess.Move):
    """Find smallest set of pieces that make pattern work."""
    # Start with moved piece
    # Add one piece at a time
    # Test if pattern still works
    # Return minimal set
```

## Next Steps

1. Implement pattern visualization
   - ASCII board display
   - Highlight key pieces
   - Show moves and relationships

2. Add pattern explanation
   - Describe key tactical elements
   - Compare to known patterns
   - Explain why it works

3. Focus on minimal patterns
   - Look at 2-piece patterns first
   - Build up to more complex ones
   - Find essential pieces

4. Improve validation
   - Test against known tactics
   - Verify in new positions
   - Compare with engine analysis

The goal is to build a system that can learn chess concepts from scratch, similar to how Eurisko discovered concepts in other domains. The current implementation shows this is possible but needs better ways to explain and validate its discoveries.
