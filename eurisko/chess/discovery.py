"""Chess discovery system built on Neo-Eurisko."""
import chess
from typing import Dict, List, Any, Optional, Tuple
from ..neo import NeoEurisko, Unit, SlotType
from .motifs import ChessMotif, create_basic_motifs
from .heuristics import create_basic_heuristics
import logging

logger = logging.getLogger(__name__)

class ChessDiscoverySystem(NeoEurisko):
    """A system for discovering and evolving chess tactical patterns."""
    
    def __init__(self):
        super().__init__()
        self.motifs: Dict[str, ChessMotif] = {}
        self.initialize_system()
        
    def initialize_system(self):
        """Initialize the system with basic motifs and heuristics."""
        # Add basic motifs
        for motif in create_basic_motifs():
            self.motifs[motif.name] = motif
            self.units[motif.name] = motif
            
        # Add basic heuristics
        for heuristic in create_basic_heuristics(self):
            self.units[heuristic.name] = heuristic
            
    def analyze_position(self, board: chess.Board) -> List[Dict[str, Any]]:
        """Apply all known motif detection heuristics to a position."""
        findings = []
        for motif in self.motifs.values():
            try:
                result = motif.detect(board)
                if result["instances"]:
                    findings.append(result)
            except Exception as e:
                logger.error(f"Error detecting motif {motif.name}: {e}")
        return findings
        
    def learn_from_puzzle(self, board: chess.Board, solution: List[str]):
        """Learn from a puzzle by analyzing the positions."""
        try:
            # Analyze initial position
            initial_patterns = self.analyze_position(board)
            
            # Make the solution moves and analyze resulting positions
            board_copy = board.copy()
            for move in solution:
                board_copy.push_uci(move)
                patterns = self.analyze_position(board_copy)
                
                # Create a target unit for the pattern discovery
                analysis_target = Unit("pattern-analysis")
                analysis_target.add_slot("before_patterns", initial_patterns, SlotType.LIST)
                analysis_target.add_slot("after_patterns", patterns, SlotType.LIST)
                analysis_target.add_slot("move", move, SlotType.TEXT)
                analysis_target.add_slot("is_a", ["PatternAnalysis"], SlotType.LIST)
                
                # Look for new or refined patterns
                self.discover_new_patterns(analysis_target)
                
                # Also try to refine existing motifs
                for motif in self.motifs.values():
                    self.refine_motif(motif)
                
                # Update statistics for the motifs
                self.update_motif_stats(initial_patterns, patterns, True)
                
        except Exception as e:
            logger.error(f"Error learning from puzzle: {e}")
            
    def discover_new_patterns(self, target: Unit):
        """Try to discover new tactical patterns or refine existing ones."""
        # Apply pattern discovery heuristics
        for heuristic in self.units.values():
            if "PatternDiscovery" in heuristic.get_slot("is_a").value:
                try:
                    self.apply_heuristic(heuristic, target)
                except Exception as e:
                    logger.error(f"Error applying {heuristic.name}: {e}")
                
    def refine_motif(self, motif: ChessMotif):
        """Attempt to refine an existing motif."""
        # Apply specialization heuristics directly to motifs
        for heuristic in self.units.values():
            if "PatternDiscovery" in heuristic.get_slot("is_a").value:
                try:
                    self.apply_heuristic(heuristic, motif)
                except Exception as e:
                    logger.error(f"Error refining motif {motif.name} with {heuristic.name}: {e}")

    def update_motif_stats(self, before_patterns: List[Dict], 
                          after_patterns: List[Dict],
                          successful: bool):
        """Update success statistics for motifs."""
        for pattern in before_patterns:
            motif = self.motifs.get(pattern["type"])
            if motif:
                perf = motif.get_slot("performance").value
                if perf:  # Safety check
                    perf["applications"] += 1
                    if successful:
                        perf["successes"] += 1
                    else:
                        perf["failures"] += 1
