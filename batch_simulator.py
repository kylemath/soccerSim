"""
Batch Simulator for running many games without visualization
"""

import numpy as np
import json
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import multiprocessing as mp
from functools import partial
import time

from game import Game
from formation import Formation
from parameter_config import (
    FixedParameters, 
    TeamConfiguration, 
    FormationParameters,
    TacticalParameters
)
from config import FIELD_WIDTH, FIELD_LENGTH


def convert_to_formation(formation_params: FormationParameters) -> Formation:
    """Convert FormationParameters to Formation object"""
    absolute_positions = formation_params.to_absolute_positions(FIELD_WIDTH, FIELD_LENGTH)
    return Formation(formation_params.name, absolute_positions)


def run_single_game(team1_config: TeamConfiguration, 
                   team2_config: TeamConfiguration,
                   fixed_params: FixedParameters,
                   random_seed: Optional[int] = None) -> Dict:
    """Run a single game and return the results"""
    
    # Convert to Formation objects
    team1_formation = convert_to_formation(team1_config.formation)
    team2_formation = convert_to_formation(team2_config.formation)
    
    # Create game
    game = Game(team1_formation, team2_formation, random_seed=random_seed)
    
    # Run game simulation (no visualization)
    dt = fixed_params.time_step
    while game.is_running and game.time < game.duration:
        game.update(dt)
    
    # Get final stats
    final_stats = game.get_final_stats()
    
    # Add team configurations to result
    final_stats['team1_config'] = team1_config.to_dict()
    final_stats['team2_config'] = team2_config.to_dict()
    final_stats['random_seed'] = random_seed
    
    return final_stats


def run_single_game_wrapper(args):
    """Wrapper for multiprocessing"""
    return run_single_game(*args)


class BatchSimulator:
    """Batch simulator for running many games efficiently"""
    
    def __init__(self, fixed_params: Optional[FixedParameters] = None):
        self.fixed_params = fixed_params or FixedParameters()
        self.results = []
    
    def run_games(self, 
                  team1_config: TeamConfiguration,
                  team2_config: TeamConfiguration,
                  num_games: int = 100,
                  parallel: bool = True,
                  num_workers: Optional[int] = None,
                  verbose: bool = True) -> List[Dict]:
        """
        Run multiple games between two team configurations
        
        Args:
            team1_config: Configuration for team 1
            team2_config: Configuration for team 2
            num_games: Number of games to simulate
            parallel: Whether to run games in parallel
            num_workers: Number of parallel workers (None = auto)
            verbose: Whether to print progress
        
        Returns:
            List of game results
        """
        
        if verbose:
            print(f"Running {num_games} games...")
            print(f"Team 1 Formation: {team1_config.formation.name}")
            print(f"Team 2 Formation: {team2_config.formation.name}")
            start_time = time.time()
        
        # Generate random seeds for each game
        random_seeds = [np.random.randint(0, 2**31) for _ in range(num_games)]
        
        # Prepare arguments for each game
        game_args = [
            (team1_config, team2_config, self.fixed_params, seed)
            for seed in random_seeds
        ]
        
        if parallel and num_games > 1:
            # Run games in parallel
            if num_workers is None:
                num_workers = min(mp.cpu_count(), num_games)
            
            with mp.Pool(num_workers) as pool:
                results = pool.map(run_single_game_wrapper, game_args)
        else:
            # Run games sequentially
            results = []
            for i, args in enumerate(game_args):
                if verbose and (i + 1) % 10 == 0:
                    print(f"  Completed {i + 1}/{num_games} games...")
                results.append(run_single_game(*args))
        
        if verbose:
            elapsed = time.time() - start_time
            print(f"Completed {num_games} games in {elapsed:.2f} seconds")
            print(f"Average time per game: {elapsed/num_games:.3f} seconds")
        
        self.results.extend(results)
        return results
    
    def analyze_results(self, results: List[Dict]) -> Dict:
        """
        Analyze results from multiple games
        
        Returns:
            Dictionary with aggregated statistics
        """
        
        # Extract statistics
        team1_goals = [r['final_score']['team1'] for r in results]
        team2_goals = [r['final_score']['team2'] for r in results]
        team1_wins = sum(1 for r in results if r['final_score']['team1'] > r['final_score']['team2'])
        team2_wins = sum(1 for r in results if r['final_score']['team2'] > r['final_score']['team1'])
        draws = sum(1 for r in results if r['final_score']['team1'] == r['final_score']['team2'])
        
        team1_shots = [r['team1_stats']['shots'] for r in results]
        team2_shots = [r['team2_stats']['shots'] for r in results]
        team1_passes = [r['team1_stats']['passes'] for r in results]
        team2_passes = [r['team2_stats']['passes'] for r in results]
        team1_possession = [r['team1_stats']['possession_time'] for r in results]
        team2_possession = [r['team2_stats']['possession_time'] for r in results]
        
        analysis = {
            'num_games': len(results),
            'team1': {
                'wins': team1_wins,
                'win_rate': team1_wins / len(results),
                'avg_goals': np.mean(team1_goals),
                'std_goals': np.std(team1_goals),
                'avg_shots': np.mean(team1_shots),
                'avg_passes': np.mean(team1_passes),
                'avg_possession': np.mean(team1_possession),
            },
            'team2': {
                'wins': team2_wins,
                'win_rate': team2_wins / len(results),
                'avg_goals': np.mean(team2_goals),
                'std_goals': np.std(team2_goals),
                'avg_shots': np.mean(team2_shots),
                'avg_passes': np.mean(team2_passes),
                'avg_possession': np.mean(team2_possession),
            },
            'draws': draws,
            'draw_rate': draws / len(results),
        }
        
        return analysis
    
    def print_analysis(self, analysis: Dict):
        """Pretty print analysis results"""
        print("\n=== BATCH SIMULATION RESULTS ===")
        print(f"Total Games: {analysis['num_games']}")
        print(f"\nTeam 1 Performance:")
        print(f"  Wins: {analysis['team1']['wins']} ({analysis['team1']['win_rate']*100:.1f}%)")
        print(f"  Avg Goals: {analysis['team1']['avg_goals']:.2f} ± {analysis['team1']['std_goals']:.2f}")
        print(f"  Avg Shots: {analysis['team1']['avg_shots']:.1f}")
        print(f"  Avg Passes: {analysis['team1']['avg_passes']:.1f}")
        print(f"  Avg Possession: {analysis['team1']['avg_possession']:.1f}s")
        
        print(f"\nTeam 2 Performance:")
        print(f"  Wins: {analysis['team2']['wins']} ({analysis['team2']['win_rate']*100:.1f}%)")
        print(f"  Avg Goals: {analysis['team2']['avg_goals']:.2f} ± {analysis['team2']['std_goals']:.2f}")
        print(f"  Avg Shots: {analysis['team2']['avg_shots']:.1f}")
        print(f"  Avg Passes: {analysis['team2']['avg_passes']:.1f}")
        print(f"  Avg Possession: {analysis['team2']['avg_possession']:.1f}s")
        
        print(f"\nDraws: {analysis['draws']} ({analysis['draw_rate']*100:.1f}%)")
    
    def save_results(self, results: List[Dict], filename: str):
        """Save results to JSON file"""
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to {filename}")
    
    def load_results(self, filename: str) -> List[Dict]:
        """Load results from JSON file"""
        with open(filename, 'r') as f:
            results = json.load(f)
        return results


