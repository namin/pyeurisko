"""Chess tactical motifs and their detection."""
import chess
from typing import Dict, List, Any, Optional, Tuple
from ..neo import Unit, SlotType

class ChessMotif(Unit):
    """A chess tactical pattern like pin, fork, etc."""
    def __init__(self, name: str):
        super().__init__(name)
        self.add_slot("pattern_type", "", SlotType.TEXT)  # e.g., "pin", "fork"
        self.add_slot("pieces_involved", [], SlotType.LIST)  # e.g., ["bishop", "queen"]
        self.add_slot("target_pieces", [], SlotType.LIST)  
        self.add_slot("detection_function", None, SlotType.CODE)
        self.add_slot("worth", 500, SlotType.UNIT)
        self.add_slot("examples", [], SlotType.LIST)  # FEN positions showing this motif
        self.add_slot("is_a", ["ChessMotif"], SlotType.LIST)
        # Initialize performance tracking
        self.add_slot("performance", {
            "applications": 0,
            "successes": 0,
            "failures": 0,
            "worth_generated": 0
        }, SlotType.LIST)
        
    def detect(self, board: chess.Board) -> Dict[str, Any]:
        """Apply this motif's detection function to a board position."""
        detection_fn = self.get_slot("detection_function").value
        if detection_fn:
            return detection_fn(board)
        return {"type": self.get_slot("pattern_type").value, "instances": []}

def detect_pin(board: chess.Board) -> Dict[str, Any]:
    """Detect if there's a pin on the board."""
    pins = []
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is None or piece.color != board.turn:
            continue
            
        # Look for pinned pieces
        if board.is_pinned(board.turn, square):
            pinner = None
            # Find the pinning piece
            for attacker in board.attackers(not board.turn, square):
                if board.is_pinned(board.turn, square):
                    pinner = attacker
                    break
                    
            pins.append({
                "pinned_square": square,
                "pinned_piece": piece,
                "pinner_square": pinner,
                "pinner_piece": board.piece_at(pinner)
            })
            
    return {"type": "pin", "instances": pins}

def detect_fork(board: chess.Board) -> Dict[str, Any]:
    """Detect if there's a fork on the board."""
    forks = []
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is None or piece.color != board.turn:
            continue
            
        # Get all squares attacked by this piece
        attacks = list(board.attacks(square))
        if len(attacks) < 2:
            continue
            
        # Look for valuable pieces being attacked
        valuable_targets = []
        for attack in attacks:
            target = board.piece_at(attack)
            if target and target.color != board.turn:
                if target.piece_type in [chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT]:
                    valuable_targets.append((attack, target))
                    
        if len(valuable_targets) >= 2:
            forks.append({
                "forking_square": square,
                "forking_piece": piece,
                "targets": valuable_targets
            })
            
    return {"type": "fork", "instances": forks}

def create_basic_motifs() -> List[ChessMotif]:
    """Create the basic tactical motifs we start with."""
    motifs = []
    
    # Pin motif
    pin = ChessMotif("pin")
    pin.add_slot("pattern_type", "pin", SlotType.TEXT)
    pin.add_slot("detection_function", detect_pin, SlotType.CODE)
    motifs.append(pin)
    
    # Fork motif
    fork = ChessMotif("fork")
    fork.add_slot("pattern_type", "fork", SlotType.TEXT)
    fork.add_slot("detection_function", detect_fork, SlotType.CODE)
    motifs.append(fork)
    
    return motifs
