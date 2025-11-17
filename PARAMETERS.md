# Soccer Simulation Parameters

This document lists all tunable parameters in the soccer simulation, beyond just the X-N-M formations.

## Formation Parameters

1. **FORMATION_FUZZINESS** (0.0-2.0 meters)
   - How much players deviate from their exact formation position
   - Higher = more spread out, less rigid formation
   - Currently: 0.5m, randomized: 0.3-1.0m

2. **FORMATION_ADHERENCE_RATE** (0.0-1.0)
   - How quickly players return to formation position
   - Higher = tighter formation adherence
   - Currently: 0.7, randomized: 0.4-0.9

3. **FORMATION_ELASTICITY** (NEW - 0.0-1.0)
   - Spring constant for formation positioning (elastic system)
   - Higher = stronger pull back to formation
   - Default: 0.5

4. **FORMATION_DAMPING** (NEW - 0.0-1.0)
   - Damping factor to prevent oscillation in formation system
   - Higher = less oscillation, smoother movement
   - Default: 0.3

5. **FORMATION_ADAPTATION_RATE** (NEW - 0.0-1.0)
   - How quickly formation adapts to game state (possession, phase)
   - Higher = faster adaptation
   - Default: 0.2

## Ball Interaction Parameters

6. **BALL_REACTION_DISTANCE** (0.0-15.0 meters)
   - Distance at which players actively pursue ball
   - Currently: 8.0m, randomized: 3.0-10.0m

7. **BALL_ATTRACTION_STRENGTH** (0.0-1.0)
   - How much players are drawn to ball vs formation
   - Higher = more aggressive ball pursuit
   - Currently: 0.5, randomized: 0.2-0.8

8. **BALL_CONTROL_RADIUS** (NEW - 0.0-2.0 meters)
   - Distance at which player has "control" of ball
   - Affects pass accuracy, shot accuracy
   - Default: 0.5m

9. **BALL_STEAL_DISTANCE** (NEW - 0.0-3.0 meters)
   - Maximum distance for successful ball steal
   - Default: 1.0m

10. **BALL_STEAL_STRENGTH** (NEW - 0.0-1.0)
    - Probability of successful steal when in range
    - Default: 0.3

11. **BALL_INTERCEPTION_RANGE** (NEW - 0.0-5.0 meters)
    - Distance players can intercept passes
    - Default: 2.0m

## Player Behavior Parameters

12. **PASS_PROPENSITY_BASE** (0.0-1.0)
    - Base probability of passing vs shooting
    - Currently: 0.6, randomized: 0.4-0.8

13. **SHOOT_PROPENSITY_BASE** (0.0-1.0)
    - Base probability of shooting
    - Currently: 0.3, randomized: 0.2-0.5

14. **DEFLECT_PROPENSITY_BASE** (0.0-1.0)
    - Base probability of deflecting
    - Currently: 0.1, randomized: 0.05-0.2

15. **PASS_DISTANCE_MAX** (0.0-30.0 meters)
    - Maximum distance for a pass
    - Currently: 15.0m

16. **SHOOT_DISTANCE_MAX** (0.0-30.0 meters)
    - Maximum distance for a shot
    - Currently: 20.0m

17. **PASS_ACCURACY_BASE** (NEW - 0.0-1.0)
    - Base pass accuracy (before distance/speed penalties)
    - Default: 0.8

18. **SHOT_ACCURACY_BASE** (NEW - 0.0-1.0)
    - Base shot accuracy (before angle/distance penalties)
    - Default: 0.4

19. **PASS_SPEED_FACTOR** (NEW - 0.0-20.0)
    - Multiplier for pass power
    - Default: 0.6

20. **SHOT_SPEED_FACTOR** (NEW - 0.0-20.0)
    - Multiplier for shot power
    - Default: 1.2

## Physical Parameters

21. **PLAYER_RADIUS** (0.1-0.5 meters)
    - Player body radius for collision detection
    - Currently: 0.3m

22. **PLAYER_SPEED_MAX** (1.0-10.0 m/s)
    - Maximum player movement speed
    - Currently: 5.0 m/s

23. **PLAYER_ACCELERATION** (NEW - 0.0-20.0 m/s²)
    - Player acceleration rate
    - Default: 8.0 m/s²

24. **PLAYER_DECELERATION** (NEW - 0.0-20.0 m/s²)
    - Player deceleration rate
    - Default: 10.0 m/s²

25. **PLAYER_INERTIA** (NEW - 0.0-1.0)
    - How much player momentum carries forward
    - Higher = more momentum, less instant direction changes
    - Default: 0.3