def compare_formations(formation1: FormationParameters,
                      formation2: FormationParameters,
                      tactics: TacticalParameters,
                      num_games: int = 100,
                      verbose: bool = True) -> Dict:
    """
    Compare two formations using the same tactics
    
    Args:
        formation1: First formation to test
        formation2: Second formation to test
        tactics: Tactical parameters (same for both teams)
        num_games: Number of games to simulate
        verbose: Whether to print progress
    
    Returns:
        Analysis of results
    """
    
    team1_config = TeamConfiguration(formation1, tactics, team_id=0)
    team2_config = TeamConfiguration(formation2, tactics, team_id=1)
    
    simulator = BatchSimulator()
    results = simulator.run_games(team1_config, team2_config, num_games, verbose=verbose)
    analysis = simulator.analyze_results(results)
    
    if verbose:
        simulator.print_analysis(analysis)
    
    return analysis


def compare_tactics(formation: FormationParameters,
                   tactics1: TacticalParameters,
                   tactics2: TacticalParameters,
                   num_games: int = 100,
                   verbose: bool = True) -> Dict:
    """
    Compare two tactical approaches using the same formation
    
    Args:
        formation: Formation to use (same for both teams)
        tactics1: First tactical approach
        tactics2: Second tactical approach
        num_games: Number of games to simulate
        verbose: Whether to print progress
    
    Returns:
        Analysis of results
    """
    
    team1_config = TeamConfiguration(formation, tactics1, team_id=0)
    team2_config = TeamConfiguration(formation, tactics2, team_id=1)
    
    simulator = BatchSimulator()
    results = simulator.run_games(team1_config, team2_config, num_games, verbose=verbose)
    analysis = simulator.analyze_results(results)
    
    if verbose:
        simulator.print_analysis(analysis)
    
    return analysis


if __name__ == '__main__':
    # Example usage
    from parameter_config import FormationPresets
    
    print("=== Batch Simulator Test ===\n")
    
    # Create team configurations
    formation_2_3_1 = FormationPresets.get_formation_2_3_1()
    formation_3_2_1 = FormationPresets.get_formation_3_2_1()
    default_tactics = TacticalParameters()
    
    # Test comparing formations
    print("\n--- Testing Formation Comparison ---")
    compare_formations(formation_2_3_1, formation_3_2_1, default_tactics, num_games=20)

