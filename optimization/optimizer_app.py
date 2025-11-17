"""
Flask web application for soccer simulator optimization
"""

import os
import json
import threading
from flask import Flask, render_template_string, jsonify, request, send_from_directory
from datetime import datetime

# Try to import CORS, but make it optional
try:
    from flask_cors import CORS
    CORS_AVAILABLE = True
except ImportError:
    CORS_AVAILABLE = False

from parameter_config import (
    FixedParameters,
    TeamConfiguration,
    FormationParameters,
    TacticalParameters,
    FormationPresets
)
from batch_simulator import BatchSimulator
from optimizer import GeneticOptimizer, FitnessEvaluator

app = Flask(__name__)
if CORS_AVAILABLE:
    CORS(app)  # Enable CORS for API requests

# Store running optimization tasks
running_optimizations = {}
optimization_results = {}


def get_html_template():
    """Return the HTML template"""
    template_path = os.path.join(os.path.dirname(__file__), 'templates', 'optimizer.html')
    if os.path.exists(template_path):
        with open(template_path, 'r') as f:
            return f.read()
    else:
        # Fallback to inline template if file not found
        return get_inline_html_template()


@app.route('/')
def index():
    """Main page"""
    try:
        return render_template_string(get_html_template())
    except FileNotFoundError:
        # Fallback to inline template
        return render_template_string(get_inline_html_template())


@app.route('/api/fixed_params', methods=['GET', 'POST'])
def fixed_params():
    """Get or update fixed parameters"""
    if request.method == 'POST':
        data = request.json
        # Fixed params are read-only in this interface
        # They can be modified in parameter_config.py
        return jsonify({'status': 'success', 'message': 'Fixed params are read-only'})
    else:
        fp = FixedParameters()
        return jsonify({
            'field_length': fp.field_length,
            'field_width': fp.field_width,
            'goal_width': fp.goal_width,
            'game_duration_seconds': fp.game_duration_seconds,
            'time_step': fp.time_step
        })


@app.route('/api/presets/formations', methods=['GET'])
def get_formation_presets():
    """Get available formation presets"""
    presets = {
        '2-3-1': FormationPresets.get_formation_2_3_1().to_dict(),
        '3-2-1': FormationPresets.get_formation_3_2_1().to_dict(),
        '2-2-2': FormationPresets.get_formation_2_2_2().to_dict(),
        '1-3-2': FormationPresets.get_formation_1_3_2().to_dict(),
    }
    return jsonify(presets)


@app.route('/api/presets/tactics', methods=['GET'])
def get_tactics_defaults():
    """Get default tactical parameters"""
    tactics = TacticalParameters()
    return jsonify(tactics.to_dict())


