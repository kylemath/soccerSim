# Soccer Simulator Optimization Guide

This guide explains how to use the soccer simulator to run many games without visualization and optimize formations and tactics.

## Overview

The optimization system consists of several key components:

1. **Fixed Parameters** - Common parameters for all teams (field size, physics, etc.)
2. **Formation Parameters** - Player positions that can be optimized
3. **Tactical Parameters** - Behavioral parameters that can be optimized
4. **Batch Simulator** - Run many games without visualization
5. **Genetic Optimizer** - Optimize formations and tactics using evolutionary algorithms

## Quick Start

### 1. Run a Quick Optimization Test

```bash
python optimize_example.py quick
```

This will run a quick optimization with fewer games and generations (~2-3 minutes).

### 2. Compare Baseline Formations

```bash
python optimize_example.py 1
```

This compares different standard formations (2-3-1, 3-2-1, 2-2-2, 1-3-2) to see which performs best.

### 3. Optimize a Formation

```bash
python optimize_example.py 2
```

This optimizes player positions to beat a specific opponent formation.

### 4. Optimize Tactics

```bash
python optimize_example.py 3
```

This optimizes tactical parameters (passing, shooting, positioning) for a fixed formation.

### 5. Optimize Both Formation and Tactics

```bash
python optimize_example.py 4
```

This optimizes both formation and tactics simultaneously.

## Detailed Usage

### Parameter Configuration

#### Fixed Parameters (parameter_config.py)

These parameters are common to all teams and don't change:
- Field dimensions (40m x 30m)
- Player physics (speed, acceleration)
- Ball physics (friction, mass)
- Game duration

Example:
```python
from parameter_config import FixedParameters

fixed_params = FixedParameters(
    field_length=40.0,
    field_width=30.0,
    game_duration_seconds=120  # 2 minutes
)
```

#### Formation Parameters

Define where players are positioned on the field (normalized 0-1 coordinates):

```python
from parameter_config import FormationParameters, FormationPresets

# Use a preset formation
formation = FormationPresets.get_formation_2_3_1()

# Or create a custom formation
custom_formation = FormationParameters(
    name="Custom",
    positions=[
        (0.5, 0.05),   # Goalkeeper
        (0.3, 0.2),    # Defender 1
        (0.7, 0.2),    # Defender 2
        (0.2, 0.5),    # Midfielder 1
        (0.5, 0.5),    # Midfielder 2
        (0.8, 0.5),    # Midfielder 3
        (0.5, 0.75),   # Forward
    ]
)
```

#### Tactical Parameters

Define how players behave:

```python
from parameter_config import TacticalParameters

tactics = TacticalParameters(
    # Formation adherence
    formation_fuzziness=0.5,           # How much players deviate
    formation_adherence_rate=0.6,      # How quickly they return
    
    # Defensive tactics
    defensive_line_adherence=0.8,      # How tight the defense stays
    defensive_line_depth=0.15,         # How deep defenders sit
    
    # Offensive tactics
    forward_push_rate=0.6,             # How aggressive forwards are
    ball_attraction_strength=0.8,      # Ball vs formation priority
    
    # Player behavior
    pass_propensity=0.6,               # Passing tendency
    shoot_propensity=0.3,              # Shooting tendency
    pass_accuracy=0.8,                 # Pass accuracy (0-1)
    shot_accuracy=0.4,                 # Shot accuracy (0-1)
)
```

### Batch Simulation

Run many games without visualization:

```python
from batch_simulator import BatchSimulator
from parameter_config import TeamConfiguration, FormationPresets, TacticalParameters

# Create team configurations
formation1 = FormationPresets.get_formation_2_3_1()
formation2 = FormationPresets.get_formation_3_2_1()
tactics = TacticalParameters()

team1 = TeamConfiguration(formation1, tactics, team_id=0)
team2 = TeamConfiguration(formation2, tactics, team_id=1)

# Run batch simulation
simulator = BatchSimulator()
results = simulator.run_games(
    team1, 
    team2, 
    num_games=100,
    parallel=True,  # Use multiprocessing
    verbose=True
)

# Analyze results
analysis = simulator.analyze_results(results)
simulator.print_analysis(analysis)

# Save results
simulator.save_results(results, "my_results.json")
```

### Comparing Configurations

#### Compare Formations

```python
from batch_simulator import compare_formations
from parameter_config import FormationPresets, TacticalParameters

formation1 = FormationPresets.get_formation_2_3_1()
formation2 = FormationPresets.get_formation_3_2_1()
tactics = TacticalParameters()

analysis = compare_formations(
    formation1,
    formation2,
    tactics,
    num_games=50,
    verbose=True
)
```

#### Compare Tactics

```python
from batch_simulator import compare_tactics
from parameter_config import FormationPresets, TacticalParameters

formation = FormationPresets.get_formation_2_3_1()

tactics1 = TacticalParameters(pass_propensity=0.7)  # More passing
tactics2 = TacticalParameters(shoot_propensity=0.5) # More shooting

analysis = compare_tactics(
    formation,
    tactics1,
    tactics2,
    num_games=50,
    verbose=True
)
```

### Optimization

#### Optimize Formation

