"""
Flask app for serving HTML visualization
"""

from flask import Flask, render_template_string, jsonify, request
from simulator import Simulator
from formation import FormationLibrary
import config
import json

app = Flask(__name__)
simulator = Simulator()


HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>7x7 Soccer Simulation</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
            overflow-x: hidden;
        }
        .main-container {
            display: flex;
            min-height: 100vh;
        }
        .content {
            flex: 1;
            padding: 20px;
            max-width: 1200px;
        }
        .container {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
            margin-top: 0;
        }
        .controls {
            margin: 20px 0;
            text-align: center;
        }
        button {
            padding: 10px 20px;
            margin: 5px;
            font-size: 16px;
            cursor: pointer;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
        }
        button:hover {
            background-color: #45a049;
        }
        button:disabled {
            background-color: #cccccc;
            cursor: not-allowed;
        }
        .field-container {
            margin: 20px 0;
            border: 2px solid #333;
            background-color: #2d5016;
            position: relative;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .stat-card {
            background: #f9f9f9;
            padding: 15px;
            border-radius: 4px;
            border-left: 4px solid #4CAF50;
        }
        .stat-title {
            font-weight: bold;
            color: #666;
            margin-bottom: 10px;
        }
        .stat-value {
            font-size: 24px;
            color: #333;
        }
        
        /* Parameters Sidebar */
        .params-sidebar {
            width: 320px;
            background: white;
            border-left: 1px solid #ddd;
            overflow-y: auto;
            box-shadow: -2px 0 4px rgba(0,0,0,0.1);
            position: sticky;
            top: 0;
            height: 100vh;
        }
        .params-header {
            padding: 15px;
            background: #4CAF50;
            color: white;
            font-weight: bold;
            font-size: 16px;
            position: sticky;
            top: 0;
            z-index: 10;
        }
        .param-category {
            border-bottom: 1px solid #eee;
        }
        .category-header {
            padding: 12px 15px;
            background: #f5f5f5;
            font-weight: bold;
            font-size: 13px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            user-select: none;
        }
        .category-header:hover {
            background: #e8e8e8;
        }
        .category-toggle {
            font-size: 12px;
        }
        .category-content {
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease;
        }
        .category-content.open {
            max-height: 2000px;
        }
        .param-item {
            padding: 8px 15px;
            border-bottom: 1px solid #f5f5f5;
        }
        .param-label {
            font-size: 11px;
            color: #666;
            margin-bottom: 4px;
            display: flex;
            justify-content: space-between;
        }
        .param-name {
            font-weight: 500;
        }
        .param-value {
            color: #4CAF50;
            font-weight: bold;
        }
        .param-slider {
            width: 100%;
            height: 4px;
            border-radius: 2px;
            background: #ddd;
            outline: none;
            -webkit-appearance: none;
        }
        .param-slider::-webkit-slider-thumb {
            -webkit-appearance: none;
            appearance: none;
            width: 14px;
            height: 14px;
            border-radius: 50%;
            background: #4CAF50;
            cursor: pointer;
        }
        .param-slider::-moz-range-thumb {
            width: 14px;
            height: 14px;
            border-radius: 50%;
            background: #4CAF50;
            cursor: pointer;
            border: none;
        }
        .reset-btn {
            width: calc(100% - 30px);
            margin: 15px;
            padding: 8px;
            font-size: 13px;
            background: #ff9800;
        }
        .reset-btn:hover {
            background: #f57c00;
        }
    </style>
</head>
<body>
    <div class="main-container">
        <div class="content">
            <div class="container">
                <h1>7x7 Indoor Soccer Simulation</h1>
                
                <div class="controls">
            <button id="startBtn" onclick="startSimulation()">Start Simulation</button>
            <button id="pauseBtn" onclick="pauseSimulation()" disabled>Pause</button>
            <button id="resetBtn" onclick="resetSimulation()">Reset</button>
            <label>
                Speed: <input type="range" id="speedSlider" min="1" max="50" value="10" oninput="updateSpeed()">
                <span id="speedValue">10x</span>
            </label>
        </div>
        
        <div class="stats-grid" style="grid-template-columns: repeat(3, 1fr);">
            <div class="stat-card">
                <div class="stat-title">Score</div>
                <div class="stat-value" id="scoreDisplay">0 - 0</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">Time Remaining</div>
                <div class="stat-value" id="clockDisplay">2:00</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">Game State</div>
                <div class="stat-value" id="gameStateDisplay" style="font-size: 18px;">In Play</div>
            </div>
        </div>
        
        <div class="field-container" id="fieldContainer">
            <canvas id="fieldCanvas" width="800" height="1067"></canvas>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-title">Team 1 Passes</div>
                <div class="stat-value" id="team1Passes">0</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">Team 2 Passes</div>
                <div class="stat-value" id="team2Passes">0</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">Team 1 Shots</div>
                <div class="stat-value" id="team1Shots">0</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">Team 2 Shots</div>
                <div class="stat-value" id="team2Shots">0</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">Team 1 Possession</div>
                <div class="stat-value" id="team1Possession">0%</div>
            </div>
            <div class="stat-card">
                <div class="stat-title">Team 2 Possession</div>
                <div class="stat-value" id="team2Possession">0%</div>
            </div>
        </div>
        
                <div id="charts"></div>
            </div>
        </div>
        
        <!-- Parameters Sidebar -->
        <div class="params-sidebar">
            <div class="params-header">Game Parameters</div>
            <div id="parametersContainer"></div>
            <button class="reset-btn" onclick="resetAllParameters()">Reset All to Defaults</button>
        </div>
    </div>
    
    <script>
        let gameData = null;
        let currentFrame = 0;
        let isPlaying = false;
        let animationId = null;
        let speedMultiplier = 10;
        
        const canvas = document.getElementById('fieldCanvas');
        const ctx = canvas.getContext('2d');
        
        // Game parameters with defaults, ranges, and metadata
        const gameParameters = {
            'Formation': [
                {name: 'FORMATION_FUZZINESS', label: 'Fuzziness', default: 0.5, min: 0, max: 2.0, step: 0.1, unit: 'm'},
                {name: 'FORMATION_ADHERENCE_RATE', label: 'Adherence Rate', default: 0.6, min: 0, max: 1.0, step: 0.05, unit: ''},
                {name: 'FORMATION_ELASTICITY', label: 'Elasticity', default: 1.5, min: 0, max: 5.0, step: 0.1, unit: ''},
                {name: 'FORMATION_DAMPING', label: 'Damping', default: 0.4, min: 0, max: 1.0, step: 0.05, unit: ''},
                {name: 'FORMATION_ADAPTATION_RATE', label: 'Adaptation Rate', default: 0.2, min: 0, max: 1.0, step: 0.05, unit: ''}
            ],
            'Ball Interaction': [
                {name: 'BALL_REACTION_DISTANCE', label: 'Reaction Distance', default: 15.0, min: 3, max: 20, step: 0.5, unit: 'm'},
                {name: 'BALL_ATTRACTION_STRENGTH', label: 'Attraction Strength', default: 0.8, min: 0, max: 1.0, step: 0.05, unit: ''},
                {name: 'BALL_CONTROL_RADIUS', label: 'Control Radius', default: 0.5, min: 0, max: 2.0, step: 0.1, unit: 'm'},
                {name: 'BALL_STEAL_DISTANCE', label: 'Steal Distance', default: 1.0, min: 0, max: 3.0, step: 0.1, unit: 'm'},
                {name: 'BALL_STEAL_STRENGTH', label: 'Steal Strength', default: 0.3, min: 0, max: 1.0, step: 0.05, unit: ''}
            ],
            'Player Behavior': [
                {name: 'PASS_PROPENSITY_BASE', label: 'Pass Propensity', default: 0.6, min: 0, max: 1.0, step: 0.05, unit: ''},
                {name: 'SHOOT_PROPENSITY_BASE', label: 'Shoot Propensity', default: 0.3, min: 0, max: 1.0, step: 0.05, unit: ''},
                {name: 'PASS_ACCURACY_BASE', label: 'Pass Accuracy', default: 0.8, min: 0, max: 1.0, step: 0.05, unit: ''},
                {name: 'SHOT_ACCURACY_BASE', label: 'Shot Accuracy', default: 0.4, min: 0, max: 1.0, step: 0.05, unit: ''},
                {name: 'PASS_DISTANCE_MAX', label: 'Max Pass Distance', default: 15.0, min: 5, max: 30, step: 1, unit: 'm'},
                {name: 'SHOOT_DISTANCE_MAX', label: 'Max Shoot Distance', default: 20.0, min: 5, max: 30, step: 1, unit: 'm'}
            ],
            'Physical': [
                {name: 'PLAYER_SPEED_MAX', label: 'Player Max Speed', default: 5.0, min: 2, max: 10, step: 0.5, unit: 'm/s'},
                {name: 'PLAYER_ACCELERATION', label: 'Acceleration', default: 8.0, min: 2, max: 20, step: 0.5, unit: 'm/s²'},
                {name: 'PLAYER_DECELERATION', label: 'Deceleration', default: 10.0, min: 2, max: 20, step: 0.5, unit: 'm/s²'},
                {name: 'PLAYER_COLLISION_RADIUS', label: 'Collision Radius', default: 1.2, min: 0.3, max: 2.0, step: 0.1, unit: 'm'},
                {name: 'PLAYER_REPULSION_STRENGTH', label: 'Repulsion Strength', default: 150.0, min: 10, max: 300, step: 10, unit: 'N'},
                {name: 'PLAYER_STAMINA_MAX', label: 'Max Stamina', default: 100.0, min: 50, max: 200, step: 10, unit: ''},
                {name: 'PLAYER_STAMINA_DECAY', label: 'Stamina Decay', default: 0.5, min: 0, max: 2, step: 0.1, unit: '/s'},
                {name: 'PLAYER_STAMINA_RECOVERY', label: 'Stamina Recovery', default: 2.0, min: 0, max: 5, step: 0.5, unit: '/s'}
            ],
            'Ball Physics': [
                {name: 'BALL_FRICTION', label: 'Friction', default: 0.015, min: 0, max: 0.05, step: 0.001, unit: ''},
                {name: 'BALL_MAX_SPEED', label: 'Max Speed', default: 25.0, min: 10, max: 40, step: 1, unit: 'm/s'},
                {name: 'BALL_AIR_RESISTANCE', label: 'Air Resistance', default: 0.005, min: 0, max: 0.02, step: 0.001, unit: ''},
                {name: 'BALL_ANGULAR_MOMENTUM', label: 'Angular Momentum', default: 0.2, min: 0, max: 1.0, step: 0.05, unit: ''},
                {name: 'BOUNCE_DAMPING', label: 'Bounce Damping', default: 0.7, min: 0, max: 1.0, step: 0.05, unit: ''}
            ],
            'Goalkeeper': [
                {name: 'GK_SPEED_MAX', label: 'Max Speed', default: 6.0, min: 3, max: 10, step: 0.5, unit: 'm/s'},
                {name: 'GK_REACTION_TIME', label: 'Reaction Time', default: 0.2, min: 0, max: 1.0, step: 0.05, unit: 's'},
                {name: 'GK_POSITIONING_RANGE', label: 'Positioning Range', default: 2.0, min: 0, max: 5, step: 0.5, unit: 'm'},
                {name: 'GK_SAVE_PROBABILITY', label: 'Save Probability', default: 0.7, min: 0, max: 1.0, step: 0.05, unit: ''}
            ],
            'Game Rules': [
                {name: 'GAME_DURATION_SECONDS', label: 'Game Duration', default: 120, min: 60, max: 3600, step: 60, unit: 's'},
                {name: 'POSSESSION_DISTANCE', label: 'Possession Distance', default: 3.0, min: 1, max: 5, step: 0.5, unit: 'm'}
            ]
        };
        
        // Store current parameter values
        let currentParams = {};
        
        // Initialize parameter values from defaults
        function initializeParameters() {
            for (const category in gameParameters) {
                gameParameters[category].forEach(param => {
                    currentParams[param.name] = param.default;
                });
            }
        }
        
        // Generate parameter controls HTML
        function generateParameterControls() {
            const container = document.getElementById('parametersContainer');
            let html = '';
            
            for (const category in gameParameters) {
                html += `
                    <div class="param-category">
                        <div class="category-header" onclick="toggleCategory('${category.replace(/\s/g, '_')}')">
                            <span>${category}</span>
                            <span class="category-toggle">▼</span>
                        </div>
                        <div id="category_${category.replace(/\s/g, '_')}" class="category-content">
                `;
                
                gameParameters[category].forEach(param => {
                    const value = currentParams[param.name];
                    html += `
                        <div class="param-item">
                            <div class="param-label">
                                <span class="param-name">${param.label}</span>
                                <span class="param-value" id="value_${param.name}">${value}${param.unit}</span>
                            </div>
                            <input type="range" 
                                   class="param-slider" 
                                   id="slider_${param.name}"
                                   min="${param.min}" 
                                   max="${param.max}" 
                                   step="${param.step}" 
                                   value="${value}"
                                   oninput="updateParameter('${param.name}', this.value, '${param.unit}')">
                        </div>
                    `;
                });
                
                html += `
                        </div>
                    </div>
                `;
            }
            
            container.innerHTML = html;
        }
        
        // Toggle category expand/collapse
        function toggleCategory(categoryId) {
            const content = document.getElementById(`category_${categoryId}`);
            const header = content.previousElementSibling;
            const toggle = header.querySelector('.category-toggle');
            
            if (content.classList.contains('open')) {
                content.classList.remove('open');
                toggle.textContent = '▼';
            } else {
                content.classList.add('open');
                toggle.textContent = '▲';
            }
        }
        
        // Update parameter value
        function updateParameter(paramName, value, unit) {
            currentParams[paramName] = parseFloat(value);
            document.getElementById(`value_${paramName}`).textContent = value + unit;
        }
        
        // Reset all parameters to defaults
        function resetAllParameters() {
            for (const category in gameParameters) {
                gameParameters[category].forEach(param => {
                    currentParams[param.name] = param.default;
                    const slider = document.getElementById(`slider_${param.name}`);
                    if (slider) {
                        slider.value = param.default;
                        document.getElementById(`value_${param.name}`).textContent = param.default + param.unit;
                    }
                });
            }
        }
        
        // Initialize parameters on page load
        initializeParameters();
        generateParameterControls();
        
        // Scale canvas to fit field (width=30m, length=40m)
        // Adjust canvas size to maintain aspect ratio
        canvas.width = 600;  // width
        canvas.height = 800; // length (maintains 30:40 ratio)
        
        const fieldWidth = 30;
        const fieldLength = 40;
        const scaleX = canvas.width / fieldWidth;
        const scaleY = canvas.height / fieldLength;
        
        function scalePoint(x, y) {
            return {
                x: x * scaleX,
                y: y * scaleY
            };
        }
        
        function drawField() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // Field background (already green from CSS)
            ctx.fillStyle = '#2d5016';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            
            // Draw field rim (boundary)
            ctx.strokeStyle = '#555555';
            ctx.lineWidth = 8;
            ctx.strokeRect(2, 2, canvas.width - 4, canvas.height - 4);
            
            // Draw inner field boundary (white lines)
            ctx.strokeStyle = '#ffffff';
            ctx.lineWidth = 2;
            ctx.strokeRect(5, 5, canvas.width - 10, canvas.height - 10);
            
            // Center line
            ctx.strokeStyle = '#ffffff';
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(0, canvas.height / 2);
            ctx.lineTo(canvas.width, canvas.height / 2);
            ctx.stroke();
            
            // Center circle
            ctx.beginPath();
            ctx.arc(canvas.width / 2, canvas.height / 2, 50, 0, 2 * Math.PI);
            ctx.stroke();
            
            // Goals
            const goalWidth = 3.0 * scaleX;
            const goalDepth = 1.0 * scaleY;
            
            // Bottom goal (Team 1)
            ctx.strokeStyle = '#ffffff';
            ctx.lineWidth = 3;
            ctx.beginPath();
            ctx.moveTo(canvas.width / 2 - goalWidth / 2, canvas.height);
            ctx.lineTo(canvas.width / 2 - goalWidth / 2, canvas.height - goalDepth);
            ctx.lineTo(canvas.width / 2 + goalWidth / 2, canvas.height - goalDepth);
            ctx.lineTo(canvas.width / 2 + goalWidth / 2, canvas.height);
            ctx.stroke();
            
            // Top goal (Team 2)
            ctx.beginPath();
            ctx.moveTo(canvas.width / 2 - goalWidth / 2, 0);
            ctx.lineTo(canvas.width / 2 - goalWidth / 2, goalDepth);
            ctx.lineTo(canvas.width / 2 + goalWidth / 2, goalDepth);
            ctx.lineTo(canvas.width / 2 + goalWidth / 2, 0);
            ctx.stroke();
        }
        
        function drawFrame(frameIndex) {
            if (!gameData || frameIndex >= gameData.states.length) return;
            
            drawField();
            
            const state = gameData.states[frameIndex];
            
            // Draw players
            state.team1_players.forEach((player) => {
                const pos = scalePoint(player.x, player.y);
                ctx.fillStyle = player.role === 'goalkeeper' ? '#FFD700' : '#0066FF';
                ctx.beginPath();
                ctx.arc(pos.x, pos.y, 8, 0, 2 * Math.PI);
                ctx.fill();
                ctx.strokeStyle = '#ffffff';
                ctx.lineWidth = 1;
                ctx.stroke();
            });
            
            state.team2_players.forEach((player) => {
                const pos = scalePoint(player.x, player.y);
                ctx.fillStyle = player.role === 'goalkeeper' ? '#FFD700' : '#FF0000';
                ctx.beginPath();
                ctx.arc(pos.x, pos.y, 8, 0, 2 * Math.PI);
                ctx.fill();
                ctx.strokeStyle = '#ffffff';
                ctx.lineWidth = 1;
                ctx.stroke();
            });
            
            // Draw ball
            const ballPos = scalePoint(state.ball.x, state.ball.y);
            ctx.fillStyle = '#ffffff';
            ctx.beginPath();
            ctx.arc(ballPos.x, ballPos.y, 5, 0, 2 * Math.PI);
            ctx.fill();
            ctx.strokeStyle = '#000000';
            ctx.lineWidth = 1;
            ctx.stroke();
            
            // Update stats display
            document.getElementById('scoreDisplay').textContent = 
                `${state.score.team1} - ${state.score.team2}`;
            
            // Update clock display (MM:SS format)
            const timeRemaining = state.time_remaining || 0;
            const minutes = Math.floor(timeRemaining / 60);
            const seconds = Math.floor(timeRemaining % 60);
            document.getElementById('clockDisplay').textContent = 
                `${minutes}:${seconds.toString().padStart(2, '0')}`;
            
            // Update game state display
            const gameStateText = {
                'in_play': 'In Play',
                'kickoff': 'Kick Off',
                'throw_in': 'Throw In',
                'corner_kick': 'Corner Kick',
                'goal_kick': 'Goal Kick',
                'out_of_bounds': 'Out of Bounds',
                'goal': 'Goal!'
            };
            document.getElementById('gameStateDisplay').textContent = 
                gameStateText[state.game_state] || state.game_state;
            
            document.getElementById('team1Passes').textContent = state.stats.team1.passes;
            document.getElementById('team2Passes').textContent = state.stats.team2.passes;
            document.getElementById('team1Shots').textContent = state.stats.team1.shots;
            document.getElementById('team2Shots').textContent = state.stats.team2.shots;
            
            const totalPossession = state.stats.team1.possession_time + state.stats.team2.possession_time;
            if (totalPossession > 0) {
                const team1Pct = (state.stats.team1.possession_time / totalPossession * 100).toFixed(1);
                const team2Pct = (state.stats.team2.possession_time / totalPossession * 100).toFixed(1);
                document.getElementById('team1Possession').textContent = team1Pct + '%';
                document.getElementById('team2Possession').textContent = team2Pct + '%';
            }
        }
        
        function animate() {
            if (!isPlaying || !gameData) return;
            
            drawFrame(currentFrame);
            currentFrame += speedMultiplier;
            
            if (currentFrame >= gameData.states.length) {
                pauseSimulation();
                drawCharts();
            } else {
                animationId = setTimeout(animate, 16); // ~60 FPS
            }
        }
        
        function startSimulation() {
            if (!gameData) {
                // Send current parameters to backend
                fetch('/api/run_game', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({params: currentParams})
                })
                    .then(response => response.json())
                    .then(data => {
                        gameData = data;
                        currentFrame = 0;
                        isPlaying = true;
                        document.getElementById('startBtn').disabled = true;
                        document.getElementById('pauseBtn').disabled = false;
                        animate();
                    })
                    .catch(error => {
                        console.error('Error starting simulation:', error);
                        alert('Error starting simulation. Check console for details.');
                    });
            } else {
                isPlaying = true;
                document.getElementById('startBtn').disabled = true;
                document.getElementById('pauseBtn').disabled = false;
                animate();
            }
        }
        
        function pauseSimulation() {
            isPlaying = false;
            if (animationId) {
                clearTimeout(animationId);
                animationId = null;
            }
            document.getElementById('startBtn').disabled = false;
            document.getElementById('pauseBtn').disabled = true;
        }
        
        function resetSimulation() {
            pauseSimulation();
            currentFrame = 0;
            if (gameData) {
                drawFrame(0);
            } else {
                drawField();
            }
            document.getElementById('charts').innerHTML = '';
        }
        
        function updateSpeed() {
            const slider = document.getElementById('speedSlider');
            speedMultiplier = parseInt(slider.value);
            document.getElementById('speedValue').textContent = speedMultiplier + 'x';
        }
        
        function drawCharts() {
            if (!gameData) return;
            
            const times = gameData.states.map(s => s.time);
            const team1Passes = gameData.states.map(s => s.stats.team1.passes);
            const team2Passes = gameData.states.map(s => s.stats.team2.passes);
            const team1Shots = gameData.states.map(s => s.stats.team1.shots);
            const team2Shots = gameData.states.map(s => s.stats.team2.shots);
            const team1Possession = gameData.states.map(s => s.stats.team1.possession_time);
            const team2Possession = gameData.states.map(s => s.stats.team2.possession_time);
            const ballSpeed = gameData.states.map(s => s.ball.speed);
            
            // Create chart container
            const chartsDiv = document.getElementById('charts');
            chartsDiv.innerHTML = '<div id="passesChart"></div><div id="shotsChart"></div><div id="possessionChart"></div><div id="ballSpeedChart"></div>';
            
            // Passes chart
            Plotly.newPlot('passesChart', [
                {
                    x: times,
                    y: team1Passes,
                    name: 'Team 1 Passes',
                    type: 'scatter',
                    line: {color: '#0066FF'}
                },
                {
                    x: times,
                    y: team2Passes,
                    name: 'Team 2 Passes',
                    type: 'scatter',
                    line: {color: '#FF0000'}
                }
            ], {
                title: 'Passes Over Time',
                xaxis: {title: 'Time (seconds)'},
                yaxis: {title: 'Number of Passes'}
            });
            
            // Shots chart
            Plotly.newPlot('shotsChart', [
                {
                    x: times,
                    y: team1Shots,
                    name: 'Team 1 Shots',
                    type: 'scatter',
                    line: {color: '#0066FF'}
                },
                {
                    x: times,
                    y: team2Shots,
                    name: 'Team 2 Shots',
                    type: 'scatter',
                    line: {color: '#FF0000'}
                }
            ], {
                title: 'Shots Over Time',
                xaxis: {title: 'Time (seconds)'},
                yaxis: {title: 'Number of Shots'}
            });
            
            // Possession chart
            Plotly.newPlot('possessionChart', [
                {
                    x: times,
                    y: team1Possession,
                    name: 'Team 1 Possession',
                    type: 'scatter',
                    fill: 'tozeroy',
                    line: {color: '#0066FF'}
                },
                {
                    x: times,
                    y: team2Possession,
                    name: 'Team 2 Possession',
                    type: 'scatter',
                    fill: 'tozeroy',
                    line: {color: '#FF0000'}
                }
            ], {
                title: 'Possession Over Time',
                xaxis: {title: 'Time (seconds)'},
                yaxis: {title: 'Possession Time (seconds)'}
            });
            
            // Ball speed chart
            Plotly.newPlot('ballSpeedChart', [
                {
                    x: times,
                    y: ballSpeed,
                    name: 'Ball Speed',
                    type: 'scatter',
                    line: {color: '#333333'}
                }
            ], {
                title: 'Ball Speed Over Time',
                xaxis: {title: 'Time (seconds)'},
                yaxis: {title: 'Speed (m/s)'}
            });
        }
        
        // Initialize
        drawField();
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)


