"""
Example script demonstrating how to use the optimizer for formations and tactics

This script shows the complete workflow:
1. Define fixed parameters (common to all teams)
2. Create baseline formations and tactics
3. Run batch simulations to compare configurations
4. Optimize formations and tactics using genetic algorithms
"""

import numpy as np
import json
from datetime import datetime

from parameter_config import (
    FixedParameters,
    TeamConfiguration,
    FormationParameters,
    TacticalParameters,
    FormationPresets
)
from batch_simulator import BatchSimulator, compare_formations, compare_tactics
from optimizer import GeneticOptimizer, FitnessEvaluator


def step1_compare_baseline_formations():
    """
    Step 1: Compare baseline formations to understand which ones perform better
    """
    print("\n" + "="*60)
    print("STEP 1: COMPARING BASELINE FORMATIONS")
    print("="*60)
    
    # Use default tactics for all
    default_tactics = TacticalParameters()
    
    # Compare different formations
    formations = {
        '2-3-1': FormationPresets.get_formation_2_3_1(),
        '3-2-1': FormationPresets.get_formation_3_2_1(),
        '2-2-2': FormationPresets.get_formation_2_2_2(),
        '1-3-2': FormationPresets.get_formation_1_3_2(),
    }
    
    results = {}
    
    # Test each formation against 2-3-1 baseline
    baseline_formation = FormationPresets.get_formation_2_3_1()
    
    for name, formation in formations.items():
        if name == '2-3-1':
            continue
        
        print(f"\n--- Testing {name} vs 2-3-1 ---")
        analysis = compare_formations(
            formation,
            baseline_formation,
            default_tactics,
            num_games=50,
            verbose=True
        )
        results[name] = analysis
    
    print("\n" + "="*60)
    print("BASELINE FORMATION COMPARISON COMPLETE")
    print("="*60)
    
    return results


def step2_optimize_formation_against_opponent():
    """
    Step 2: Optimize a formation against a specific opponent
    """
    print("\n" + "="*60)
    print("STEP 2: OPTIMIZING FORMATION AGAINST OPPONENT")
    print("="*60)
    
    # Start with a base formation
    base_formation = FormationPresets.get_formation_2_3_1()
    base_tactics = TacticalParameters()
    
    # Define opponent (a strong 3-2-1 formation)
    opponent_formation = FormationPresets.get_formation_3_2_1()
    opponent_config = TeamConfiguration(opponent_formation, base_tactics, team_id=1)
    
    # Create evaluator
    evaluator = FitnessEvaluator(
        opponent_config,
        num_games=20  # Run 20 games per fitness evaluation
    )
    
    # Create optimizer
    optimizer = GeneticOptimizer(
        population_size=30,
        mutation_rate=0.15,
        mutation_strength=0.08,
        crossover_rate=0.7,
        elite_fraction=0.1
    )
    
    # Optimize
    best_formation, best_fitness, history = optimizer.optimize_formation(
        base_formation,
        base_tactics,
        evaluator,
        generations=20,
        verbose=True
    )
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    optimizer.save_best(f"best_formation_{timestamp}.json")
    optimizer.save_history(f"formation_history_{timestamp}.json")
    
    print("\n" + "="*60)
    print("FORMATION OPTIMIZATION COMPLETE")
    print(f"Best Fitness: {best_fitness:.2f}")
    print("="*60)
    
    return best_formation, best_fitness, history


def step3_optimize_tactics():
    """
    Step 3: Optimize tactical parameters for a fixed formation
    """
    print("\n" + "="*60)
    print("STEP 3: OPTIMIZING TACTICS")
    print("="*60)
    
    # Use a fixed formation
    formation = FormationPresets.get_formation_2_3_1()
    
    # Start with baseline tactics
    base_tactics = TacticalParameters()
    
    # Define opponent
    opponent_formation = FormationPresets.get_formation_3_2_1()
    opponent_tactics = TacticalParameters(
        # Make opponent more defensive
        defensive_line_adherence=0.9,
        defensive_line_depth=0.1,
        ball_attraction_strength=0.6
    )
    opponent_config = TeamConfiguration(opponent_formation, opponent_tactics, team_id=1)
    
    # Create evaluator
    evaluator = FitnessEvaluator(
        opponent_config,
        num_games=20
    )
    
    # Create optimizer
    optimizer = GeneticOptimizer(
        population_size=30,
        mutation_rate=0.15,
        mutation_strength=0.1,
        crossover_rate=0.7
    )
    
    # Optimize
    best_tactics, best_fitness, history = optimizer.optimize_tactics(
        formation,
        base_tactics,
        evaluator,
        generations=20,
        verbose=True
    )
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    optimizer.save_best(f"best_tactics_{timestamp}.json")
    optimizer.save_history(f"tactics_history_{timestamp}.json")
    
    print("\n" + "="*60)
    print("TACTICS OPTIMIZATION COMPLETE")
    print(f"Best Fitness: {best_fitness:.2f}")
    print("="*60)
    
    # Print best tactics
    print("\nBest Tactical Parameters:")
    for key, value in best_tactics.to_dict().items():
        print(f"  {key}: {value:.3f}")
    
    return best_tactics, best_fitness, history


