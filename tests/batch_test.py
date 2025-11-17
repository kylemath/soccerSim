#!/usr/bin/env python3
"""
Quick batch test script - Run many games quickly to test performance
"""

import time
import sys
from parameter_config import (
    FixedParameters,
    TeamConfiguration,
    FormationParameters,
    TacticalParameters,
    FormationPresets
)
from batch_simulator import BatchSimulator


def quick_batch_test(num_games=100, game_duration=120):
    """Quick test of batch simulation"""
    
    print("\n" + "="*60)
    print("QUICK BATCH TEST")
    print("="*60)
    
    # Set game duration (can make shorter for testing)
    fixed_params = FixedParameters(game_duration_seconds=game_duration)
    
    # Create simple team configurations
    team1_config = TeamConfiguration(
        FormationPresets.get_formation_2_3_1(),
        TacticalParameters(),
        team_id=0
    )
    
    team2_config = TeamConfiguration(
        FormationPresets.get_formation_3_2_1(),
        TacticalParameters(),
        team_id=1
    )
    
    print(f"\nConfiguration:")
    print(f"  Team 1: {team1_config.formation.name}")
    print(f"  Team 2: {team2_config.formation.name}")
    print(f"  Game Duration: {game_duration}s")
    print(f"  Number of Games: {num_games}")
    print(f"  Using parallel processing: Yes")
    
    # Run batch simulation
    simulator = BatchSimulator(fixed_params)
    
    print("\n" + "-"*60)
    print("Running games...")
    start_time = time.time()
    
    results = simulator.run_games(
        team1_config,
        team2_config,
        num_games=num_games,
        parallel=True,
        verbose=True
    )
    
    elapsed = time.time() - start_time
    
    print("\n" + "-"*60)
    print("RESULTS")
    print("-"*60)
    
    # Analyze results
    analysis = simulator.analyze_results(results)
    simulator.print_analysis(analysis)
    
    print(f"\nPerformance:")
    print(f"  Total Time: {elapsed:.2f} seconds")
    print(f"  Time per Game: {elapsed/num_games:.3f} seconds")
    print(f"  Games per Second: {num_games/elapsed:.2f}")
    
    print("\n" + "="*60)
    print("Batch test complete!")
    print("="*60 + "\n")
    
    return results, analysis


def compare_formations():
    """Compare different formations"""
    
    print("\n" + "="*60)
    print("COMPARING FORMATIONS")
    print("="*60)
    
    fixed_params = FixedParameters(game_duration_seconds=60)  # Shorter for testing
    base_tactics = TacticalParameters()
    
    formations = {
        '2-3-1': FormationPresets.get_formation_2_3_1(),
        '3-2-1': FormationPresets.get_formation_3_2_1(),
        '2-2-2': FormationPresets.get_formation_2_2_2(),
        '1-3-2': FormationPresets.get_formation_1_3_2(),
    }
    
    # Test each formation against 2-3-1
    baseline_formation = FormationPresets.get_formation_2_3_1()
    baseline_config = TeamConfiguration(baseline_formation, base_tactics, team_id=1)
    
    simulator = BatchSimulator(fixed_params)
    
    print(f"\nTesting each formation against baseline (2-3-1)")
    print(f"Games per comparison: 50")
    print(f"Game duration: {fixed_params.game_duration_seconds}s\n")
    
    results_summary = {}
    
    for name, formation in formations.items():
        if name == '2-3-1':
            continue  # Skip baseline
        
        print(f"\n--- Testing {name} vs 2-3-1 ---")
        
        test_config = TeamConfiguration(formation, base_tactics, team_id=0)
        
        start_time = time.time()
        results = simulator.run_games(
            test_config,
            baseline_config,
            num_games=50,
            parallel=True,
            verbose=False
        )
        elapsed = time.time() - start_time
        
        analysis = simulator.analyze_results(results)
        
        results_summary[name] = {
            'win_rate': analysis['team1']['win_rate'],
            'avg_goals': analysis['team1']['avg_goals'],
            'time': elapsed
        }
        
        print(f"  Win Rate: {analysis['team1']['win_rate']*100:.1f}%")
        print(f"  Avg Goals: {analysis['team1']['avg_goals']:.2f}")
        print(f"  Time: {elapsed:.2f}s")
    
    print("\n" + "="*60)
    print("COMPARISON SUMMARY")
    print("="*60)
    
    for name, stats in results_summary.items():
        print(f"\n{name}:")
        print(f"  Win Rate: {stats['win_rate']*100:.1f}%")
        print(f"  Avg Goals: {stats['avg_goals']:.2f}")
        print(f"  Test Time: {stats['time']:.2f}s")
    
    return results_summary


def test_performance(num_games_list=[10, 50, 100, 500]):
    """Test performance with different numbers of games"""
    
    print("\n" + "="*60)
    print("PERFORMANCE TEST")
    print("="*60)
    
    fixed_params = FixedParameters(game_duration_seconds=60)  # Shorter for testing
    
    team1_config = TeamConfiguration(
        FormationPresets.get_formation_2_3_1(),
        TacticalParameters(),
        team_id=0
    )
    
    team2_config = TeamConfiguration(
        FormationPresets.get_formation_3_2_1(),
        TacticalParameters(),
        team_id=1
    )
    
    simulator = BatchSimulator(fixed_params)
    
    print("\nTesting parallel processing performance:\n")
    
    for num_games in num_games_list:
        print(f"Running {num_games} games...", end=' ', flush=True)
        
        start_time = time.time()
        results = simulator.run_games(
            team1_config,
            team2_config,
            num_games=num_games,
            parallel=True,
            verbose=False
        )
        elapsed = time.time() - start_time
        
        games_per_sec = num_games / elapsed
        time_per_game = elapsed / num_games
        
        print(f"Done! ({elapsed:.2f}s)")
        print(f"  {games_per_sec:.2f} games/second")
        print(f"  {time_per_game:.3f} seconds/game")
        print()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Quick batch test for soccer simulator')
    parser.add_argument('--games', type=int, default=100, help='Number of games to run (default: 100)')
    parser.add_argument('--duration', type=int, default=120, help='Game duration in seconds (default: 120)')
    parser.add_argument('--compare', action='store_true', help='Compare different formations')
    parser.add_argument('--perf', action='store_true', help='Test performance with different game counts')
    
    args = parser.parse_args()
    
    if args.compare:
        compare_formations()
    elif args.perf:
        test_performance()
    else:
        quick_batch_test(args.games, args.duration)

