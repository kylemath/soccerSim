"""
Parameter Configuration for Soccer Simulation
Separates fixed parameters from optimizable parameters
"""

from dataclasses import dataclass, field
from typing import List, Tuple
import numpy as np


@dataclass
class FixedParameters:
    """Parameters that are common across all teams and players"""
    
    # Field dimensions (fixed for all games)
    field_length: float = 40.0
    field_width: float = 30.0
    goal_width: float = 3.0
    goal_depth: float = 1.0
    
    # Physical constants (fixed for all games)
    player_radius: float = 0.3
    player_speed_max: float = 5.0
    player_acceleration: float = 8.0
    player_deceleration: float = 10.0
    player_inertia: float = 0.3
    
    # Ball properties (fixed for all games)
    ball_radius: float = 0.11
    ball_mass: float = 0.43
    ball_friction: float = 0.015
    ball_max_speed: float = 25.0
    ball_air_resistance: float = 0.005
    
    # Game rules (fixed for all games)
    game_duration_seconds: float = 2 * 60  # 2 minutes for testing
    time_step: float = 0.016
    possession_distance: float = 3.0
    
    # Goalkeeper parameters (fixed)
    gk_radius: float = 0.35
    gk_speed_max: float = 6.0
    gk_reaction_time: float = 0.2
    gk_positioning_range: float = 2.0
    gk_save_probability: float = 0.7