def step4_optimize_both():
    """
    Step 4: Optimize both formation and tactics simultaneously
    """
    print("\n" + "="*60)
    print("STEP 4: OPTIMIZING BOTH FORMATION AND TACTICS")
    print("="*60)
    
    # Start with baseline
    base_formation = FormationPresets.get_formation_2_3_1()
    base_tactics = TacticalParameters()
    
    # Define strong opponent
    opponent_formation = FormationPresets.get_formation_3_2_1()
    opponent_tactics = TacticalParameters(
        defensive_line_adherence=0.9,
        ball_attraction_strength=0.7,
        pass_propensity=0.7,
        shot_accuracy=0.5
    )
    opponent_config = TeamConfiguration(opponent_formation, opponent_tactics, team_id=1)
    
    # Create evaluator
    evaluator = FitnessEvaluator(
        opponent_config,
        num_games=15  # Fewer games per evaluation since this is slower
    )
    
    # Create optimizer
    optimizer = GeneticOptimizer(
        population_size=25,
        mutation_rate=0.15,
        mutation_strength=0.1,
        crossover_rate=0.7
    )
    
    # Optimize
    best_config, best_fitness, history = optimizer.optimize_both(
        base_formation,
        base_tactics,
        evaluator,
        generations=15,
        verbose=True
    )
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    optimizer.save_best(f"best_config_{timestamp}.json")
    optimizer.save_history(f"both_history_{timestamp}.json")
    
    print("\n" + "="*60)
    print("COMBINED OPTIMIZATION COMPLETE")
    print(f"Best Fitness: {best_fitness:.2f}")
    print("="*60)
    
    return best_config, best_fitness, history


def step5_validate_optimized_config():
    """
    Step 5: Validate the optimized configuration with more games
    """
    print("\n" + "="*60)
    print("STEP 5: VALIDATING OPTIMIZED CONFIGURATION")
    print("="*60)
    
    # Load the best configuration (or use from previous step)
    # For this example, we'll create a sample optimized config
    optimized_formation = FormationPresets.get_formation_2_3_1()
    optimized_tactics = TacticalParameters(
        ball_attraction_strength=0.85,
        pass_propensity=0.65,
        shot_accuracy=0.45
    )
    optimized_config = TeamConfiguration(optimized_formation, optimized_tactics, team_id=0)
    
    # Baseline config
    baseline_formation = FormationPresets.get_formation_2_3_1()
    baseline_tactics = TacticalParameters()
    baseline_config = TeamConfiguration(baseline_formation, baseline_tactics, team_id=1)
    
    # Run extensive validation
    simulator = BatchSimulator()
    
    print("\n--- Running 100 validation games ---")
    results = simulator.run_games(
        optimized_config,
        baseline_config,
        num_games=100,
        parallel=True,
        verbose=True
    )
    
    # Analyze
    analysis = simulator.analyze_results(results)
    simulator.print_analysis(analysis)
    
    # Save validation results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    simulator.save_results(results, f"validation_results_{timestamp}.json")
    
    print("\n" + "="*60)
    print("VALIDATION COMPLETE")
    print("="*60)
    
    return analysis


def quick_optimization_example():
    """
    Quick example for testing (fewer games/generations)
    """
    print("\n" + "="*60)
    print("QUICK OPTIMIZATION EXAMPLE")
    print("="*60)
    
    # Setup
    base_formation = FormationPresets.get_formation_2_3_1()
    base_tactics = TacticalParameters()
    
    opponent_formation = FormationPresets.get_formation_3_2_1()
    opponent_config = TeamConfiguration(opponent_formation, base_tactics, team_id=1)
    
    # Create evaluator with fewer games
    evaluator = FitnessEvaluator(opponent_config, num_games=10)
    
    # Create optimizer with smaller population
    optimizer = GeneticOptimizer(
        population_size=15,
        mutation_rate=0.15,
        mutation_strength=0.1
    )
    
    # Optimize formation only
    print("\n--- Optimizing Formation (Quick) ---")
    best_formation, best_fitness, history = optimizer.optimize_formation(
        base_formation,
        base_tactics,
        evaluator,
        generations=5,
        verbose=True
    )
    
    print(f"\n✓ Quick optimization complete!")
    print(f"Best Fitness: {best_fitness:.2f}")
    
    return best_formation, best_fitness


def main():
    """
    Main function - choose which step to run
    """
    import sys
    
    if len(sys.argv) < 2:
        print("\nUsage: python optimize_example.py <step>")
        print("\nAvailable steps:")
        print("  1  - Compare baseline formations")
        print("  2  - Optimize formation against opponent")
        print("  3  - Optimize tactics for fixed formation")
        print("  4  - Optimize both formation and tactics")
        print("  5  - Validate optimized configuration")
        print("  quick - Quick optimization example (for testing)")
        print("  all - Run all steps sequentially")
        return
    
    step = sys.argv[1].lower()
    
    if step == '1':
        step1_compare_baseline_formations()
    elif step == '2':
        step2_optimize_formation_against_opponent()
    elif step == '3':
        step3_optimize_tactics()
    elif step == '4':
        step4_optimize_both()
    elif step == '5':
        step5_validate_optimized_config()
    elif step == 'quick':
        quick_optimization_example()
    elif step == 'all':
        print("\n🚀 Running complete optimization pipeline...\n")
        step1_compare_baseline_formations()
        step2_optimize_formation_against_opponent()
        step3_optimize_tactics()
        step4_optimize_both()
        step5_validate_optimized_config()
        print("\n✅ All steps completed!")
    else:
        print(f"Unknown step: {step}")
        print("Use: 1, 2, 3, 4, 5, quick, or all")


if __name__ == '__main__':
    # If no arguments, run quick example
    import sys
    if len(sys.argv) == 1:
        print("\nNo arguments provided, running quick example...")
        print("For full options, run: python optimize_example.py")
        quick_optimization_example()
    else:
        main()

