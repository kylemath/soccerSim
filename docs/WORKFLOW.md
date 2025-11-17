# Soccer Simulator Optimization Workflow

## Complete Workflow Diagram

```
┌────────────────────────────────────────────────────────────────┐
│                    STEP 1: DEFINE PARAMETERS                   │
│────────────────────────────────────────────────────────────────│
│                                                                 │
│  Fixed Parameters          Optimizable Parameters              │
│  ┌──────────────┐         ┌──────────────┬──────────────┐     │
│  │ Field: 40×30m│         │  Formation   │   Tactics    │     │
│  │ Physics      │         │  ┌────────┐  │  ┌────────┐  │     │
│  │ Rules        │         │  │ 7 pos. │  │  │16 params│  │     │
│  └──────────────┘         │  └────────┘  │  └────────┘  │     │
│                           └──────────────┴──────────────┘     │
└────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌────────────────────────────────────────────────────────────────┐
│                   STEP 2: BATCH SIMULATION                     │
│────────────────────────────────────────────────────────────────│
│                                                                 │
│  Run N games without visualization                             │
│                                                                 │
│  Game 1  Game 2  Game 3  ...  Game N                           │
│    ║       ║       ║            ║                              │
│    ▼       ▼       ▼            ▼                              │
│  Result Result Result  ...  Result                             │
│                                                                 │
│  ┌──────────────────────────────────┐                          │
│  │  Statistical Analysis             │                          │
│  │  - Win rate                       │                          │
│  │  - Goals for/against              │                          │
│  │  - Shots, passes, possession      │                          │
│  └──────────────────────────────────┘                          │
│                                                                 │
│  Fitness = Win_Rate × 100 + Goal_Diff × 10                     │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌────────────────────────────────────────────────────────────────┐
│                 STEP 3: GENETIC OPTIMIZATION                   │
│────────────────────────────────────────────────────────────────│
│                                                                 │
│  Generation 0: Initialize Population                           │
│  ┌────┐ ┌────┐ ┌────┐ ┌────┐ ... ┌────┐                       │
│  │Ind1│ │Ind2│ │Ind3│ │Ind4│     │IndN│                       │
│  └────┘ └────┘ └────┘ └────┘     └────┘                       │
│    │      │      │      │           │                          │
│    └──────┴──────┴──────┴───────────┘                          │
│                  │                                              │
│                  ▼                                              │
│  ┌────────────────────────────────────┐                        │
│  │  Evaluate Fitness (run games)      │                        │
│  │  Fitness: [F1, F2, F3, ..., FN]    │                        │
│  └────────────────────────────────────┘                        │
│                  │                                              │
│                  ▼                                              │
│  ┌────────────────────────────────────┐                        │
│  │  Selection (Tournament)            │                        │
│  │  Select best performers as parents │                        │
│  └────────────────────────────────────┘                        │
│                  │                                              │
│     ┌────────────┴────────────┐                                │
│     ▼                          ▼                                │
│  Parent 1                  Parent 2                            │
│     │                          │                                │
│     └──────────┬───────────────┘                               │
│                ▼                                                │
│  ┌────────────────────────────────────┐                        │
│  │  Crossover (mix features)          │                        │
│  └────────────────────────────────────┘                        │
│                │                                                │
│                ▼                                                │
│  ┌────────────────────────────────────┐                        │
│  │  Mutation (random changes)         │                        │
│  └────────────────────────────────────┘                        │
│                │                                                │
│                ▼                                                │
│  Generation 1: New Population                                  │
│  ┌────┐ ┌────┐ ┌────┐ ┌────┐ ... ┌────┐                       │
│  │Ind1│ │Ind2│ │Ind3│ │Ind4│     │IndN│                       │
│  └────┘ └────┘ └────┘ └────┘     └────┘                       │
│                │                                                │
│                ▼                                                │
│  Repeat for N generations...                                   │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌────────────────────────────────────────────────────────────────┐
│                   STEP 4: VALIDATION                           │
│────────────────────────────────────────────────────────────────│
│                                                                 │
│  Best Configuration Found!                                     │
│                                                                 │
│  Run 100+ validation games                                     │
│  ┌──────────────────────────────────┐                          │
│  │  Confirm performance              │                          │
│  │  - Win rate: 78%                  │                          │
│  │  - Goals: 2.8 vs 1.2              │                          │
│  │  - Consistent results             │                          │
│  └──────────────────────────────────┘                          │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

## Detailed Step-by-Step Process

### Phase 1: Setup (1 minute)

```bash
# 1. Activate environment
source venv/bin/activate

