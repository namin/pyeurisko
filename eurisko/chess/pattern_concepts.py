"""Higher-level chess concepts discovered from basic patterns."""
import chess
from dataclasses import dataclass
from typing import List, Dict, Set, Optional
from collections import defaultdict

@dataclass
class ChessConcept:
    """A higher-level chess concept discovered from patterns."""
    name: str
    patterns: List[Dict]  # List of related patterns
    core_features: Dict  # What makes these patterns similar
    success_rate: float
    avg_material_gain: float
    example_sequences: List[List[chess.Move]]  # Move sequences demonstrating this concept

class ConceptDiscoverer:
    """Discovers higher-level chess concepts from patterns."""
    
    def __init__(self):
        self.concepts = []
        self.pattern_sequences = defaultdict(list)  # Track sequences for each pattern
        
    def add_pattern_sequence(self, pattern_key: str, moves: List[chess.Move], 
                           material_gain: float):
        """Add a sequence of moves that demonstrate a pattern."""
        if material_gain > 0:  # Only track successful sequences
            self.pattern_sequences[pattern_key].append({
                'moves': moves,
                'gain': material_gain
            })
            
    def find_similar_patterns(self, patterns: List[Dict]) -> List[List[Dict]]:
        """Group similar patterns together based on their features."""
        groups = []
        used_patterns = set()
        
        for i, pattern1 in enumerate(patterns):
            if i in used_patterns:
                continue
                
            # Start a new group
            group = [pattern1]
            used_patterns.add(i)
            
            # Look for similar patterns
            for j, pattern2 in enumerate(patterns):
                if j in used_patterns:
                    continue
                    
                if self.are_patterns_similar(pattern1, pattern2):
                    group.append(pattern2)
                    used_patterns.add(j)
                    
            if len(group) > 1:  # Only keep groups of related patterns
                groups.append(group)
                
        return groups
        
    def are_patterns_similar(self, pattern1: Dict, pattern2: Dict) -> bool:
        """Check if two patterns are similar enough to be part of same concept."""
        # Patterns are similar if they share:
        # 1. Similar piece relationships
        # 2. Similar material gains
        # 3. Similar success rates
        
        def get_key_pieces(pattern):
            return set(p for p in pattern['pieces'] if p in 
                      ['queen', 'rook', 'bishop', 'knight'])
                      
        def get_relationship_type(pattern):
            return pattern['relationship'].split('_')[0]  # Remove _through suffix
            
        # Check if patterns involve same piece types
        if len(get_key_pieces(pattern1) & get_key_pieces(pattern2)) < 1:
            return False
            
        # Check if relationships are similar
        if get_relationship_type(pattern1) != get_relationship_type(pattern2):
            return False
            
        # Check if success metrics are similar
        if abs(pattern1['success_rate'] - pattern2['success_rate']) > 0.2:
            return False
            
        if abs(pattern1['avg_gain'] - pattern2['avg_gain']) > 1.5:
            return False
            
        return True
        
    def extract_core_features(self, patterns: List[Dict]) -> Dict:
        """Extract common features that define a group of patterns."""
        features = {
            'piece_types': set(),
            'relationships': set(),
            'success_rate': 0.0,
            'avg_gain': 0.0,
            'move_types': set()
        }
        
        # Collect all features
        for pattern in patterns:
            features['piece_types'].update(pattern['pieces'])
            features['relationships'].add(pattern['relationship'])
            features['success_rate'] += pattern['success_rate']
            features['avg_gain'] += pattern['avg_gain']
            
            # Analyze move types from sequences
            for seq in self.pattern_sequences[pattern['name']]:
                for move in seq['moves']:
                    features['move_types'].add(self.classify_move_type(move))
                    
        # Average the metrics
        features['success_rate'] /= len(patterns)
        features['avg_gain'] /= len(patterns)
        
        return features
        
    def classify_move_type(self, move: chess.Move) -> str:
        """Classify the type of chess move."""
        # TODO: Add more move classifications
        if move.promotion:
            return "promotion"
        elif move.is_capture:
            return "capture"
        elif move.is_check:
            return "check"
        else:
            return "quiet"
            
    def name_concept(self, core_features: Dict) -> str:
        """Generate a name for a chess concept based on its features."""
        # Start with piece types involved
        key_pieces = [p for p in core_features['piece_types'] 
                     if p in ['queen', 'rook', 'bishop', 'knight']]
        piece_str = '_'.join(sorted(key_pieces))
        
        # Add primary relationship
        rel = list(core_features['relationships'])[0]
        
        # Add primary move type
        move_types = sorted(core_features['move_types'])
        move_str = move_types[0] if move_types else "position"
        
        return f"{piece_str}_{rel}_{move_str}"
        
    def discover_concepts(self, patterns: List[Dict]) -> List[ChessConcept]:
        """Discover higher-level chess concepts from patterns."""
        # First group similar patterns
        pattern_groups = self.find_similar_patterns(patterns)
        
        # Create concepts from groups
        for group in pattern_groups:
            # Extract common features
            features = self.extract_core_features(group)
            
            # Generate name
            name = self.name_concept(features)
            
            # Collect example sequences
            sequences = []
            for pattern in group:
                sequences.extend(
                    seq['moves'] for seq in self.pattern_sequences[pattern['name']]
                )
            
            # Create concept
            concept = ChessConcept(
                name=name,
                patterns=group,
                core_features=features,
                success_rate=features['success_rate'],
                avg_material_gain=features['avg_gain'],
                example_sequences=sequences[:5]  # Keep top 5 examples
            )
            
            self.concepts.append(concept)
            
        return self.concepts

    def get_novel_patterns(self, min_success_rate: float = 0.6) -> List[Dict]:
        """Find patterns that don't match common chess concepts."""
        novel = []
        
        # Define common chess concepts
        common_concepts = {
            "fork": {"pieces": {"knight"}, "relationship": "knight_move"},
            "pin": {"pieces": {"bishop", "rook", "queen"}, "relationship": "diagonal"},
            "skewer": {"pieces": {"bishop", "rook", "queen"}, "relationship": "diagonal"},
            "discovered_attack": {"pieces": {"knight", "bishop"}, "relationship": "through"}
        }
        
        # Look through all patterns
        for pattern in self.patterns:
            if pattern['success_rate'] < min_success_rate:
                continue
                
            # Check if pattern matches any common concept
            is_common = False
            for concept in common_concepts.values():
                if (concept['pieces'] & set(pattern['pieces']) and
                    concept['relationship'] in pattern['relationship']):
                    is_common = True
                    break
                    
            if not is_common:
                novel.append(pattern)
                
        return novel
