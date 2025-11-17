# 7x7 Indoor Soccer Formation Evolution Simulator

A physics-based soccer simulation system for testing and evolving formations for 7x7 u13 indoor soccer. The simulator uses a pinball-style physics engine to rapidly test formations without full-scale soccer simulation.

## Features

- **Pinball-style physics**: Fast, simplified physics simulation focusing on ball movement, speed, and acceleration
- **Player behaviors**: Players have propensities to pass, shoot, or deflect the ball with random variation
- **Fuzzy formations**: Players adhere to formations with tunable randomness and fuzzy boundaries
- **Four game phases**: Tracks formation adherence across different phases of the game
- **Realistic dimensions**: Field size matches half FIFA field (touchline to touchline) for 7x7 u13 soccer
- **Visualization**: HTML-based visualization with real-time charts for passes, possession, shots, and goals
- **Database storage**: Games are stored in SQLite database for analysis and evolution
- **Formation evolution**: Framework ready for RL/genetic algorithm optimization

## Setup

1. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the visualization server:
```bash
python app.py
```

4. Open your browser to `http://localhost:5000`

## Configuration

Edit `config.py` to adjust:
- Field dimensions
- Player and ball properties
- Behavior propensities (pass, shoot, deflect)
- Formation fuzziness and adherence rates
- Physics parameters (friction, bounce damping)
- Game duration and simulation speed

## Project Structure

- `config.py` - Configuration parameters
- `physics.py` - Ball physics engine
- `player.py` - Player entities with behaviors
- `formation.py` - Formation system with evolution capabilities
- `game.py` - Game simulation logic
- `simulator.py` - Main simulator interface
- `database.py` - Database models for storing games
- `app.py` - Flask web server for visualization

## Usage

### Running a Single Game

```python
from simulator import Simulator
from formation import FormationLibrary

simulator = Simulator()
team1_formation = FormationLibrary.get_formation('2-3-1')
team2_formation = FormationLibrary.get_formation('3-2-1')

result = simulator.run_game(team1_formation, team2_formation)
print(result['final_stats'])
```

### Saving Games to Database

```python
result = simulator.run_and_save_game(team1_formation, team2_formation)
print(f"Game saved with ID: {result['final_stats']['db_id']}")
```

## Formation Evolution (Coming Soon)

The system is designed to support evolutionary algorithms and reinforcement learning for optimizing formations. The `Formation` class includes `mutate()` and `crossover()` methods ready for genetic algorithms.

## Game Statistics Tracked

- Goals for/against
- Passes completed
- Shots taken
- Possession time
- Player touches
- Ball position and speed over time

## Next Steps

1. Implement evolution/RL algorithm for formation optimization
2. Scale up to run many games against different formation opponents
3. Analyze formation adherence across game phases
4. Optimize formations based on win rates and statistics

