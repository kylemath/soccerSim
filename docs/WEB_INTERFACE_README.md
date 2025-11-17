# Soccer Simulator Optimization Web Interface

A beautiful, interactive web interface for optimizing soccer team formations and tactics!

## 🚀 Quick Start

### Option 1: Using the startup script
```bash
cd /Users/kylemathewson/soccerSim
source venv/bin/activate
python start_optimizer.py
```

### Option 2: Direct launch
```bash
cd /Users/kylemathewson/soccerSim
source venv/bin/activate
python optimizer_app.py
```

Then open your browser and go to: **http://127.0.0.1:5001**

## ✨ Features

### 1. **Interactive Configuration**
- Configure Team 1 and Team 2 (Opponent) separately
- Choose from preset formations (2-3-1, 3-2-1, 2-2-2, 1-3-2)
- Adjust tactical parameters with sliders
- Visual formation preview

### 2. **Save & Load Configurations**
- Save your team configurations to JSON files
- Load previously saved configurations
- Browse saved configurations
- Share configurations with others

### 3. **Optimization**
- **Optimize Formation Only**: Find the best player positions
- **Optimize Tactics Only**: Find the best behavioral parameters
- **Optimize Both**: Complete optimization (slower but thorough)
- Real-time progress tracking
- Visual progress charts

### 4. **Comparison**
- Run batch comparisons between two teams
- Statistical analysis (win rate, goals, shots, passes)
- Side-by-side results

### 5. **Results & Analysis**
- View optimization history charts
- See best configurations found
- Compare team performances

## 📖 How to Use

### Step 1: Configure Teams

1. **Team 1 Tab**:
   - Select a formation preset or use custom
   - Adjust tactical parameters (sliders)
   - Formation is visualized in real-time

2. **Team 2 Tab** (Opponent):
   - Configure the opponent team
   - This is what Team 1 will be optimized against

### Step 2: Choose Optimization Mode

- **Formation Only**: Optimizes player positions
- **Tactics Only**: Optimizes behavioral parameters  
- **Both**: Optimizes everything (takes longer)

### Step 3: Set Optimization Parameters

- **Population Size**: Number of candidates per generation (10-100)
- **Generations**: Number of evolution cycles (5-100)
- **Games per Evaluation**: How many games to test each candidate (5-50)
- **Mutation Rate**: How often to mutate (0.05-0.3)
- **Mutation Strength**: How much to mutate (0.05-0.2)

### Step 4: Start Optimization

1. Click **"🚀 Start Optimization"**
2. Watch progress in the **Results & Analysis** tab
3. View charts showing fitness over generations
4. See the best configuration when done

### Step 5: Save Results

1. Click **"💾 Save Configuration"**
2. Enter a filename
3. Configuration saved to `saved_configs/` folder

### Step 6: Load Previous Configurations

1. Click **"📂 Load Configuration"**
2. Browse saved configurations
3. Click a file to load it

## 🎯 Use Cases

### Find the Best Formation

1. Set Team 1 to formation you want to optimize
2. Set Team 2 (opponent) to a challenging formation
3. Choose "Optimize Formation Only"
4. Run optimization
5. Best formation positions are saved

### Find the Best Tactics

1. Set Team 1 formation (keep it fixed)
2. Set opponent configuration
3. Choose "Optimize Tactics Only"
4. Run optimization
5. Best tactical parameters are found

### Complete Optimization

1. Set baseline configurations
2. Choose "Optimize Both"
3. Run optimization (this takes longer)
4. Get optimized formation AND tactics

### Compare Configurations

1. Configure both teams
2. Click **"⚖️ Compare Teams"**
3. Enter number of games (e.g., 50)
4. View statistical comparison

## 📁 File Structure

```
soccerSim/
├── optimizer_app.py          # Flask backend
├── templates/
│   └── optimizer.html        # Web interface
├── saved_configs/            # Saved configurations (auto-created)
│   └── *.json               # Your saved configs
└── start_optimizer.py        # Quick start script
```

## 🎨 Interface Overview

### Sidebar (Left)
- **Quick Actions**: Load defaults, save/load configs
- **Optimization Mode**: Choose what to optimize
- **Optimization Settings**: Adjust algorithm parameters
- **Status**: Real-time optimization progress

### Main Area (Right)
- **Team 1 Configuration**: Your team
- **Team 2 Configuration**: Opponent
- **Results & Analysis**: Charts and results

## 💾 Saved Files

All saved configurations are stored in `saved_configs/` folder as JSON files:

```json
{
  "team1": {
    "formation": {
      "name": "2-3-1",
      "positions": [[0.5, 0.05], ...]
    },
    "tactics": {
      "pass_propensity": 0.6,
      ...
    }
  },
  "team2": {...},
  "timestamp": "2025-01-31T12:00:00"
}
```

## 🔧 Troubleshooting

### Port Already in Use
If port 5001 is busy, edit `optimizer_app.py` and change the port:
```python
app.run(debug=True, host='127.0.0.1', port=5002)  # Change port
```

### CORS Errors
If you see CORS errors, install flask-cors:
```bash
pip install flask-cors
```

### Files Not Saving
Make sure `saved_configs/` directory exists (created automatically).

### Optimization Stuck
Check the browser console for errors. The optimization runs in the background - wait for it to complete.

## 🚀 Tips

1. **Start Small**: Use fewer games/generations for testing
2. **Save Often**: Save configurations as you experiment
3. **Compare First**: Run comparisons before full optimization
4. **Be Patient**: Optimization can take 10-60 minutes
5. **Check Results**: Always review the best configuration found

## 📊 Understanding Results

### Fitness Score
- **Higher is better**
- Formula: `win_rate × 100 + goal_difference × 10`
- Example: 70% win rate, +1.0 goal diff = 80.0 fitness

### Optimization Progress
- **Best Fitness**: Best performing candidate so far
- **Average Fitness**: Average of all candidates
- Rising trend = optimization is working
- Flat line = may need more generations

### Comparison Results
- **Win Rate**: Percentage of games won
- **Avg Goals**: Average goals scored per game
- **Std Goals**: Standard deviation (consistency)
- **Shots/Passes**: Offensive activity

## 🎓 Examples

### Example 1: Quick Test
1. Load defaults
2. Set 10 games, 5 generations
3. Optimize formation
4. Takes ~2 minutes

### Example 2: Thorough Search
1. Configure both teams carefully
2. Set 30 games, 30 generations
3. Optimize both
4. Takes ~30-60 minutes

### Example 3: Compare Two Strategies
1. Configure Team 1 with aggressive tactics
2. Configure Team 2 with defensive tactics
3. Run comparison with 100 games
4. See which strategy wins more

## 📝 Notes

- All optimizations run in the background
- You can close the browser - optimization continues
- Results are saved automatically when complete
- Use "Stop" button to cancel if needed
- Saved configurations are JSON - easy to edit manually

## 🆘 Support

If you encounter issues:
1. Check browser console (F12) for errors
2. Check server terminal for Python errors
3. Ensure all dependencies are installed
4. Try reloading the page
5. Restart the server

## 🎉 Enjoy!

Have fun optimizing your soccer teams! The web interface makes it easy to experiment with different configurations and find the best strategies.

