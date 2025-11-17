"""
Genetic Algorithm Optimizer for Formations and Tactics
"""

import numpy as np
import json
from typing import List, Tuple, Callable, Optional, Dict
from datetime import datetime
import time
import multiprocessing as mp
from functools import partial

from parameter_config import (
    FixedParameters,
    TeamConfiguration,
    FormationParameters,
    TacticalParameters,
    FormationPresets
)
from batch_simulator import BatchSimulator


class FitnessEvaluator:
    """Evaluates fitness of team configurations"""
    
    def __init__(self, 
                 opponent_config: TeamConfiguration,
                 num_games: int = 20,
                 fixed_params: Optional[FixedParameters] = None,
                 parallel_evaluation: bool = True):
        """
        Args:
            opponent_config: Configuration of the opponent to test against
            num_games: Number of games to run for fitness evaluation
            fixed_params: Fixed simulation parameters
            parallel_evaluation: Whether to evaluate multiple candidates in parallel
        """
        self.opponent_config = opponent_config
        self.num_games = num_games
        self.fixed_params = fixed_params or FixedParameters()
        self.parallel_evaluation = parallel_evaluation
        self.simulator = BatchSimulator(fixed_params)
    
    def evaluate_formation(self, formation: FormationParameters, 
                          tactics: TacticalParameters) -> float:
        """
        Evaluate fitness of a formation
        
        Returns:
            Fitness score (higher is better)
        """
        team_config = TeamConfiguration(formation, tactics, team_id=0)
        
        # Run games
        results = self.simulator.run_games(
            team_config, 
            self.opponent_config,
            num_games=self.num_games,
            parallel=True,
            verbose=False
        )
        
        # Calculate fitness based on multiple factors
        analysis = self.simulator.analyze_results(results)
        
        # Fitness = win_rate * 100 + goal_difference * 10
        win_rate = analysis['team1']['win_rate']
        goal_diff = analysis['team1']['avg_goals'] - analysis['team2']['avg_goals']
        
        fitness = win_rate * 100 + goal_diff * 10
        
        return fitness
    
    def evaluate_tactics(self, tactics: TacticalParameters,
                        formation: FormationParameters) -> float:
        """
        Evaluate fitness of tactical parameters
        
        Returns:
            Fitness score (higher is better)
        """
        return self.evaluate_formation(formation, tactics)
    
    def evaluate_formation_batch(self, formations: List[FormationParameters],
                                 tactics: TacticalParameters,
                                 num_workers: Optional[int] = None) -> List[float]:
        """
        Evaluate fitness of multiple formations in parallel
        
        Args:
            formations: List of formations to evaluate
            tactics: Tactical parameters (same for all)
            num_workers: Number of parallel workers (None = auto)
        
        Returns:
            List of fitness scores
        """
        if not self.parallel_evaluation or len(formations) == 1:
            # Sequential evaluation
            return [self.evaluate_formation(f, tactics) for f in formations]
        
        # Parallel evaluation
        if num_workers is None:
            num_workers = min(mp.cpu_count(), len(formations))
        
        with mp.Pool(num_workers) as pool:
            evaluate_fn = partial(self._evaluate_formation_worker, 
                                 opponent_config=self.opponent_config,
                                 tactics=tactics,
                                 num_games=self.num_games,
                                 fixed_params=self.fixed_params)
            fitness_scores = pool.map(evaluate_fn, formations)
        
        return fitness_scores
    
    def evaluate_tactics_batch(self, tactics_list: List[TacticalParameters],
                               formation: FormationParameters,
                               num_workers: Optional[int] = None) -> List[float]:
        """
        Evaluate fitness of multiple tactical configurations in parallel
        
        Args:
            tactics_list: List of tactical configurations to evaluate
            formation: Formation (same for all)
            num_workers: Number of parallel workers (None = auto)
        
        Returns:
            List of fitness scores
        """
        if not self.parallel_evaluation or len(tactics_list) == 1:
            # Sequential evaluation
            return [self.evaluate_tactics(t, formation) for t in tactics_list]
        
        # Parallel evaluation
        if num_workers is None:
            num_workers = min(mp.cpu_count(), len(tactics_list))
        
        with mp.Pool(num_workers) as pool:
            evaluate_fn = partial(self._evaluate_tactics_worker,
                                 opponent_config=self.opponent_config,
                                 formation=formation,
                                 num_games=self.num_games,
                                 fixed_params=self.fixed_params)
            fitness_scores = pool.map(evaluate_fn, tactics_list)
        
        return fitness_scores
    
    @staticmethod
    def _evaluate_formation_worker(formation: FormationParameters,
                                   opponent_config: TeamConfiguration,
                                   tactics: TacticalParameters,
                                   num_games: int,
                                   fixed_params: FixedParameters) -> float:
        """Worker function for parallel formation evaluation"""
        team_config = TeamConfiguration(formation, tactics, team_id=0)
        simulator = BatchSimulator(fixed_params)
        
        results = simulator.run_games(
            team_config,
            opponent_config,
            num_games=num_games,
            parallel=True,
            verbose=False
        )
        
        analysis = simulator.analyze_results(results)
        win_rate = analysis['team1']['win_rate']
        goal_diff = analysis['team1']['avg_goals'] - analysis['team2']['avg_goals']
        
        return win_rate * 100 + goal_diff * 10
    
    @staticmethod
    def _evaluate_tactics_worker(tactics: TacticalParameters,
                                opponent_config: TeamConfiguration,
                                formation: FormationParameters,
                                num_games: int,
                                fixed_params: FixedParameters) -> float:
        """Worker function for parallel tactics evaluation"""
        team_config = TeamConfiguration(formation, tactics, team_id=0)
        simulator = BatchSimulator(fixed_params)
        
        results = simulator.run_games(
            team_config,
            opponent_config,
            num_games=num_games,
            parallel=True,
            verbose=False
        )
        
        analysis = simulator.analyze_results(results)
        win_rate = analysis['team1']['win_rate']
        goal_diff = analysis['team1']['avg_goals'] - analysis['team2']['avg_goals']
        
        return win_rate * 100 + goal_diff * 10


