"""
Configuration for 7x7 Indoor Soccer Simulation
Based on half FIFA field (touchline to touchline)
"""

# Field dimensions (meters)
# Half FIFA field: ~52.5m x 68m (but indoor typically smaller)
FIELD_LENGTH = 40.0  # meters (half field typically 40-50m)
FIELD_WIDTH = 30.0   # meters (half field typically 25-30m)

# Goal dimensions
GOAL_WIDTH = 3.0     # meters (standard indoor goal)
GOAL_DEPTH = 1.0     # meters

# Player dimensions
PLAYER_RADIUS = 0.3  # meters (approximate player body radius)
PLAYER_SPEED_MAX = 5.0  # m/s (max player movement speed)
PLAYER_ACCELERATION = 8.0  # m/s² (player acceleration rate)
PLAYER_DECELERATION = 10.0  # m/s² (player deceleration rate)
PLAYER_INERTIA = 0.3  # how much player momentum carries forward (0-1)
PLAYER_COLLISION_RADIUS = 1.2  # effective collision radius (meters) - larger radius prevents clustering
PLAYER_REPULSION_STRENGTH = 150.0  # force applied when players collide (N) - much stronger repulsion
PLAYER_STAMINA_MAX = 100.0  # maximum player stamina
PLAYER_STAMINA_DECAY = 0.5  # stamina loss rate during movement (per second)
PLAYER_STAMINA_RECOVERY = 2.0  # stamina recovery rate when stationary (per second)

# Ball properties
BALL_RADIUS = 0.11   # meters (standard soccer ball)
BALL_MASS = 0.43     # kg
BALL_FRICTION = 0.015  # friction coefficient
BALL_MAX_SPEED = 25.0  # m/s (shot speed limit)
BALL_AIR_RESISTANCE = 0.005  # air resistance coefficient
BALL_ANGULAR_MOMENTUM = 0.2  # how much ball spin affects trajectory (0-1)

# Physics parameters
GRAVITY = 0.0        # 2D simulation (no gravity)
BOUNCE_DAMPING = 0.7  # energy loss on bounce
WALL_BOUNCE_DAMPING = 0.6

# Game rules
GAME_DURATION_SECONDS = 2 * 60  # 2 minutes for initial testing (change to 40*60 for full game)
KICKOFF_X = FIELD_WIDTH / 2   # Center of width (touchline to touchline)
KICKOFF_Y = FIELD_LENGTH / 2  # Center of length (goal line to goal line)
POSSESSION_DISTANCE = 3.0  # distance threshold for possession tracking (meters)

# Field boundaries and rim
FIELD_RIM_HEIGHT = 0.05  # height of rim around field (meters) - ball needs speed to roll over
FIELD_RIM_DAMPING = 0.8  # energy loss when ball hits rim
OUT_OF_BOUNDS_MARGIN = 0.5  # distance beyond field edge to consider out of bounds (meters)

# Restart positions
CORNER_KICK_DISTANCE = 0.5  # distance from corner for corner kick (meters)
GOAL_KICK_Y_DISTANCE = 2.0  # distance from goal line for goal kick (meters)
THROW_IN_X_MARGIN = 1.0  # margin from sideline for throw-in (meters)
RESTART_FREEZE_TIME = 1.0  # time to freeze players before restart (seconds)

# Formation parameters
FORMATION_FUZZINESS = 0.5  # how much players deviate from formation (meters) - allow more deviation
FORMATION_ADHERENCE_RATE = 0.6  # how quickly players return to formation (0-1) - reduced for more free movement
FORMATION_ELASTICITY = 1.5  # spring constant for formation positioning (0-1) - reduced to allow ball pursuit
FORMATION_DAMPING = 0.4  # damping factor to prevent oscillation (0-1) - reduced for more responsive movement
FORMATION_ADAPTATION_RATE = 0.2  # how quickly formation adapts to game state (0-1)
DEFENSIVE_LINE_ADHERENCE = 0.8  # how strongly defenders adhere to defensive line (0-1)
DEFENSIVE_LINE_DEPTH = 0.15  # defensive line follows ball at this depth (fraction of field length)
FORWARD_PUSH_RATE = 0.6  # how much forwards push forward toward ball (0-1)
BALL_REACTION_DISTANCE = 15.0  # distance at which players actively pursue ball (meters) - increased significantly
BALL_BOUNDARY_REACTION_DISTANCE = 20.0  # distance for ball near boundaries (meters) - players always pursue
BALL_ATTRACTION_STRENGTH = 0.8  # how much players are drawn to ball vs formation (0-1) - much stronger ball pursuit
BALL_CLOSE_DISTANCE = 5.0  # distance within which players prioritize ball over formation (meters) - increased
BALL_SLOW_SPEED_THRESHOLD = 2.0  # speed below which ball is considered slow/stationary (m/s)

# Player behavior parameters
PASS_PROPENSITY_BASE = 0.6    # base probability of passing vs shooting
SHOOT_PROPENSITY_BASE = 0.3   # base probability of shooting
DEFLECT_PROPENSITY_BASE = 0.1  # base probability of deflecting
PASS_DISTANCE_MAX = 15.0      # max distance for a pass (meters)
SHOOT_DISTANCE_MAX = 20.0     # max distance for a shot (meters)
PASS_ACCURACY_BASE = 0.8      # base pass accuracy (0-1)
SHOT_ACCURACY_BASE = 0.4      # base shot accuracy (0-1)
PASS_SPEED_FACTOR = 0.6       # multiplier for pass power
SHOT_SPEED_FACTOR = 1.2       # multiplier for shot power
BALL_CONTROL_RADIUS = 0.5     # distance at which player has "control" of ball (meters)
BALL_STEAL_DISTANCE = 1.0      # maximum distance for successful ball steal (meters)
BALL_STEAL_STRENGTH = 0.3      # probability of successful steal when in range (0-1)
BALL_INTERCEPTION_RANGE = 2.0  # distance players can intercept passes (meters)

# Goalkeeper parameters
GK_RADIUS = 0.35     # slightly larger than field players
GK_SPEED_MAX = 6.0   # faster than field players
GK_REACTION_TIME = 0.2  # seconds to react to ball
GK_POSITIONING_RANGE = 2.0  # how far GK moves from goal center (meters)
GK_SAVE_PROBABILITY = 0.7  # base probability of making a save when in range (0-1)

# Randomization parameters (for game variability)
BALL_PATH_RANDOMNESS = 0.035  # random angle deviation per frame (radians, ~2 degrees)
BALL_FRICTION_VARIATION = 0.05  # friction variation (±5%)
BALL_BOUNCE_VARIATION = 0.1  # bounce energy variation (±10%)
BALL_KICK_ANGLE_ERROR = 0.05  # kick direction error standard deviation (radians, ~3 degrees)
BALL_KICK_POWER_VARIATION = 0.05  # kick power variation (±5%)
BALL_SPIN_VARIATION = 0.5  # spin magnitude variation (0.5x to 1.5x)
KICKOFF_POSITION_OFFSET = 0.2  # random kickoff position offset (meters)
RESTART_SPEED_VARIATION = (0.8, 1.2)  # min/max multiplier for restart speeds

# Evolution/RL parameters
POPULATION_SIZE = 50
MUTATION_RATE = 0.1
CROSSOVER_RATE = 0.7
GENERATIONS = 100

# Simulation parameters
TIME_STEP = 0.016    # ~60 FPS
SLOW_MOTION_FACTOR = 10  # visualization speed multiplier

