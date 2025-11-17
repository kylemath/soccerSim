"""
Quick test script to run a single game simulation
"""

from simulator import Simulator
from formation import FormationLibrary
from config import *

# Override game duration for testing
import config
config.GAME_DURATION_SECONDS = 60  # 1 minute for quick testing

if __name__ == '__main__':
    print("Running test game simulation...")
    
    simulator = Simulator()
    
    # Test with different formations
    team1_formation = FormationLibrary.get_formation('2-3-1')
    team2_formation = FormationLibrary.get_formation('3-2-1')
    
    print(f"Team 1 Formation: {team1_formation.name}")
    print(f"Team 2 Formation: {team2_formation.name}")
    print(f"Game Duration: {config.GAME_DURATION_SECONDS} seconds")
    print("\nRunning simulation...")
    
    result = simulator.run_game(team1_formation, team2_formation, record_states=True)
    
    final_stats = result['final_stats']
    
    print("\n=== FINAL RESULTS ===")
    print(f"Final Score: Team 1 {final_stats['final_score']['team1']} - {final_stats['final_score']['team2']} Team 2")
    print(f"\nTeam 1 Stats:")
    print(f"  Goals: {final_stats['team1_stats']['goals']}")
    print(f"  Passes: {final_stats['team1_stats']['passes']}")
    print(f"  Shots: {final_stats['team1_stats']['shots']}")
    print(f"  Possession Time: {final_stats['team1_stats']['possession_time']:.1f}s")
    print(f"  Touches: {final_stats['team1_stats']['touches']}")
    
    print(f"\nTeam 2 Stats:")
    print(f"  Goals: {final_stats['team2_stats']['goals']}")
    print(f"  Passes: {final_stats['team2_stats']['passes']}")
    print(f"  Shots: {final_stats['team2_stats']['shots']}")
    print(f"  Possession Time: {final_stats['team2_stats']['possession_time']:.1f}s")
    print(f"  Touches: {final_stats['team2_stats']['touches']}")
    
    print(f"\nTotal Events: {len(final_stats['events'])}")
    print(f"States Recorded: {len(result['states'])}")
    
    print("\nTest completed successfully!")