26. **PLAYER_COLLISION_RADIUS** (NEW - 0.3-1.0 meters)
    - Effective collision radius (may be larger than visual radius)
    - Default: 0.5m

27. **PLAYER_REPULSION_STRENGTH** (NEW - 0.0-50.0 N)
    - Force applied when players collide
    - Default: 20.0 N

28. **PLAYER_STAMINA_MAX** (NEW - 0.0-100.0)
    - Maximum player stamina
    - Default: 100.0

29. **PLAYER_STAMINA_DECAY** (NEW - 0.0-10.0 per second)
    - Stamina loss rate during movement
    - Default: 0.5

30. **PLAYER_STAMINA_RECOVERY** (NEW - 0.0-10.0 per second)
    - Stamina recovery rate when stationary
    - Default: 2.0

## Ball Physics Parameters

31. **BALL_RADIUS** (0.05-0.15 meters)
    - Ball radius
    - Currently: 0.11m

32. **BALL_MASS** (0.2-0.6 kg)
    - Ball mass
    - Currently: 0.43 kg

33. **BALL_FRICTION** (0.0-0.1)
    - Friction coefficient
    - Currently: 0.015, randomized: 0.01-0.02

34. **BALL_MAX_SPEED** (10.0-40.0 m/s)
    - Maximum ball speed
    - Currently: 25.0 m/s

35. **BALL_AIR_RESISTANCE** (NEW - 0.0-0.1)
    - Air resistance coefficient
    - Default: 0.005

36. **BALL_BOUNCE_DAMPING** (0.0-1.0)
    - Energy loss on bounce
    - Currently: 0.7, randomized: 0.6-0.8

37. **WALL_BOUNCE_DAMPING** (0.0-1.0)
    - Energy loss on wall bounce
    - Currently: 0.6, randomized: 0.5-0.7

38. **BALL_ANGULAR_MOMENTUM** (NEW - 0.0-1.0)
    - How much ball spins affect trajectory
    - Default: 0.2

## Goalkeeper Parameters

39. **GK_RADIUS** (0.3-0.5 meters)
    - Goalkeeper radius
    - Currently: 0.35m

40. **GK_SPEED_MAX** (3.0-10.0 m/s)
    - Maximum goalkeeper speed
    - Currently: 6.0 m/s

41. **GK_REACTION_TIME** (0.0-1.0 seconds)
    - Time to react to ball
    - Currently: 0.2s

42. **GK_POSITIONING_RANGE** (NEW - 0.0-5.0 meters)
    - How far GK moves from goal center
    - Default: 2.0m

43. **GK_SAVE_PROBABILITY** (NEW - 0.0-1.0)
    - Base probability of making a save when in range
    - Default: 0.7

## Game Rules Parameters

44. **GAME_DURATION_SECONDS** (60-3600 seconds)
    - Game duration
    - Currently: 120s (2 minutes for testing)

45. **TIME_STEP** (0.001-0.1 seconds)
    - Simulation time step
    - Currently: 0.016s (~60 FPS)

46. **POSSESSION_DISTANCE** (0.0-5.0 meters)
    - Distance threshold for possession tracking
    - Currently: 3.0m

## Evolution/RL Parameters

47. **POPULATION_SIZE** (10-1000)
    - Number of formations in population
    - Currently: 50

48. **MUTATION_RATE** (0.0-1.0)
    - Probability of mutation
    - Currently: 0.1

49. **CROSSOVER_RATE** (0.0-1.0)
    - Probability of crossover
    - Currently: 0.7

50. **GENERATIONS** (1-10000)
    - Number of evolution generations
    - Currently: 100

## Visualization Parameters

51. **SLOW_MOTION_FACTOR** (1-100)
    - Visualization speed multiplier
    - Currently: 10

## Summary by Category

- **Formation Control**: 5 parameters (fuzziness, adherence, elasticity, damping, adaptation)
- **Ball Interaction**: 6 parameters (reaction distance, attraction, control, steal, interception)
- **Player Behavior**: 9 parameters (pass/shoot/deflect propensities, distances, accuracies)
- **Physical Properties**: 10 parameters (size, speed, acceleration, collision, stamina)
- **Ball Physics**: 8 parameters (size, mass, friction, damping, air resistance, spin)
- **Goalkeeper**: 5 parameters (size, speed, reaction, positioning, save probability)
- **Game Rules**: 3 parameters (duration, time step, possession)
- **Evolution/RL**: 4 parameters (population, mutation, crossover, generations)
- **Visualization**: 1 parameter (slow motion)

**Total: 51 tunable parameters** (plus formation structure X-N-M)