@dataclass
class TacticalParameters:
    """Parameters that can be optimized for each team's tactics"""
    
    # Formation behavior
    formation_fuzziness: float = 0.5  # How much players deviate from formation
    formation_adherence_rate: float = 0.6  # How quickly players return to formation
    formation_elasticity: float = 1.5  # Spring constant for formation positioning
    formation_damping: float = 0.4  # Damping factor to prevent oscillation
    
    # Defensive tactics
    defensive_line_adherence: float = 0.8  # How strongly defenders adhere to defensive line
    defensive_line_depth: float = 0.15  # Defensive line depth (fraction of field)
    
    # Offensive tactics
    forward_push_rate: float = 0.6  # How much forwards push forward toward ball
    ball_attraction_strength: float = 0.8  # How much players are drawn to ball vs formation
    
    # Ball reaction distances
    ball_reaction_distance: float = 15.0  # Distance at which players actively pursue ball
    ball_close_distance: float = 5.0  # Distance within which players prioritize ball
    
    # Player behavior
    pass_propensity: float = 0.6  # Probability of passing vs shooting
    shoot_propensity: float = 0.3  # Probability of shooting
    pass_accuracy: float = 0.8  # Pass accuracy (0-1)
    shot_accuracy: float = 0.4  # Shot accuracy (0-1)
    pass_speed_factor: float = 0.6  # Multiplier for pass power
    shot_speed_factor: float = 1.2  # Multiplier for shot power
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'formation_fuzziness': self.formation_fuzziness,
            'formation_adherence_rate': self.formation_adherence_rate,
            'formation_elasticity': self.formation_elasticity,
            'formation_damping': self.formation_damping,
            'defensive_line_adherence': self.defensive_line_adherence,
            'defensive_line_depth': self.defensive_line_depth,
            'forward_push_rate': self.forward_push_rate,
            'ball_attraction_strength': self.ball_attraction_strength,
            'ball_reaction_distance': self.ball_reaction_distance,
            'ball_close_distance': self.ball_close_distance,
            'pass_propensity': self.pass_propensity,
            'shoot_propensity': self.shoot_propensity,
            'pass_accuracy': self.pass_accuracy,
            'shot_accuracy': self.shot_accuracy,
            'pass_speed_factor': self.pass_speed_factor,
            'shot_speed_factor': self.shot_speed_factor,
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create from dictionary"""
        return cls(**data)
    
    def mutate(self, mutation_rate=0.1, mutation_strength=0.1):
        """Mutate tactical parameters"""
        mutated = TacticalParameters()
        for key, value in self.to_dict().items():
            if np.random.random() < mutation_rate:
                # Mutate the parameter
                if isinstance(value, float):
                    delta = np.random.normal(0, mutation_strength * value)
                    new_value = max(0.0, min(1.0, value + delta))  # Clamp to [0, 1]
                    setattr(mutated, key, new_value)
                else:
                    setattr(mutated, key, value)
            else:
                setattr(mutated, key, value)
        return mutated
    
    def crossover(self, other):
        """Crossover with another tactical parameter set"""
        child = TacticalParameters()
        for key in self.to_dict().keys():
            if np.random.random() < 0.5:
                setattr(child, key, getattr(self, key))
            else:
                setattr(child, key, getattr(other, key))
        return child


@dataclass
class FormationParameters:
    """Parameters that define a team's formation"""
    
    name: str = "Custom"
    positions: List[Tuple[float, float]] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.positions:
            # Default 2-3-1 formation (normalized coordinates 0-1)
            self.positions = [
                (0.5, 0.05),   # GK
                (0.3, 0.2),    # D1
                (0.7, 0.2),    # D2
                (0.2, 0.5),    # M1
                (0.5, 0.5),    # M2
                (0.8, 0.5),    # M3
                (0.5, 0.75),   # F1
            ]
    
    def to_absolute_positions(self, field_width, field_length):
        """Convert normalized positions to absolute coordinates"""
        absolute = []
        for x, y in self.positions:
            abs_x = x * field_width
            abs_y = y * field_length
            absolute.append((abs_x, abs_y))
        return absolute
    
    def mutate(self, mutation_rate=0.1, mutation_strength=0.05):
        """Mutate formation positions"""
        mutated_positions = []
        for x, y in self.positions:
            if np.random.random() < mutation_rate:
                new_x = x + np.random.normal(0, mutation_strength)
                new_y = y + np.random.normal(0, mutation_strength)
                # Clamp to valid range
                new_x = max(0.05, min(0.95, new_x))
                new_y = max(0.05, min(0.95, new_y))
                mutated_positions.append((new_x, new_y))
            else:
                mutated_positions.append((x, y))
        
        return FormationParameters(f"{self.name}_mutated", mutated_positions)
    
    def crossover(self, other):
        """Crossover with another formation"""
        child_positions = []
        for i in range(min(len(self.positions), len(other.positions))):
            if np.random.random() < 0.5:
                child_positions.append(self.positions[i])
            else:
                child_positions.append(other.positions[i])
        
        return FormationParameters(f"{self.name}_x_{other.name}", child_positions)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'name': self.name,
            'positions': self.positions
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create from dictionary"""
        return cls(data['name'], data['positions'])


# Preset formations
class FormationPresets:
    """Predefined formations in normalized coordinates"""
    
    @staticmethod
    def get_formation_2_3_1():
        """2-3-1 formation"""
        return FormationParameters("2-3-1", [
            (0.5, 0.05),   # GK
            (0.3, 0.2),    # D1
            (0.7, 0.2),    # D2
            (0.2, 0.5),    # M1
            (0.5, 0.5),    # M2
            (0.8, 0.5),    # M3
            (0.5, 0.75),   # F1
        ])
    
    @staticmethod
    def get_formation_3_2_1():
        """3-2-1 formation"""
        return FormationParameters("3-2-1", [
            (0.5, 0.05),   # GK
            (0.25, 0.2),   # D1
            (0.5, 0.2),    # D2
            (0.75, 0.2),   # D3
            (0.35, 0.5),   # M1
            (0.65, 0.5),   # M2
            (0.5, 0.75),   # F1
        ])
    
    @staticmethod
    def get_formation_2_2_2():
        """2-2-2 formation"""
        return FormationParameters("2-2-2", [
            (0.5, 0.05),   # GK
            (0.3, 0.25),   # D1
            (0.7, 0.25),   # D2
            (0.3, 0.5),    # M1
            (0.7, 0.5),    # M2
            (0.3, 0.75),   # F1
            (0.7, 0.75),   # F2
        ])
    
    @staticmethod
    def get_formation_1_3_2():
        """1-3-2 formation"""
        return FormationParameters("1-3-2", [
            (0.5, 0.05),   # GK
            (0.5, 0.2),    # D1
            (0.2, 0.4),    # M1
            (0.5, 0.4),    # M2
            (0.8, 0.4),    # M3
            (0.3, 0.75),   # F1
            (0.7, 0.75),   # F2
        ])


@dataclass
class TeamConfiguration:
    """Complete configuration for a team"""
    
    formation: FormationParameters
    tactics: TacticalParameters
    team_id: int = 0
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'formation': self.formation.to_dict(),
            'tactics': self.tactics.to_dict(),
            'team_id': self.team_id
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create from dictionary"""
        return cls(
            formation=FormationParameters.from_dict(data['formation']),
            tactics=TacticalParameters.from_dict(data['tactics']),
            team_id=data.get('team_id', 0)
        )