def randomize_game_parameters():
    """Randomize game parameters for each restart"""
    import config as cfg
    import numpy as np
    
    # Randomize formation parameters
    cfg.FORMATION_FUZZINESS = 0.3 + np.random.uniform(0, 0.7)  # 0.3 to 1.0
    cfg.FORMATION_ADHERENCE_RATE = 0.4 + np.random.uniform(0, 0.5)  # 0.4 to 0.9
    cfg.BALL_REACTION_DISTANCE = 3.0 + np.random.uniform(0, 7.0)  # 3.0 to 10.0
    cfg.BALL_ATTRACTION_STRENGTH = 0.2 + np.random.uniform(0, 0.6)  # 0.2 to 0.8
    
    # Randomize player behavior parameters
    cfg.PASS_PROPENSITY_BASE = 0.4 + np.random.uniform(0, 0.4)  # 0.4 to 0.8
    cfg.SHOOT_PROPENSITY_BASE = 0.2 + np.random.uniform(0, 0.3)  # 0.2 to 0.5
    cfg.DEFLECT_PROPENSITY_BASE = 0.05 + np.random.uniform(0, 0.15)  # 0.05 to 0.2
    
    # Normalize propensities
    total = cfg.PASS_PROPENSITY_BASE + cfg.SHOOT_PROPENSITY_BASE + cfg.DEFLECT_PROPENSITY_BASE
    cfg.PASS_PROPENSITY_BASE /= total
    cfg.SHOOT_PROPENSITY_BASE /= total
    cfg.DEFLECT_PROPENSITY_BASE /= total
    
    # Randomize physics parameters slightly
    cfg.BALL_FRICTION = 0.01 + np.random.uniform(0, 0.01)  # 0.01 to 0.02
    cfg.BOUNCE_DAMPING = 0.6 + np.random.uniform(0, 0.2)  # 0.6 to 0.8
    cfg.WALL_BOUNCE_DAMPING = 0.5 + np.random.uniform(0, 0.2)  # 0.5 to 0.7


@app.route('/api/run_game', methods=['GET', 'POST'])
def run_game():
    """Run a game and return visualization data"""
    # If POST request, update config parameters from UI
    if request.method == 'POST':
        params = request.json.get('params', {})
        apply_parameters(params)
    else:
        # Randomize parameters for each game (GET request)
        randomize_game_parameters()
    
    # Use default formations for now
    team1_formation = FormationLibrary.get_formation('2-3-1')
    team2_formation = FormationLibrary.get_formation('3-2-1')
    
    result = simulator.run_game(team1_formation, team2_formation, record_states=True)
    # Return states directly for visualization
    return jsonify({
        'states': result['states'],
        'final_stats': result['final_stats']
    })

def apply_parameters(params):
    """Apply parameter overrides to config module"""
    for param_name, value in params.items():
        if hasattr(config, param_name):
            setattr(config, param_name, value)
            print(f"Updated {param_name} to {value}")


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)

