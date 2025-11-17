# Quick Start Guide - Soccer Simulator Optimization

## What You Can Do

1. **Run many games without visualization** - Fast batch simulations
2. **Define fixed parameters** - Common settings for all teams
3. **Optimize formations** - Find the best player positions
4. **Optimize tactics** - Find the best behavioral parameters
5. **Compare configurations** - Test different strategies head-to-head

## Installation

Your environment is already set up! Just activate it:

```bash
cd /Users/kylemathewson/soccerSim
source venv/bin/activate
```

## Quick Test (3 minutes)

Run a quick optimization to see it in action:

```bash
python optimize_example.py quick
```

This will:
- Create a population of formation variations
- Run games to evaluate each one
- Evolve better formations over 5 generations
- Show you the best result

## Main Commands

### 1. Compare Different Formations

```bash
python optimize_example.py 1
```

Tests different standard formations (2-3-1, 3-2-1, 2-2-2, 1-3-2) to see which works best.

### 2. Optimize a Formation

```bash
python optimize_example.py 2
```

Takes a formation and evolves it to beat a specific opponent.

### 3. Optimize Tactics

```bash
python optimize_example.py 3
```

Optimizes how players behave (passing, shooting, positioning).

### 4. Optimize Both

```bash
python optimize_example.py 4
```

Optimizes formation AND tactics together.

### 5. Validate Results

```bash
python optimize_example.py 5
```

Runs many games to confirm the optimized configuration works well.

### Run Everything

```bash
python optimize_example.py all
```

Runs the complete optimization pipeline (takes 1-2 hours).

## Simple Custom Example

Create a file `my_optimization.py`:

```python
from parameter_config import FormationPresets, TacticalParameters, TeamConfiguration
from batch_simulator import BatchSimulator

# Create two team configurations
formation1 = FormationPresets.get_formation_2_3_1()
formation2 = FormationPresets.get_formation_3_2_1()
tactics = TacticalParameters()

team1 = TeamConfiguration(formation1, tactics, team_id=0)
team2 = TeamConfiguration(formation2, tactics, team_id=1)

# Run 50 games
simulator = BatchSimulator()
results = simulator.run_games(team1, team2, num_games=50, parallel=True)

# See the results
analysis = simulator.analyze_results(results)
simulator.print_analysis(analysis)
```

Then run it:

```bash
python my_optimization.py
```

## Key Files

- `parameter_config.py` - Define fixed and optimizable parameters
- `batch_simulator.py` - Run many games without visualization
- `optimizer.py` - Genetic algorithm for optimization
- `optimize_example.py` - Complete examples
- `visualize_optimization.py` - Plot results

## Understanding Parameters

### Fixed Parameters (Don't Change)

These are the same for all teams:
- Field size: 40m x 30m
- Player speed: 5 m/s max
- Ball physics
- Game duration: 2 minutes (for testing)

### Formation Parameters (Optimize These)

Where players are positioned:
- 7 players: 1 GK + 6 field players
- Positions as (x, y) coordinates
- Normalized to 0-1 scale

Example formations:
- **2-3-1**: Balanced (2 defenders, 3 midfielders, 1 forward)
- **3-2-1**: Defensive (3 defenders, 2 midfielders, 1 forward)
- **2-2-2**: Aggressive (2 defenders, 2 midfielders, 2 forwards)
- **1-3-2**: Control (1 defender, 3 midfielders, 2 forwards)

### Tactical Parameters (Optimize These)

How players behave:
- **pass_propensity**: How often they pass vs shoot (0-1)
- **shot_accuracy**: How accurate shots are (0-1)
- **ball_attraction_strength**: Chase ball vs stay in formation (0-1)
- **defensive_line_adherence**: How tight defense stays (0-1)
- And 12 more parameters...

## Optimization Process

The genetic algorithm works like evolution:

1. **Generation 0**: Create random variations
2. **Evaluate**: Run games to measure fitness
3. **Select**: Keep the best performers
4. **Breed**: Mix features from top performers
5. **Mutate**: Add random changes
6. **Repeat**: Go back to step 2

After 20-50 generations, you get an optimized configuration!

## Example Output

```
Generation 1/20: Best=113.00, Avg=64.13, Time=60.1s
Generation 2/20: Best=123.00, Avg=71.20, Time=59.8s
...
Generation 20/20: Best=156.00, Avg=128.47, Time=59.6s

Optimization completed in 1200.5 seconds
Best fitness: 156.00

=== BATCH SIMULATION RESULTS ===
Total Games: 100
Team 1 Performance:
  Wins: 68 (68.0%)
  Avg Goals: 2.34 ± 1.12
  Avg Shots: 8.5
  Avg Passes: 24.3
```

## Tips

1. **Start small**: Use `quick` example first
2. **Be patient**: Full optimization takes time
3. **Save results**: All results are automatically saved
4. **Parallel processing**: Enabled by default for speed
5. **Adjust game duration**: Edit `FixedParameters.game_duration_seconds` for faster testing

## What's Being Optimized?

The fitness function is:
```
fitness = win_rate × 100 + goal_difference × 10
```

So a team that:
- Wins 70% of games
- Scores 2.5 goals/game on average
- Concedes 1.5 goals/game

Gets fitness = 70 + (2.5-1.5)×10 = **80.0**

Higher fitness = better team!

## Next Steps

1. Run `python optimize_example.py quick` to see it work
2. Try comparing formations with step 1
3. Read `OPTIMIZATION_GUIDE.md` for detailed documentation
4. Experiment with custom configurations
5. Visualize results with `visualize_optimization.py`

## Need Help?

- Full guide: `OPTIMIZATION_GUIDE.md`
- Code examples: `optimize_example.py`
- Parameters reference: `parameter_config.py`
- Simulator details: `batch_simulator.py`

## File Structure

```
soccerSim/
├── parameter_config.py      # Parameter definitions
├── batch_simulator.py       # Batch simulation engine
├── optimizer.py             # Genetic algorithm optimizer
├── optimize_example.py      # Example workflows
├── visualize_optimization.py # Visualization tools
├── QUICK_START.md          # This file
└── OPTIMIZATION_GUIDE.md   # Detailed guide
```

Have fun optimizing! 🏆⚽