class GeneticOptimizer:
    """Genetic Algorithm for optimizing formations and tactics"""
    
    def __init__(self,
                 population_size: int = 30,
                 mutation_rate: float = 0.15,
                 mutation_strength: float = 0.1,
                 crossover_rate: float = 0.7,
                 elite_fraction: float = 0.1):
        """
        Args:
            population_size: Number of individuals in population
            mutation_rate: Probability of mutation
            mutation_strength: Strength of mutations
            crossover_rate: Probability of crossover
            elite_fraction: Fraction of top performers to preserve
        """
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.mutation_strength = mutation_strength
        self.crossover_rate = crossover_rate
        self.elite_size = max(1, int(population_size * elite_fraction))
        
        self.best_individual = None
        self.best_fitness = -float('inf')
        self.history = []
    
    def optimize_formation(self,
                          base_formation: FormationParameters,
                          tactics: TacticalParameters,
                          evaluator: FitnessEvaluator,
                          generations: int = 50,
                          verbose: bool = True) -> Tuple[FormationParameters, float, List]:
        """
        Optimize formation using genetic algorithm
        
        Args:
            base_formation: Starting formation
            tactics: Fixed tactical parameters
            evaluator: Fitness evaluator
            generations: Number of generations to evolve
            verbose: Whether to print progress
        
        Returns:
            (best_formation, best_fitness, history)
        """
        
        if verbose:
            print(f"\n=== OPTIMIZING FORMATION ===")
            print(f"Base Formation: {base_formation.name}")
            print(f"Population Size: {self.population_size}")
            print(f"Generations: {generations}")
            print(f"Starting optimization...\n")
        
        # Initialize population
        population = self._initialize_formation_population(base_formation)
        
        start_time = time.time()
        
        for gen in range(generations):
            gen_start = time.time()
            
            # Evaluate fitness (parallel evaluation of all candidates)
            fitness_scores = evaluator.evaluate_formation_batch(population, tactics)
            
            # Track best
            best_idx = np.argmax(fitness_scores)
            if fitness_scores[best_idx] > self.best_fitness:
                self.best_fitness = fitness_scores[best_idx]
                self.best_individual = population[best_idx]
            
            # Record history
            self.history.append({
                'generation': gen,
                'best_fitness': fitness_scores[best_idx],
                'avg_fitness': np.mean(fitness_scores),
                'std_fitness': np.std(fitness_scores)
            })
            
            if verbose:
                elapsed = time.time() - gen_start
                print(f"Generation {gen+1}/{generations}: "
                      f"Best={fitness_scores[best_idx]:.2f}, "
                      f"Avg={np.mean(fitness_scores):.2f}, "
                      f"Time={elapsed:.1f}s")
            
            # Selection and reproduction
            population = self._evolve_population(
                population, 
                fitness_scores,
                lambda ind: ind.mutate(self.mutation_rate, self.mutation_strength)
            )
        
        total_time = time.time() - start_time
        
        if verbose:
            print(f"\nOptimization completed in {total_time:.1f} seconds")
            print(f"Best fitness: {self.best_fitness:.2f}")
        
        return self.best_individual, self.best_fitness, self.history
    
    def optimize_tactics(self,
                        formation: FormationParameters,
                        base_tactics: TacticalParameters,
                        evaluator: FitnessEvaluator,
                        generations: int = 50,
                        verbose: bool = True) -> Tuple[TacticalParameters, float, List]:
        """
        Optimize tactical parameters using genetic algorithm
        
        Args:
            formation: Fixed formation
            base_tactics: Starting tactical parameters
            evaluator: Fitness evaluator
            generations: Number of generations to evolve
            verbose: Whether to print progress
        
        Returns:
            (best_tactics, best_fitness, history)
        """
        
        if verbose:
            print(f"\n=== OPTIMIZING TACTICS ===")
            print(f"Formation: {formation.name}")
            print(f"Population Size: {self.population_size}")
            print(f"Generations: {generations}")
            print(f"Starting optimization...\n")
        
        # Initialize population
        population = self._initialize_tactics_population(base_tactics)
        
        start_time = time.time()
        
        for gen in range(generations):
            gen_start = time.time()
            
            # Evaluate fitness (parallel evaluation of all candidates)
            fitness_scores = evaluator.evaluate_tactics_batch(population, formation)
            
            # Track best
            best_idx = np.argmax(fitness_scores)
            if fitness_scores[best_idx] > self.best_fitness:
                self.best_fitness = fitness_scores[best_idx]
                self.best_individual = population[best_idx]
            
            # Record history
            self.history.append({
                'generation': gen,
                'best_fitness': fitness_scores[best_idx],
                'avg_fitness': np.mean(fitness_scores),
                'std_fitness': np.std(fitness_scores)
            })
            
            if verbose:
                elapsed = time.time() - gen_start
                print(f"Generation {gen+1}/{generations}: "
                      f"Best={fitness_scores[best_idx]:.2f}, "
                      f"Avg={np.mean(fitness_scores):.2f}, "
                      f"Time={elapsed:.1f}s")
            
            # Selection and reproduction
            population = self._evolve_population(
                population,
                fitness_scores,
                lambda ind: ind.mutate(self.mutation_rate, self.mutation_strength)
            )
        
        total_time = time.time() - start_time
        
        if verbose:
            print(f"\nOptimization completed in {total_time:.1f} seconds")
            print(f"Best fitness: {self.best_fitness:.2f}")
        
        return self.best_individual, self.best_fitness, self.history
    
    def optimize_both(self,
                     base_formation: FormationParameters,
                     base_tactics: TacticalParameters,
                     evaluator: FitnessEvaluator,
                     generations: int = 50,
                     verbose: bool = True) -> Tuple[TeamConfiguration, float, List]:
        """
        Optimize both formation and tactics simultaneously
        
        Args:
            base_formation: Starting formation
            base_tactics: Starting tactical parameters
            evaluator: Fitness evaluator
            generations: Number of generations to evolve
            verbose: Whether to print progress
        
        Returns:
            (best_config, best_fitness, history)
        """
        
        if verbose:
            print(f"\n=== OPTIMIZING FORMATION AND TACTICS ===")
            print(f"Base Formation: {base_formation.name}")
            print(f"Population Size: {self.population_size}")
            print(f"Generations: {generations}")
            print(f"Starting optimization...\n")
        
        # Initialize population with team configurations
        population = []
        for _ in range(self.population_size):
            formation = base_formation.mutate(self.mutation_rate, self.mutation_strength)
            tactics = base_tactics.mutate(self.mutation_rate, self.mutation_strength)
            population.append(TeamConfiguration(formation, tactics, team_id=0))
        
        start_time = time.time()
        
        for gen in range(generations):
            gen_start = time.time()
            
            # Evaluate fitness (parallel evaluation of all candidates)
            # Prepare arguments for batch evaluation
            evaluate_fn = partial(self._evaluate_team_config_worker,
                                 opponent_config=evaluator.opponent_config,
                                 num_games=evaluator.num_games,
                                 fixed_params=evaluator.fixed_params)
            
            # Use parallel evaluation if enabled
            if evaluator.parallel_evaluation and len(population) > 1:
                num_workers = min(mp.cpu_count(), len(population))
                with mp.Pool(num_workers) as pool:
                    fitness_scores = pool.map(evaluate_fn, population)
            else:
                fitness_scores = [evaluate_fn(ind) for ind in population]
            
            # Track best
            best_idx = np.argmax(fitness_scores)
            if fitness_scores[best_idx] > self.best_fitness:
                self.best_fitness = fitness_scores[best_idx]
                self.best_individual = population[best_idx]
            
            # Record history
            self.history.append({
                'generation': gen,
                'best_fitness': fitness_scores[best_idx],
                'avg_fitness': np.mean(fitness_scores),
                'std_fitness': np.std(fitness_scores)
            })
            
            if verbose:
                elapsed = time.time() - gen_start
                print(f"Generation {gen+1}/{generations}: "
                      f"Best={fitness_scores[best_idx]:.2f}, "
                      f"Avg={np.mean(fitness_scores):.2f}, "
                      f"Time={elapsed:.1f}s")
            
            # Selection and reproduction
            new_population = []
            
            # Elite preservation
            elite_indices = np.argsort(fitness_scores)[-self.elite_size:]
            for idx in elite_indices:
                new_population.append(population[idx])
            
            # Generate offspring
            while len(new_population) < self.population_size:
                # Tournament selection
                parent1 = self._tournament_selection(population, fitness_scores)
                parent2 = self._tournament_selection(population, fitness_scores)
                
                # Crossover
                if np.random.random() < self.crossover_rate:
                    child_formation = parent1.formation.crossover(parent2.formation)
                    child_tactics = parent1.tactics.crossover(parent2.tactics)
                else:
                    child_formation = parent1.formation
                    child_tactics = parent1.tactics
                
                # Mutation
                child_formation = child_formation.mutate(self.mutation_rate, self.mutation_strength)
                child_tactics = child_tactics.mutate(self.mutation_rate, self.mutation_strength)
                
                new_population.append(TeamConfiguration(child_formation, child_tactics, team_id=0))
            
            population = new_population
        
        total_time = time.time() - start_time
        
        if verbose:
            print(f"\nOptimization completed in {total_time:.1f} seconds")
            print(f"Best fitness: {self.best_fitness:.2f}")
        
        return self.best_individual, self.best_fitness, self.history
    
    def _initialize_formation_population(self, base: FormationParameters) -> List[FormationParameters]:
        """Initialize population of formations"""
        population = [base]
        for _ in range(self.population_size - 1):
            mutated = base.mutate(self.mutation_rate * 2, self.mutation_strength * 2)
            population.append(mutated)
        return population
    
    def _initialize_tactics_population(self, base: TacticalParameters) -> List[TacticalParameters]:
        """Initialize population of tactical parameters"""
        population = [base]
        for _ in range(self.population_size - 1):
            mutated = base.mutate(self.mutation_rate * 2, self.mutation_strength * 2)
            population.append(mutated)
        return population
    
    def _evolve_population(self, population, fitness_scores, mutate_fn):
        """Evolve population through selection, crossover, and mutation"""
        new_population = []
        
        # Elite preservation
        elite_indices = np.argsort(fitness_scores)[-self.elite_size:]
        for idx in elite_indices:
            new_population.append(population[idx])
        
        # Generate offspring
        while len(new_population) < self.population_size:
            # Tournament selection
            parent1 = self._tournament_selection(population, fitness_scores)
            parent2 = self._tournament_selection(population, fitness_scores)
            
            # Crossover
            if np.random.random() < self.crossover_rate:
                child = parent1.crossover(parent2)
            else:
                child = parent1
            
            # Mutation
            child = mutate_fn(child)
            
            new_population.append(child)
        
        return new_population
    
    def _tournament_selection(self, population, fitness_scores, tournament_size=3):
        """Select individual using tournament selection"""
        indices = np.random.choice(len(population), tournament_size, replace=False)
        tournament_fitness = [fitness_scores[i] for i in indices]
        winner_idx = indices[np.argmax(tournament_fitness)]
        return population[winner_idx]
    
    @staticmethod
    def _evaluate_team_config_worker(team_config: TeamConfiguration,
                                    opponent_config: TeamConfiguration,
                                    num_games: int,
                                    fixed_params: FixedParameters) -> float:
        """Worker function for parallel team configuration evaluation"""
        simulator = BatchSimulator(fixed_params)
        
        results = simulator.run_games(
            team_config,
            opponent_config,
            num_games=num_games,
            parallel=True,
            verbose=False
        )
        
        analysis = simulator.analyze_results(results)
        win_rate = analysis['team1']['win_rate']
        goal_diff = analysis['team1']['avg_goals'] - analysis['team2']['avg_goals']
        
        return win_rate * 100 + goal_diff * 10
    
    def save_history(self, filename: str):
        """Save optimization history to file"""
        with open(filename, 'w') as f:
            json.dump(self.history, f, indent=2)
        print(f"History saved to {filename}")
    
    def save_best(self, filename: str):
        """Save best individual to file"""
        if isinstance(self.best_individual, TeamConfiguration):
            data = self.best_individual.to_dict()
        elif isinstance(self.best_individual, FormationParameters):
            data = self.best_individual.to_dict()
        elif isinstance(self.best_individual, TacticalParameters):
            data = self.best_individual.to_dict()
        else:
            raise ValueError("Unknown individual type")
        
        data['fitness'] = self.best_fitness
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Best individual saved to {filename}")


if __name__ == '__main__':
    # Example usage
    print("=== Optimizer Test ===\n")
    
    # Setup
    base_formation = FormationPresets.get_formation_2_3_1()
    base_tactics = TacticalParameters()
    
    # Create opponent (standard 3-2-1)
    opponent_formation = FormationPresets.get_formation_3_2_1()
    opponent_config = TeamConfiguration(opponent_formation, base_tactics, team_id=1)
    
    # Create evaluator
    evaluator = FitnessEvaluator(opponent_config, num_games=10)
    
    # Create optimizer
    optimizer = GeneticOptimizer(
        population_size=20,
        mutation_rate=0.15,
        mutation_strength=0.1
    )
    
    # Optimize formation
    print("\n--- Testing Formation Optimization ---")
    best_formation, best_fitness, history = optimizer.optimize_formation(
        base_formation,
        base_tactics,
        evaluator,
        generations=5,
        verbose=True
    )
    
    print(f"\nBest Formation Fitness: {best_fitness:.2f}")

