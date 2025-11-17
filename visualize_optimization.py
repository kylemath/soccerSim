"""
Visualize optimization results and compare configurations
"""

import json
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict


def plot_optimization_history(history_file: str, save_file: str = None):
    """
    Plot optimization history showing fitness over generations
    
    Args:
        history_file: Path to history JSON file
        save_file: Optional path to save figure
    """
    # Load history
    with open(history_file, 'r') as f:
        history = json.load(f)
    
    # Extract data
    generations = [h['generation'] for h in history]
    best_fitness = [h['best_fitness'] for h in history]
    avg_fitness = [h['avg_fitness'] for h in history]
    std_fitness = [h['std_fitness'] for h in history]
    
    # Create plot
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot best and average fitness
    ax.plot(generations, best_fitness, 'g-', linewidth=2, label='Best Fitness')
    ax.plot(generations, avg_fitness, 'b-', linewidth=2, label='Average Fitness')
    
    # Add standard deviation band
    avg_fitness_array = np.array(avg_fitness)
    std_fitness_array = np.array(std_fitness)
    ax.fill_between(
        generations,
        avg_fitness_array - std_fitness_array,
        avg_fitness_array + std_fitness_array,
        alpha=0.3,
        label='Std Dev'
    )
    
    ax.set_xlabel('Generation', fontsize=12)
    ax.set_ylabel('Fitness', fontsize=12)
    ax.set_title('Optimization Progress', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_file:
        plt.savefig(save_file, dpi=300, bbox_inches='tight')
        print(f"Plot saved to {save_file}")
    else:
        plt.show()


def plot_formation_comparison(formation1_file: str, 
                             formation2_file: str,
                             labels: List[str] = None):
    """
    Visualize two formations side by side
    
    Args:
        formation1_file: Path to first formation JSON
        formation2_file: Path to second formation JSON
        labels: Optional labels for formations
    """
    # Load formations
    with open(formation1_file, 'r') as f:
        formation1 = json.load(f)
    with open(formation2_file, 'r') as f:
        formation2 = json.load(f)
    
    if labels is None:
        labels = [formation1.get('name', 'Formation 1'), 
                 formation2.get('name', 'Formation 2')]
    
    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Plot formation 1
    _plot_formation(ax1, formation1['positions'], labels[0])
    
    # Plot formation 2
    _plot_formation(ax2, formation2['positions'], labels[1])
    
    plt.tight_layout()
    plt.show()


def _plot_formation(ax, positions: List[List[float]], title: str):
    """Helper function to plot a single formation"""
    
    # Field dimensions (normalized 0-1)
    field_width = 1.0
    field_length = 1.0
    
    # Draw field
    ax.set_xlim(0, field_width)
    ax.set_ylim(0, field_length)
    ax.set_aspect('equal')
    
    # Draw field lines
    ax.plot([0, field_width], [0, 0], 'k-', linewidth=2)  # Bottom
    ax.plot([0, field_width], [field_length, field_length], 'k-', linewidth=2)  # Top
    ax.plot([0, 0], [0, field_length], 'k-', linewidth=2)  # Left
    ax.plot([field_width, field_width], [0, field_length], 'k-', linewidth=2)  # Right
    ax.plot([0, field_width], [field_length/2, field_length/2], 'k--', linewidth=1, alpha=0.5)  # Center line
    
    # Draw goals
    goal_width = 0.2
    goal_center = field_width / 2
    ax.plot([goal_center - goal_width/2, goal_center + goal_width/2], 
           [0, 0], 'r-', linewidth=4, label='Goal')
    ax.plot([goal_center - goal_width/2, goal_center + goal_width/2], 
           [field_length, field_length], 'b-', linewidth=4)
    
    # Plot players
    for i, (x, y) in enumerate(positions):
        if i == 0:
            # Goalkeeper
            ax.scatter(x, y, c='red', s=300, marker='o', 
                      edgecolors='black', linewidth=2, label='GK', zorder=10)
            ax.text(x, y, 'GK', ha='center', va='center', 
                   fontsize=8, fontweight='bold')
        else:
            # Field player
            ax.scatter(x, y, c='lightblue', s=200, marker='o',
                      edgecolors='black', linewidth=2, zorder=10)
            ax.text(x, y, str(i), ha='center', va='center',
                   fontsize=8, fontweight='bold')
    
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.set_xlabel('Field Width')
    ax.set_ylabel('Field Length')
    ax.legend(loc='upper right')


def compare_batch_results(results_files: List[str], labels: List[str] = None):
    """
    Compare results from multiple batch simulations
    
    Args:
        results_files: List of paths to result JSON files
        labels: Optional labels for each result set
    """
    if labels is None:
        labels = [f"Config {i+1}" for i in range(len(results_files))]
    
    # Load all results
    all_results = []
    for file in results_files:
        with open(file, 'r') as f:
            results = json.load(f)
        all_results.append(results)
    
    # Extract statistics
    stats = []
    for results in all_results:
        team1_goals = [r['final_score']['team1'] for r in results]
        team2_goals = [r['final_score']['team2'] for r in results]
        team1_wins = sum(1 for r in results if r['final_score']['team1'] > r['final_score']['team2'])
        
        stats.append({
            'avg_goals_for': np.mean(team1_goals),
            'avg_goals_against': np.mean(team2_goals),
            'win_rate': team1_wins / len(results),
            'avg_shots': np.mean([r['team1_stats']['shots'] for r in results]),
            'avg_passes': np.mean([r['team1_stats']['passes'] for r in results]),
        })
    
    # Create comparison plots
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Win rate comparison
    ax = axes[0, 0]
    win_rates = [s['win_rate'] * 100 for s in stats]
    bars = ax.bar(labels, win_rates, color=['green' if wr > 50 else 'red' for wr in win_rates])
    ax.axhline(y=50, color='black', linestyle='--', linewidth=1, alpha=0.5)
    ax.set_ylabel('Win Rate (%)')
    ax.set_title('Win Rate Comparison', fontweight='bold')
    ax.set_ylim(0, 100)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
               f'{height:.1f}%', ha='center', va='bottom')
    
    # Goals comparison
    ax = axes[0, 1]
    x = np.arange(len(labels))
    width = 0.35
    ax.bar(x - width/2, [s['avg_goals_for'] for s in stats], 
           width, label='Goals For', color='green', alpha=0.7)
    ax.bar(x + width/2, [s['avg_goals_against'] for s in stats],
           width, label='Goals Against', color='red', alpha=0.7)
    ax.set_ylabel('Average Goals')
    ax.set_title('Goals Comparison', fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()
    
    # Shots comparison
    ax = axes[1, 0]
    shots = [s['avg_shots'] for s in stats]
    ax.bar(labels, shots, color='blue', alpha=0.7)
    ax.set_ylabel('Average Shots')
    ax.set_title('Shots Comparison', fontweight='bold')
    
    # Passes comparison
    ax = axes[1, 1]
    passes = [s['avg_passes'] for s in stats]
    ax.bar(labels, passes, color='purple', alpha=0.7)
    ax.set_ylabel('Average Passes')
    ax.set_title('Passes Comparison', fontweight='bold')
    
    plt.tight_layout()
    plt.show()


def visualize_tactics_heatmap(tactics_file: str):
    """
    Create a heatmap visualization of tactical parameters
    
    Args:
        tactics_file: Path to tactics JSON file
    """
    # Load tactics
    with open(tactics_file, 'r') as f:
        tactics_data = json.load(f)
    
    # Extract tactical parameters
    if 'tactics' in tactics_data:
        tactics = tactics_data['tactics']
    else:
        tactics = tactics_data
    
    # Organize parameters by category
    categories = {
        'Formation Behavior': [
            'formation_fuzziness',
            'formation_adherence_rate',
            'formation_elasticity',
            'formation_damping'
        ],
        'Defensive Tactics': [
            'defensive_line_adherence',
            'defensive_line_depth',
        ],
        'Offensive Tactics': [
            'forward_push_rate',
            'ball_attraction_strength',
            'ball_reaction_distance',
            'ball_close_distance',
        ],
        'Player Behavior': [
            'pass_propensity',
            'shoot_propensity',
            'pass_accuracy',
            'shot_accuracy',
            'pass_speed_factor',
            'shot_speed_factor',
        ]
    }
    
    # Create figure
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()
    
    for i, (category, params) in enumerate(categories.items()):
        ax = axes[i]
        
        # Get values (normalize distance parameters)
        values = []
        labels = []
        for param in params:
            if param in tactics:
                value = tactics[param]
                # Normalize distance parameters to 0-1 range
                if 'distance' in param:
                    value = value / 20.0  # Assuming max distance ~20
                values.append(value)
                # Format label
                label = param.replace('_', ' ').title()
                labels.append(label)
        
        # Create bar chart
        bars = ax.barh(labels, values, color='skyblue', edgecolor='black')
        
        # Color bars based on value
        for bar, value in zip(bars, values):
            if value > 0.7:
                bar.set_color('green')
                bar.set_alpha(0.7)
            elif value < 0.3:
                bar.set_color('red')
                bar.set_alpha(0.7)
            else:
                bar.set_color('yellow')
                bar.set_alpha(0.7)
        
        ax.set_xlim(0, 1.0)
        ax.set_xlabel('Value (normalized)', fontsize=10)
        ax.set_title(category, fontsize=12, fontweight='bold')
        ax.grid(axis='x', alpha=0.3)
        
        # Add value labels
        for bar, value in zip(bars, values):
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2,
                   f'{value:.2f}', ha='left', va='center', fontsize=9)
    
    plt.tight_layout()
    plt.show()


def main():
    """Example usage"""
    import sys
    
    if len(sys.argv) < 2:
        print("\nUsage: python visualize_optimization.py <command> [files...]")
        print("\nCommands:")
        print("  history <file>           - Plot optimization history")
        print("  formations <file1> <file2> - Compare two formations")
        print("  results <file1> [file2...] - Compare batch results")
        print("  tactics <file>           - Visualize tactical parameters")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'history' and len(sys.argv) >= 3:
        plot_optimization_history(sys.argv[2])
    
    elif command == 'formations' and len(sys.argv) >= 4:
        plot_formation_comparison(sys.argv[2], sys.argv[3])
    
    elif command == 'results' and len(sys.argv) >= 3:
        files = sys.argv[2:]
        labels = [f"Config {i+1}" for i in range(len(files))]
        compare_batch_results(files, labels)
    
    elif command == 'tactics' and len(sys.argv) >= 3:
        visualize_tactics_heatmap(sys.argv[2])
    
    else:
        print(f"Invalid command or missing files")


if __name__ == '__main__':
    main()

