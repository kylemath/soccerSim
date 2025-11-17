"""
Main simulator for running games and generating visualization data
"""

import json
import numpy as np
from game import Game
from formation import Formation, FormationLibrary
from database import Database
from config import *


class Simulator:
    """Simulator for running games and collecting data"""
    def __init__(self, db_path='soccer_sim.db'):
        self.db = Database(db_path)
    
    def run_game(self, team1_formation, team2_formation, record_states=True):
        """Run a single game and return states for visualization"""
        game = Game(team1_formation, team2_formation)
        
        states = []
        dt = TIME_STEP
        last_record_time = 0.0
        
        while game.is_running and game.time < game.duration:
            game.update(dt)
            if record_states:
                # Record state every 0.1 seconds for visualization
                if len(states) == 0 or game.time - last_record_time >= 0.1:
                    states.append(game.get_state())
                    last_record_time = game.time
        
        final_stats = game.get_final_stats()
        
        return {
            'states': states,
            'final_stats': final_stats
        }
    
    def run_and_save_game(self, team1_formation, team2_formation):
        """Run game and save to database"""
        result = self.run_game(team1_formation, team2_formation, record_states=False)
        game_id = self.db.save_game(result['final_stats'])
        result['final_stats']['db_id'] = game_id
        return result
    
    def generate_visualization_data(self, game_result):
        """Generate data for HTML visualization"""
        states = game_result['states']
        final_stats = game_result['final_stats']
        
        # Extract time series data
        times = [s['time'] for s in states]
        
        # Ball position over time
        ball_x = [s['ball']['x'] for s in states]
        ball_y = [s['ball']['y'] for s in states]
        ball_speed = [s['ball']['speed'] for s in states]
        
        # Player positions over time
        team1_positions = []
        team2_positions = []
        for state in states:
            team1_positions.append([(p['x'], p['y']) for p in state['team1_players']])
            team2_positions.append([(p['x'], p['y']) for p in state['team2_players']])
        
        # Stats over time
        team1_passes = [s['stats']['team1']['passes'] for s in states]
        team2_passes = [s['stats']['team2']['passes'] for s in states]
        team1_shots = [s['stats']['team1']['shots'] for s in states]
        team2_shots = [s['stats']['team2']['shots'] for s in states]
        team1_possession = [s['stats']['team1']['possession_time'] for s in states]
        team2_possession = [s['stats']['team2']['possession_time'] for s in states]
        
        # Score over time
        team1_goals = [s['score']['team1'] for s in states]
        team2_goals = [s['score']['team2'] for s in states]
        
        return {
            'times': times,
            'ball': {
                'x': ball_x,
                'y': ball_y,
                'speed': ball_speed
            },
            'team1_positions': team1_positions,
            'team2_positions': team2_positions,
            'stats': {
                'team1_passes': team1_passes,
                'team2_passes': team2_passes,
                'team1_shots': team1_shots,
                'team2_shots': team2_shots,
                'team1_possession': team1_possession,
                'team2_possession': team2_possession,
                'team1_goals': team1_goals,
                'team2_goals': team2_goals
            },
            'final_stats': final_stats,
            'field': {
                'width': FIELD_WIDTH,
                'length': FIELD_LENGTH,
                'goal_width': GOAL_WIDTH
            }
        }