# 2. Choose what to optimize
#    - Formations only
#    - Tactics only
#    - Both together
```

### Phase 2: Baseline Comparison (5-10 minutes)

```bash
# Compare standard formations
python optimize_example.py 1
```

**What happens:**
1. Creates 4 standard formations (2-3-1, 3-2-1, 2-2-2, 1-3-2)
2. Runs each vs baseline (50 games each)
3. Shows which formation performs best
4. Use best as starting point

**Output:**
```
--- Testing 3-2-1 vs 2-3-1 ---
Running 50 games...
Completed 50 games in 5.2 seconds

Team 1 Performance:
  Wins: 28 (56.0%)
  Avg Goals: 1.84 ± 0.92
```

### Phase 3: Formation Optimization (15-30 minutes)

```bash
# Optimize formation against opponent
python optimize_example.py 2
```

**What happens:**
1. Initialize population (30 formation variations)
2. For each generation (20-30 times):
   - Evaluate each formation (20 games)
   - Select best performers
   - Create next generation (crossover + mutation)
3. Save best formation found

**Output:**
```
Generation 1/30: Best=113.00, Avg=64.13, Time=60.1s
Generation 2/30: Best=123.00, Avg=71.20, Time=59.8s
...
Generation 30/30: Best=156.00, Avg=142.47, Time=59.6s

Best fitness: 156.00
Saved to: best_formation_20251031_143022.json
```

### Phase 4: Tactics Optimization (15-30 minutes)

```bash
# Optimize tactics for best formation
python optimize_example.py 3
```

**What happens:**
1. Use best formation from Phase 3
2. Initialize population (30 tactical variations)
3. For each generation (20-30 times):
   - Evaluate each tactic set (20 games)
   - Select best performers
   - Create next generation
4. Save best tactics found

**Output:**
```
Generation 1/30: Best=118.00, Avg=72.13, Time=58.3s
...
Generation 30/30: Best=168.00, Avg=148.22, Time=58.1s

Best Tactical Parameters:
  pass_propensity: 0.682
  shot_accuracy: 0.473
  ball_attraction_strength: 0.847
  ...
```

### Phase 5: Combined Optimization (30-60 minutes)

```bash
# Optimize formation AND tactics together
python optimize_example.py 4
```

**What happens:**
1. Initialize population (25 complete configurations)
2. For each generation (15-30 times):
   - Evaluate each config (15 games)
   - Select best performers
   - Create next generation (crossover both formation and tactics)
3. Save best complete configuration

**Output:**
```
Generation 1/30: Best=121.00, Avg=68.45, Time=73.2s
...
Generation 30/30: Best=172.00, Avg=155.33, Time=72.8s

Best fitness: 172.00
Saved to: best_config_20251031_150522.json
```

### Phase 6: Validation (5-10 minutes)

```bash
# Validate optimized configuration
python optimize_example.py 5
```

**What happens:**
1. Load best configuration
2. Run 100+ games vs baseline
3. Statistical analysis
4. Confirm performance is consistent

**Output:**
```
Running 100 validation games...
Completed 100 games in 10.3 seconds

=== BATCH SIMULATION RESULTS ===
Total Games: 100

Team 1 Performance:
  Wins: 78 (78.0%)
  Avg Goals: 2.81 ± 1.15
  Avg Shots: 9.2
  Avg Passes: 26.4
  Avg Possession: 74.3s

Team 2 Performance:
  Wins: 18 (18.0%)
  Avg Goals: 1.23 ± 0.89

Draws: 4 (4.0%)
```

## Quick Workflow (Testing)

For quick testing during development:

```bash
# 1. Quick optimization test (3 minutes)
python optimize_example.py quick

# 2. Test specific configuration
python -c "
from parameter_config import *
from batch_simulator import *

team1 = TeamConfiguration(
    FormationPresets.get_formation_2_3_1(),
    TacticalParameters(),
    team_id=0
)
team2 = TeamConfiguration(
    FormationPresets.get_formation_3_2_1(),
    TacticalParameters(),
    team_id=1
)

simulator = BatchSimulator()
results = simulator.run_games(team1, team2, num_games=20)
analysis = simulator.analyze_results(results)
simulator.print_analysis(analysis)
"
```

## Custom Workflow Example

```python
# custom_optimization.py

