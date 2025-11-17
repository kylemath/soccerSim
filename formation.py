"""
Formation system with fuzzy boundaries and evolution
"""

import numpy as np
from config import *


class Formation:
    """Formation configuration for 7x7 team"""
    def __init__(self, name="Custom", positions=None):
        self.name = name
        
        if positions is None:
            # Default 2-3-1 formation (2 defenders, 3 midfielders, 1 forward)
            positions = self._create_default_formation()
        
        self.positions = positions  # List of (x, y) tuples relative to field
    
    def _create_default_formation(self):
        """Create default 2-3-1 formation"""
        # Normalized positions (0-1 scale)
        # Then convert to field coordinates
        positions = []
        
        # Goalkeeper (always at goal)
        positions.append((FIELD_WIDTH / 2, 2.0 if np.random.random() < 0.5 else FIELD_LENGTH - 2.0))
        
        # 2 Defenders
        positions.append((FIELD_WIDTH * 0.3, FIELD_LENGTH * 0.25))
        positions.append((FIELD_WIDTH * 0.7, FIELD_LENGTH * 0.25))
        
        # 3 Midfielders
        positions.append((FIELD_WIDTH * 0.2, FIELD_LENGTH * 0.5))
        positions.append((FIELD_WIDTH * 0.5, FIELD_LENGTH * 0.5))
        positions.append((FIELD_WIDTH * 0.8, FIELD_LENGTH * 0.5))
        
        # 1 Forward
        positions.append((FIELD_WIDTH / 2, FIELD_LENGTH * 0.75))
        
        return positions
    
    def apply_to_team(self, team, is_home=True):
        """Apply formation to team players"""
        # Flip formation if away team (mirror across center line)
        for i, player in enumerate(team.players):
            if i < len(self.positions):
                x, y = self.positions[i]
                # Flip y coordinate for away team: mirror around center line
                if not is_home:
                    y = FIELD_LENGTH - y
                player.set_formation_position(x, y)
    
    def mutate(self, mutation_rate=MUTATION_RATE):
        """Mutate formation by randomly adjusting positions"""
        mutated = Formation(name=f"{self.name}_mutated")
        mutated.positions = []
        
        for x, y in self.positions:
            if np.random.random() < mutation_rate:
                # Mutate position
                new_x = x + np.random.normal(0, FIELD_WIDTH * 0.1)
                new_y = y + np.random.normal(0, FIELD_LENGTH * 0.1)
                
                # Keep within bounds
                new_x = max(PLAYER_RADIUS, min(FIELD_WIDTH - PLAYER_RADIUS, new_x))
                new_y = max(PLAYER_RADIUS, min(FIELD_LENGTH - PLAYER_RADIUS, new_y))
                
                mutated.positions.append((new_x, new_y))
            else:
                mutated.positions.append((x, y))
        
        return mutated
    
    def crossover(self, other):
        """Crossover with another formation"""
        child = Formation(name=f"{self.name}_x_{other.name}")
        child.positions = []
        
        for i in range(min(len(self.positions), len(other.positions))):
            if np.random.random() < 0.5:
                child.positions.append(self.positions[i])
            else:
                child.positions.append(other.positions[i])
        
        # Add remaining positions from longer formation
        if len(self.positions) > len(other.positions):
            child.positions.extend(self.positions[len(other.positions):])
        elif len(other.positions) > len(self.positions):
            child.positions.extend(other.positions[len(self.positions):])
        
        return child
    
    def to_dict(self):
        """Convert to dictionary for storage"""
        return {
            'name': self.name,
            'positions': self.positions
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create from dictionary"""
        formation = cls(name=data['name'], positions=data['positions'])
        return formation


class FormationLibrary:
    """Common formations for 7x7 soccer"""
    
    @staticmethod
    def get_formation(name):
        """Get a predefined formation"""
        formations = {
            '2-3-1': FormationLibrary._create_2_3_1(),
            '3-2-1': FormationLibrary._create_3_2_1(),
            '2-2-2': FormationLibrary._create_2_2_2(),
            '1-3-2': FormationLibrary._create_1_3_2(),
        }
        return formations.get(name, formations['2-3-1'])
    
    @staticmethod
    def _create_2_3_1():
        """2-3-1 formation"""
        positions = [
            (FIELD_WIDTH / 2, 2.0),  # GK
            (FIELD_WIDTH * 0.3, FIELD_LENGTH * 0.2),  # D1
            (FIELD_WIDTH * 0.7, FIELD_LENGTH * 0.2),  # D2
            (FIELD_WIDTH * 0.2, FIELD_LENGTH * 0.5),  # M1
            (FIELD_WIDTH * 0.5, FIELD_LENGTH * 0.5),  # M2
            (FIELD_WIDTH * 0.8, FIELD_LENGTH * 0.5),  # M3
            (FIELD_WIDTH / 2, FIELD_LENGTH * 0.75),   # F1
        ]
        return Formation("2-3-1", positions)
    
    @staticmethod
    def _create_3_2_1():
        """3-2-1 formation"""
        positions = [
            (FIELD_WIDTH / 2, 2.0),  # GK
            (FIELD_WIDTH * 0.25, FIELD_LENGTH * 0.2),  # D1
            (FIELD_WIDTH / 2, FIELD_LENGTH * 0.2),     # D2
            (FIELD_WIDTH * 0.75, FIELD_LENGTH * 0.2),  # D3
            (FIELD_WIDTH * 0.35, FIELD_LENGTH * 0.5),  # M1
            (FIELD_WIDTH * 0.65, FIELD_LENGTH * 0.5),  # M2
            (FIELD_WIDTH / 2, FIELD_LENGTH * 0.75),    # F1
        ]
        return Formation("3-2-1", positions)
    
    @staticmethod
    def _create_2_2_2():
        """2-2-2 formation"""
        positions = [
            (FIELD_WIDTH / 2, 2.0),  # GK
            (FIELD_WIDTH * 0.3, FIELD_LENGTH * 0.25),  # D1
            (FIELD_WIDTH * 0.7, FIELD_LENGTH * 0.25),  # D2
            (FIELD_WIDTH * 0.3, FIELD_LENGTH * 0.5),   # M1
            (FIELD_WIDTH * 0.7, FIELD_LENGTH * 0.5),   # M2
            (FIELD_WIDTH * 0.3, FIELD_LENGTH * 0.75),  # F1
            (FIELD_WIDTH * 0.7, FIELD_LENGTH * 0.75),  # F2
        ]
        return Formation("2-2-2", positions)
    
    @staticmethod
    def _create_1_3_2():
        """1-3-2 formation"""
        positions = [
            (FIELD_WIDTH / 2, 2.0),  # GK
            (FIELD_WIDTH / 2, FIELD_LENGTH * 0.2),     # D1
            (FIELD_WIDTH * 0.2, FIELD_LENGTH * 0.4),  # M1
            (FIELD_WIDTH / 2, FIELD_LENGTH * 0.4),    # M2
            (FIELD_WIDTH * 0.8, FIELD_LENGTH * 0.4),  # M3
            (FIELD_WIDTH * 0.3, FIELD_LENGTH * 0.75), # F1
            (FIELD_WIDTH * 0.7, FIELD_LENGTH * 0.75), # F2
        ]
        return Formation("1-3-2", positions)