@app.route('/api/team_config/save', methods=['POST'])
def save_team_config():
    """Save a team configuration to file"""
    try:
        data = request.json
        filename = data.get('filename', f"team_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        # Ensure filename ends with .json
        if not filename.endswith('.json'):
            filename += '.json'
        
        # Ensure filename is safe
        filename = os.path.basename(filename)
        
        filepath = os.path.join('saved_configs', filename)
        os.makedirs('saved_configs', exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(data.get('config'), f, indent=2)
        
        return jsonify({'status': 'success', 'filename': filename, 'path': filepath})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@app.route('/api/team_config/load', methods=['POST'])
def load_team_config():
    """Load a team configuration from file"""
    try:
        data = request.json
        filename = data.get('filename')
        
        if not filename:
            return jsonify({'status': 'error', 'message': 'Filename required'}), 400
        
        filename = os.path.basename(filename)  # Security
        filepath = os.path.join('saved_configs', filename)
        
        if not os.path.exists(filepath):
            return jsonify({'status': 'error', 'message': 'File not found'}), 404
        
        with open(filepath, 'r') as f:
            config = json.load(f)
        
        return jsonify({'status': 'success', 'config': config})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@app.route('/api/team_config/list', methods=['GET'])
def list_team_configs():
    """List all saved team configurations"""
    try:
        saved_dir = 'saved_configs'
        os.makedirs(saved_dir, exist_ok=True)
        
        files = [f for f in os.listdir(saved_dir) if f.endswith('.json')]
        files.sort(key=lambda x: os.path.getmtime(os.path.join(saved_dir, x)), reverse=True)
        
        return jsonify({'status': 'success', 'files': files})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@app.route('/api/compare', methods=['POST'])
def compare_configurations():
    """Compare two team configurations"""
    try:
        data = request.json
        team1_config = TeamConfiguration.from_dict(data['team1'])
        team2_config = TeamConfiguration.from_dict(data['team2'])
        num_games = data.get('num_games', 50)
        parallel = data.get('parallel', True)
        
        import time
        start_time = time.time()
        
        simulator = BatchSimulator()
        results = simulator.run_games(
            team1_config,
            team2_config,
            num_games=num_games,
            parallel=parallel,
            verbose=False
        )
        
        elapsed = time.time() - start_time
        
        analysis = simulator.analyze_results(results)
        
        return jsonify({
            'status': 'success',
            'analysis': analysis,
            'num_games': num_games,
            'elapsed_time': elapsed,
            'games_per_second': num_games / elapsed if elapsed > 0 else 0
        })
    except Exception as e:
        import traceback
        return jsonify({
            'status': 'error', 
            'message': str(e),
            'traceback': traceback.format_exc()
        }), 400


# Store running batch tests
running_batch_tests = {}


@app.route('/api/batch_test', methods=['POST'])
def batch_test():
    """Quick batch test - run games with progress tracking"""
    try:
        data = request.json or {}
        num_games = data.get('num_games', 100)
        game_duration = data.get('game_duration', 120)
        parallel = data.get('parallel', True)
        
        # Create task ID
        task_id = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        
        # Create simple configurations
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
        
        fixed_params = FixedParameters(game_duration_seconds=game_duration)
        
        # Initialize progress
        running_batch_tests[task_id] = {
            'status': 'running',
            'games_completed': 0,
            'total_games': num_games,
            'start_time': None,
            'elapsed_time': 0,
            'results': None,
            'analysis': None,
            'error': None
        }
        
        # Run in background thread
        def run_batch_test():
            try:
                import time
                import numpy as np
                import multiprocessing as mp
                from batch_simulator import run_single_game, run_single_game_wrapper
                
                start_time = time.time()
                running_batch_tests[task_id]['start_time'] = start_time
                
                # Generate random seeds
                random_seeds = [np.random.randint(0, 2**31) for _ in range(num_games)]
                
                # Prepare arguments
                game_args = [
                    (team1_config, team2_config, fixed_params, seed)
                    for seed in random_seeds
                ]
                
                results = []
                
                if parallel and num_games > 1:
                    # Use imap for progress tracking
                    num_workers = min(mp.cpu_count(), num_games)
                    
                    with mp.Pool(num_workers) as pool:
                        # Use imap_unordered for progress tracking
                        for i, result in enumerate(pool.imap_unordered(run_single_game_wrapper, game_args)):
                            results.append(result)
                            running_batch_tests[task_id].update({
                                'games_completed': i + 1,
                                'elapsed_time': time.time() - start_time,
                                'estimated_remaining': (time.time() - start_time) / (i + 1) * (num_games - i - 1) if i > 0 else 0
                            })
                else:
                    # Sequential with progress updates
                    for i, args in enumerate(game_args):
                        result = run_single_game(*args)
                        results.append(result)
                        running_batch_tests[task_id].update({
                            'games_completed': i + 1,
                            'elapsed_time': time.time() - start_time
                        })
                
                elapsed = time.time() - start_time
                
                # Analyze results
                simulator = BatchSimulator(fixed_params)
                analysis = simulator.analyze_results(results)
                
                running_batch_tests[task_id].update({
                    'status': 'completed',
                    'games_completed': num_games,
                    'elapsed_time': elapsed,
                    'results': results,
                    'analysis': analysis,
                    'performance': {
                        'total_time': elapsed,
                        'time_per_game': elapsed / num_games,
                        'games_per_second': num_games / elapsed if elapsed > 0 else 0,
                        'num_games': num_games,
                        'parallel': parallel
                    }
                })
            except Exception as e:
                import traceback
                running_batch_tests[task_id].update({
                    'status': 'error',
                    'error': str(e),
                    'traceback': traceback.format_exc()
                })
        
        thread = threading.Thread(target=run_batch_test)
        thread.daemon = True
        thread.start()
        
        return jsonify({'status': 'started', 'task_id': task_id})
    except Exception as e:
        import traceback
        return jsonify({
            'status': 'error',
            'message': str(e),
            'traceback': traceback.format_exc()
        }), 400


@app.route('/api/batch_test/status/<task_id>', methods=['GET'])
def get_batch_test_status(task_id):
    """Get batch test progress status"""
    if task_id not in running_batch_tests:
        return jsonify({'status': 'not_found'}), 404
    
    status = dict(running_batch_tests[task_id])
    
    # Remove results from status response (too large)
    if 'results' in status:
        status.pop('results')
    
    return jsonify(status)


@app.route('/api/optimize/formation', methods=['POST'])
def optimize_formation():
    """Start formation optimization"""
    try:
        data = request.json
        
        # Parse configurations
        base_formation = FormationParameters.from_dict(data['base_formation'])
        tactics = TacticalParameters.from_dict(data['tactics'])
        opponent_config = TeamConfiguration.from_dict(data['opponent'])
        
        # Optimization parameters
        population_size = data.get('population_size', 30)
        generations = data.get('generations', 20)
        num_games = data.get('num_games', 20)
        mutation_rate = data.get('mutation_rate', 0.15)
        mutation_strength = data.get('mutation_strength', 0.1)
        
        # Create task ID
        task_id = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        
        # Create evaluator and optimizer
        evaluator = FitnessEvaluator(opponent_config, num_games=num_games)
        optimizer = GeneticOptimizer(
            population_size=population_size,
            mutation_rate=mutation_rate,
            mutation_strength=mutation_strength,
            crossover_rate=0.7
        )
        
        # Run optimization in background thread
        def run_optimization():
            try:
                import sys
                print(f"DEBUG: Optimization thread started for task {task_id}")
                sys.stdout.flush()
                import time
                start_time = time.time()
                
                # Initialize status
                running_optimizations[task_id] = {
                    'status': 'running',
                    'generation': 0,
                    'total_generations': generations,
                    'current_phase': 'Initializing population...',
                    'best_fitness': None,  # Use None instead of -inf for JSON compatibility
                    'history': []
                }
                print(f"DEBUG: Status initialized for task {task_id}")
                
                # Initialize population
                print(f"DEBUG: Creating initial population...")
                running_optimizations[task_id].update({
                    'current_phase': 'Creating initial population...',
                    'generation': 0
                })
                
                population = optimizer._initialize_formation_population(base_formation)
                print(f"DEBUG: Population initialized with {len(population)} individuals")
                
                # Update status after population is created
                running_optimizations[task_id].update({
                    'current_phase': 'Population initialized. Starting optimization...',
                    'generation': 0
                })
                
                # Small delay to ensure status is visible
                time.sleep(0.1)
                
                print(f"DEBUG: Starting generation loop for {generations} generations...")
                for gen in range(generations):
                    print(f"DEBUG: Loop iteration {gen + 1}/{generations}")
                    gen_start = time.time()
                    
                    # Update status to show we're evaluating candidates
                    # Use direct dictionary assignment to ensure thread safety
                    status_update = {
                        'status': 'running',
                        'generation': gen + 1,
                        'total_generations': generations,
                        'current_phase': f'Starting generation {gen + 1}...'
                    }
                    running_optimizations[task_id].update(status_update)
                    print(f"DEBUG: Updated status for generation {gen + 1}")  # Debug output
                    
                    # Small delay to ensure status update is visible
                    time.sleep(0.1)
                    
                    # Evaluate fitness
                    fitness_scores = []
                    total_candidates = len(population)
                    
                    for i, individual in enumerate(population):
                        # Update status to show progress within generation (more frequent updates)
                        if i % 3 == 0 or i == 0:  # Update every 3 candidates or at start
                            phase_update = {
                                'current_phase': f'Evaluating candidate {i+1}/{total_candidates}...',
                                'generation': gen + 1  # Explicitly set generation again
                            }
                            running_optimizations[task_id].update(phase_update)
                            print(f"DEBUG: Evaluating candidate {i+1}/{total_candidates} for generation {gen + 1}")
                        
                        fitness = evaluator.evaluate_formation(individual, tactics)
                        fitness_scores.append(fitness)
                        
                        # Update every candidate if it's a small population
                        if total_candidates <= 10:
                            running_optimizations[task_id]['current_phase'] = f'Evaluated {i+1}/{total_candidates} candidates...'
                    
                    # Track best
                    best_idx = max(range(len(fitness_scores)), key=lambda i: fitness_scores[i])
                    best_gen_fitness = fitness_scores[best_idx]
                    
                    current_best = running_optimizations[task_id].get('best_fitness')
                    if current_best is None or best_gen_fitness > current_best:
                        running_optimizations[task_id]['best_fitness'] = best_gen_fitness
                        running_optimizations[task_id]['best_individual'] = population[best_idx].to_dict()
                    
                    # Update history
                    history = running_optimizations[task_id].get('history', [])
                    history.append({
                        'generation': gen + 1,
                        'best_fitness': best_gen_fitness,
                        'avg_fitness': sum(fitness_scores) / len(fitness_scores),
                        'std_fitness': (sum((x - sum(fitness_scores)/len(fitness_scores))**2 for x in fitness_scores) / len(fitness_scores))**0.5
                    })
                    running_optimizations[task_id]['history'] = history
                    
                    gen_elapsed = time.time() - gen_start
                    total_elapsed = time.time() - start_time
                    avg_gen_time = total_elapsed / (gen + 1)
                    estimated_remaining = avg_gen_time * (generations - gen - 1)
                    
                    # Update status with detailed info
                    running_optimizations[task_id].update({
                        'status': 'running',
                        'generation': gen + 1,  # Make sure generation is explicitly set
                        'current_phase': f'Generation {gen + 1} complete',
                        'best_fitness': best_gen_fitness,
                        'avg_fitness': sum(fitness_scores) / len(fitness_scores),
                        'gen_elapsed_time': gen_elapsed,
                        'total_elapsed_time': total_elapsed,
                        'estimated_remaining_time': estimated_remaining
                    })
                    
                    # Small delay to ensure status update is visible
                    time.sleep(0.1)
                    
                    # Evolve population
                    population = optimizer._evolve_population(
                        population,
                        fitness_scores,
                        lambda ind: ind.mutate(optimizer.mutation_rate, optimizer.mutation_strength)
                    )
                
                # Optimization complete
                best_formation = optimizer.best_individual if optimizer.best_individual else base_formation
                running_optimizations[task_id] = {
                    'status': 'completed',
                    'best_formation': best_formation.to_dict() if hasattr(best_formation, 'to_dict') else best_formation,
                    'best_fitness': running_optimizations[task_id]['best_fitness'],
                    'history': running_optimizations[task_id]['history'],
                    'total_time': time.time() - start_time
                }
            except Exception as e:
                import traceback
                error_msg = str(e)
                error_trace = traceback.format_exc()
                print(f"DEBUG: ERROR in optimization thread for task {task_id}: {error_msg}")
                print(f"DEBUG: Traceback: {error_trace}")
                running_optimizations[task_id] = {
                    'status': 'error',
                    'message': error_msg,
                    'traceback': error_trace
                }
        
        # Set initial status before starting thread
        running_optimizations[task_id] = {
            'status': 'running',
            'generation': 0,
            'total_generations': generations,
            'current_phase': 'Starting optimization...',
            'best_fitness': None,  # Use None instead of -inf for JSON compatibility
            'history': []
        }
        
        print(f"DEBUG: About to start optimization thread for task {task_id}")
        import sys
        sys.stdout.flush()
        
        thread = threading.Thread(target=run_optimization)
        thread.daemon = True
        thread.start()
        
        print(f"DEBUG: Thread started for task {task_id}, thread name: {thread.name}")
        sys.stdout.flush()
        
        return jsonify({'status': 'started', 'task_id': task_id})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@app.route('/api/optimize/tactics', methods=['POST'])
def optimize_tactics():
    """Start tactical optimization"""
    try:
        data = request.json
        
        # Parse configurations
        formation = FormationParameters.from_dict(data['formation'])
        base_tactics = TacticalParameters.from_dict(data['base_tactics'])
        opponent_config = TeamConfiguration.from_dict(data['opponent'])
        
        # Optimization parameters
        population_size = data.get('population_size', 30)
        generations = data.get('generations', 20)
        num_games = data.get('num_games', 20)
        mutation_rate = data.get('mutation_rate', 0.15)
        mutation_strength = data.get('mutation_strength', 0.1)
        
        # Create task ID
        task_id = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        
        # Create evaluator and optimizer
        evaluator = FitnessEvaluator(opponent_config, num_games=num_games)
        optimizer = GeneticOptimizer(
            population_size=population_size,
            mutation_rate=mutation_rate,
            mutation_strength=mutation_strength,
            crossover_rate=0.7
        )
        
        # Run optimization in background thread
        def run_optimization():
            try:
                best_tactics, best_fitness, history = optimizer.optimize_tactics(
                    formation,
                    base_tactics,
                    evaluator,
                    generations=generations,
                    verbose=False
                )
                
                running_optimizations[task_id] = {
                    'status': 'completed',
                    'best_tactics': best_tactics.to_dict(),
                    'best_fitness': best_fitness,
                    'history': history
                }
            except Exception as e:
                running_optimizations[task_id] = {
                    'status': 'error',
                    'message': str(e)
                }
        
        thread = threading.Thread(target=run_optimization)
        thread.daemon = True
        thread.start()
        
        running_optimizations[task_id] = {
            'status': 'running',
            'generation': 0,
            'total_generations': generations
        }
        
        return jsonify({'status': 'started', 'task_id': task_id})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@app.route('/api/optimize/both', methods=['POST'])
def optimize_both():
    """Start combined optimization"""
    try:
        data = request.json
        
        # Parse configurations
        base_formation = FormationParameters.from_dict(data['base_formation'])
        base_tactics = TacticalParameters.from_dict(data['base_tactics'])
        opponent_config = TeamConfiguration.from_dict(data['opponent'])
        
        # Optimization parameters
        population_size = data.get('population_size', 25)
        generations = data.get('generations', 15)
        num_games = data.get('num_games', 15)
        mutation_rate = data.get('mutation_rate', 0.15)
        mutation_strength = data.get('mutation_strength', 0.1)
        
        # Create task ID
        task_id = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        
        # Create evaluator and optimizer
        evaluator = FitnessEvaluator(opponent_config, num_games=num_games)
        optimizer = GeneticOptimizer(
            population_size=population_size,
            mutation_rate=mutation_rate,
            mutation_strength=mutation_strength,
            crossover_rate=0.7
        )
        
        # Run optimization in background thread
        def run_optimization():
            try:
                best_config, best_fitness, history = optimizer.optimize_both(
                    base_formation,
                    base_tactics,
                    evaluator,
                    generations=generations,
                    verbose=False
                )
                
                running_optimizations[task_id] = {
                    'status': 'completed',
                    'best_config': best_config.to_dict(),
                    'best_fitness': best_fitness,
                    'history': history
                }
            except Exception as e:
                running_optimizations[task_id] = {
                    'status': 'error',
                    'message': str(e)
                }
        
        thread = threading.Thread(target=run_optimization)
        thread.daemon = True
        thread.start()
        
        running_optimizations[task_id] = {
            'status': 'running',
            'generation': 0,
            'total_generations': generations
        }
        
        return jsonify({'status': 'started', 'task_id': task_id})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@app.route('/api/optimize/status/<task_id>', methods=['GET'])
def get_optimization_status(task_id):
    """Get optimization status"""
    if task_id not in running_optimizations:
        return jsonify({'status': 'not_found'}), 404
    
    # Make a copy to avoid race conditions
    status = dict(running_optimizations[task_id])
    
    # Ensure all required fields are present
    if 'status' not in status:
        status['status'] = 'unknown'
    
    # Make sure numeric fields are properly set
    if 'generation' not in status:
        status['generation'] = 0
    if 'total_generations' not in status:
        status['total_generations'] = 0
    
    # Debug logging
    print(f"DEBUG: Status request for {task_id}: generation={status.get('generation')}, status={status.get('status')}")
    
    return jsonify(status)


@app.route('/api/optimize/list', methods=['GET'])
def list_optimizations():
    """List all optimization tasks"""
    tasks = []
    for task_id, status in running_optimizations.items():
        tasks.append({
            'task_id': task_id,
            'status': status.get('status', 'unknown'),
            'generation': status.get('generation', 0),
            'total_generations': status.get('total_generations', 0)
        })
    return jsonify({'tasks': tasks})


@app.route('/saved_configs/<filename>')
def serve_saved_config(filename):
    """Serve saved configuration files"""
    return send_from_directory('saved_configs', filename)


if __name__ == '__main__':
    # Create saved_configs directory
    os.makedirs('saved_configs', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    print("\n" + "="*60)
    print("Soccer Simulator Optimization Web Interface")
    print("="*60)
    print("\nOpen your browser and go to: http://127.0.0.1:5001")
    print("\nPress Ctrl+C to stop the server\n")
    
    app.run(debug=True, host='127.0.0.1', port=5001, threaded=True)


def get_inline_html_template():
    """Fallback inline HTML template if file not found"""
    return """<html><body>
    <h1>Error: Template file not found</h1>
    <p>Please ensure templates/optimizer.html exists</p>
    <p>Template path: """ + os.path.join(os.path.dirname(__file__), 'templates', 'optimizer.html') + """</p>
    </body></html>"""