from parameter_config import (
    FixedParameters, 
    FormationPresets, 
    TacticalParameters,
    TeamConfiguration
)
from optimizer import GeneticOptimizer, FitnessEvaluator

# 1. Define fixed parameters
fixed_params = FixedParameters(
    game_duration_seconds=120  # 2 minutes
)

# 2. Create baseline configuration
base_formation = FormationPresets.get_formation_2_3_1()
base_tactics = TacticalParameters()

# 3. Define opponent
opponent_formation = FormationPresets.get_formation_3_2_1()
opponent_tactics = TacticalParameters(
    defensive_line_adherence=0.9,  # Very defensive
    pass_propensity=0.7            # Lots of passing
)
opponent = TeamConfiguration(opponent_formation, opponent_tactics, team_id=1)

# 4. Create evaluator
evaluator = FitnessEvaluator(
    opponent_config=opponent,
    num_games=20,
    fixed_params=fixed_params
)

# 5. Create optimizer
optimizer = GeneticOptimizer(
    population_size=30,
    mutation_rate=0.15,
    mutation_strength=0.1,
    crossover_rate=0.7
)

# 6. Run optimization
print("Optimizing formation...")
best_formation, fitness, history = optimizer.optimize_formation(
    base_formation,
    base_tactics,
    evaluator,
    generations=30,
    verbose=True
)

print(f"\nBest formation fitness: {fitness:.2f}")
optimizer.save_best("my_best_formation.json")
optimizer.save_history("my_optimization_history.json")

# 7. Visualize results
import matplotlib.pyplot as plt

gens = [h['generation'] for h in history]
best = [h['best_fitness'] for h in history]
avg = [h['avg_fitness'] for h in history]

plt.figure(figsize=(10, 6))
plt.plot(gens, best, 'g-', label='Best', linewidth=2)
plt.plot(gens, avg, 'b-', label='Average', linewidth=2)
plt.xlabel('Generation')
plt.ylabel('Fitness')
plt.title('Optimization Progress')
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig('my_optimization_progress.png')
print("Progress plot saved to my_optimization_progress.png")
```

## Parallel vs Sequential

### Parallel (Default)
```python
results = simulator.run_games(
    team1, team2,
    num_games=100,
    parallel=True  # Use all CPU cores
)
# Time: ~10 seconds
```

### Sequential
```python
results = simulator.run_games(
    team1, team2,
    num_games=100,
    parallel=False  # One at a time
)
# Time: ~60 seconds
```

## Parameter Tuning Guide

### For Faster Results (Testing)
```python
# Reduce games per evaluation
evaluator = FitnessEvaluator(opponent, num_games=10)  # Instead of 20

# Smaller population
optimizer = GeneticOptimizer(population_size=15)  # Instead of 30

# Fewer generations
optimizer.optimize_formation(..., generations=10)  # Instead of 30
```

### For Better Results (Production)
```python
# More games per evaluation
evaluator = FitnessEvaluator(opponent, num_games=30)  # More accurate

# Larger population
optimizer = GeneticOptimizer(population_size=50)  # More diversity

# More generations
optimizer.optimize_formation(..., generations=50)  # Better convergence
```

### For Exploration
```python
# Higher mutation
optimizer = GeneticOptimizer(
    mutation_rate=0.25,      # More exploration
    mutation_strength=0.15   # Bigger changes
)
```

### For Stability
```python
# Lower mutation
optimizer = GeneticOptimizer(
    mutation_rate=0.10,      # Less exploration
    mutation_strength=0.05,  # Smaller changes
    elite_fraction=0.2       # Preserve more elites
)
```

## Time Estimates by Configuration

| Configuration | Games/Eval | Population | Generations | Time |
|--------------|------------|------------|-------------|------|
| Quick Test   | 10         | 15         | 5           | 3 min |
| Fast         | 15         | 20         | 15          | 10 min |
| Balanced     | 20         | 30         | 30          | 30 min |
| Thorough     | 30         | 40         | 40          | 90 min |
| Exhaustive   | 50         | 50         | 50          | 3 hours |

## Summary

The workflow is:
1. **Define** parameters (fixed vs optimizable)
2. **Compare** baseline configurations
3. **Optimize** formations
4. **Optimize** tactics
5. **Validate** results

You can run the entire pipeline with:
```bash
python optimize_example.py all
```

Or run individual steps as needed!