```python
from optimizer import GeneticOptimizer, FitnessEvaluator
from parameter_config import (
    TeamConfiguration, 
    FormationPresets, 
    TacticalParameters
)

# Define opponent
opponent_formation = FormationPresets.get_formation_3_2_1()
opponent_tactics = TacticalParameters()
opponent_config = TeamConfiguration(opponent_formation, opponent_tactics, team_id=1)

# Create evaluator
evaluator = FitnessEvaluator(
    opponent_config,
    num_games=20  # Games per fitness evaluation
)

# Create optimizer
optimizer = GeneticOptimizer(
    population_size=30,      # Number of candidates per generation
    mutation_rate=0.15,      # Probability of mutation
    mutation_strength=0.1,   # How much to mutate
    crossover_rate=0.7,      # Probability of crossover
    elite_fraction=0.1       # Top % to preserve
)

# Optimize
base_formation = FormationPresets.get_formation_2_3_1()
base_tactics = TacticalParameters()

best_formation, best_fitness, history = optimizer.optimize_formation(
    base_formation,
    base_tactics,
    evaluator,
    generations=30,
    verbose=True
)

# Save results
optimizer.save_best("best_formation.json")
optimizer.save_history("optimization_history.json")
```

#### Optimize Tactics

```python
# Similar to above, but optimize tactics instead
best_tactics, best_fitness, history = optimizer.optimize_tactics(
    formation,
    base_tactics,
    evaluator,
    generations=30,
    verbose=True
)
```

#### Optimize Both

```python
# Optimize formation and tactics simultaneously
best_config, best_fitness, history = optimizer.optimize_both(
    base_formation,
    base_tactics,
    evaluator,
    generations=30,
    verbose=True
)
```

## Understanding the Optimizer

### Genetic Algorithm Process

1. **Initialize Population**: Create random variations of the base configuration
2. **Evaluate Fitness**: Run games to measure performance
3. **Selection**: Select best performers
4. **Crossover**: Combine features from two parents
5. **Mutation**: Random changes to create diversity
6. **Repeat**: Iterate for multiple generations

### Fitness Function

The fitness score is calculated as:
```
fitness = win_rate * 100 + goal_difference * 10
```

Where:
- `win_rate` = wins / total_games
- `goal_difference` = avg_goals_for - avg_goals_against

Higher fitness = better performance

### Optimization Parameters

**Population Size**: 
- Larger = more diversity, slower
- Recommended: 20-50

**Mutation Rate**:
- Higher = more exploration, less stability
- Recommended: 0.10-0.20

**Mutation Strength**:
- How much parameters change when mutated
- Recommended: 0.05-0.15

**Crossover Rate**:
- Probability of combining two parents
- Recommended: 0.6-0.8

**Generations**:
- More generations = better results, longer time
- Recommended: 20-50 for good results

**Games per Evaluation**:
- More games = more accurate fitness, slower
- Recommended: 15-30

## Performance Tips

1. **Use Parallel Processing**: Set `parallel=True` in batch simulations
2. **Start Small**: Test with fewer games/generations first
3. **Use Quick Example**: Run `python optimize_example.py quick` to test
4. **Save Progress**: Optimizer saves best results and history
5. **Shorter Games**: Reduce game duration in FixedParameters for faster testing

## Example Workflow

### Phase 1: Identify Fixed Parameters

Run baseline tests to determine what parameters should stay fixed:

```bash
python optimize_example.py 1
```

Review results and decide on fixed parameters (field size, physics constants, etc.)

### Phase 2: Test Formation Variations

Optimize formations against different opponent styles:

```bash
python optimize_example.py 2
```

### Phase 3: Optimize Tactics

For each promising formation, optimize tactical parameters:

```bash
python optimize_example.py 3
```

### Phase 4: Combined Optimization

Optimize both formation and tactics together:

```bash
python optimize_example.py 4
```

### Phase 5: Validation

Validate the best configuration with extensive testing:

```bash
python optimize_example.py 5
```

## Time Estimates

These are rough estimates on a modern laptop (8 cores):

- **Quick example**: 2-3 minutes
- **Step 1 (Compare formations)**: 5-10 minutes
- **Step 2 (Optimize formation)**: 15-30 minutes
- **Step 3 (Optimize tactics)**: 15-30 minutes
- **Step 4 (Optimize both)**: 30-60 minutes
- **Step 5 (Validation)**: 5-10 minutes
- **Full pipeline**: 1-2 hours

## Output Files

The optimizer creates several output files:

- `best_formation_TIMESTAMP.json` - Best formation found
- `best_tactics_TIMESTAMP.json` - Best tactics found
- `best_config_TIMESTAMP.json` - Best combined configuration
- `*_history_TIMESTAMP.json` - Optimization progress over generations
- `validation_results_TIMESTAMP.json` - Detailed game results

## Customization

### Create Custom Fitness Function

```python
def custom_fitness(team1_config, team2_config):
    # Your custom evaluation logic
    # Return higher values for better performance
    pass

evaluator.evaluate_formation = custom_fitness
```

### Adjust Optimization Strategy

```python
optimizer = GeneticOptimizer(
    population_size=50,        # Increase for more diversity
    mutation_rate=0.2,         # Increase for more exploration
    mutation_strength=0.15,    # Increase for bigger changes
    crossover_rate=0.8,        # Increase for more mixing
    elite_fraction=0.15        # Increase to preserve more elites
)
```

## Troubleshooting

**Optimization converges too quickly**:
- Increase mutation rate and strength
- Increase population size
- Decrease elite fraction

**Results are unstable**:
- Increase games per evaluation
- Decrease mutation rate
- Increase elite fraction

**Optimization is too slow**:
- Decrease games per evaluation
- Decrease population size
- Decrease generations
- Use parallel processing

**Out of memory**:
- Decrease population size
- Run games sequentially (`parallel=False`)

## Next Steps

1. Run the quick example to understand the system
2. Compare baseline formations to find good starting points
3. Optimize against different opponent strategies
4. Create custom fitness functions for specific objectives
5. Experiment with different optimization parameters

For questions or issues, refer to the code documentation in:
- `parameter_config.py`
- `batch_simulator.py`
- `optimizer.py`
- `optimize_example.py`

