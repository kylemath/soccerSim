"""
Player entity with behaviors and formation adherence
"""

import numpy as np
from physics import Vector2D
from config import (
    FIELD_WIDTH, FIELD_LENGTH, PLAYER_RADIUS, GK_RADIUS, PLAYER_SPEED_MAX, GK_SPEED_MAX,
    FORMATION_FUZZINESS, FORMATION_ADHERENCE_RATE, FORMATION_ELASTICITY, FORMATION_DAMPING,
    FORMATION_ADAPTATION_RATE, DEFENSIVE_LINE_ADHERENCE, DEFENSIVE_LINE_DEPTH, FORWARD_PUSH_RATE,
    PASS_PROPENSITY_BASE, SHOOT_PROPENSITY_BASE, DEFLECT_PROPENSITY_BASE, PASS_DISTANCE_MAX,
    SHOOT_DISTANCE_MAX, BALL_REACTION_DISTANCE, BALL_BOUNDARY_REACTION_DISTANCE,
    BALL_ATTRACTION_STRENGTH, BALL_CLOSE_DISTANCE, PLAYER_ACCELERATION, PLAYER_DECELERATION, PLAYER_INERTIA,
    PLAYER_COLLISION_RADIUS, PLAYER_REPULSION_STRENGTH, PLAYER_STAMINA_MAX,
    PLAYER_STAMINA_DECAY, PLAYER_STAMINA_RECOVERY, PASS_ACCURACY_BASE, SHOT_ACCURACY_BASE,
    PASS_SPEED_FACTOR, SHOT_SPEED_FACTOR, BALL_CONTROL_RADIUS, BALL_STEAL_DISTANCE,
    BALL_STEAL_STRENGTH, BALL_INTERCEPTION_RANGE, GK_POSITIONING_RANGE
)


class Player:
    """Individual player with position, behavior, and formation role"""
    def __init__(self, team_id, player_id, position, role='field'):
        self.team_id = team_id
        self.player_id = player_id
        self.role = role  # 'field', 'goalkeeper'
        self.base_position = Vector2D(position[0], position[1])  # base formation position
        self.original_base_position = Vector2D(position[0], position[1])  # original unadapted position
        
        # Add small random offset to starting position for variability
        start_offset_x = np.random.uniform(-0.3, 0.3)
        start_offset_y = np.random.uniform(-0.3, 0.3)
        self.position = Vector2D(position[0] + start_offset_x, position[1] + start_offset_y)  # current position
        
        # Position role will be determined after formation is set
        self.position_role = None
        
        # Behavior propensities (with random variation)
        self.pass_propensity = max(0, PASS_PROPENSITY_BASE + np.random.normal(0, 0.1))
        self.shoot_propensity = max(0, SHOOT_PROPENSITY_BASE + np.random.normal(0, 0.1))
        self.deflect_propensity = max(0, DEFLECT_PROPENSITY_BASE + np.random.normal(0, 0.05))
        
        # Normalize propensities to sum to 1
        total = self.pass_propensity + self.shoot_propensity + self.deflect_propensity
        if total > 0:
            self.pass_propensity /= total
            self.shoot_propensity /= total
            self.deflect_propensity /= total
        else:
            # Fallback if all are negative (shouldn't happen, but safety)
            self.pass_propensity = PASS_PROPENSITY_BASE
            self.shoot_propensity = SHOOT_PROPENSITY_BASE
            self.deflect_propensity = DEFLECT_PROPENSITY_BASE
            total = self.pass_propensity + self.shoot_propensity + self.deflect_propensity
            self.pass_propensity /= total
            self.shoot_propensity /= total
            self.deflect_propensity /= total
        
        # Physical properties with random variation
        self.radius = GK_RADIUS if role == 'goalkeeper' else PLAYER_RADIUS
        # Add ±10% variation to max speed for player diversity
        base_speed = GK_SPEED_MAX if role == 'goalkeeper' else PLAYER_SPEED_MAX
        self.max_speed = base_speed * np.random.uniform(0.9, 1.1)
        self.velocity = Vector2D(0, 0)
        self.acceleration = PLAYER_ACCELERATION
        self.deceleration = PLAYER_DECELERATION
        self.inertia = PLAYER_INERTIA
        self.collision_radius = PLAYER_COLLISION_RADIUS
        
        # Formation adherence (elastic system)
        self.fuzziness = FORMATION_FUZZINESS * (1 + np.random.normal(0, 0.2))
        self.adherence_rate = FORMATION_ADHERENCE_RATE
        self.elasticity = FORMATION_ELASTICITY
        self.damping = FORMATION_DAMPING
        self.formation_velocity = Vector2D(0, 0)  # Velocity for elastic system
        
        # Stamina system
        self.stamina = PLAYER_STAMINA_MAX
        self.max_stamina = PLAYER_STAMINA_MAX
        self.effective_max_speed = self.max_speed  # Will be updated by stamina
        
        # Ball control
        self.has_ball_control = False
        
        # Stats
        self.passes_made = 0
        self.shots_taken = 0
        self.touches = 0
        self.steals = 0
        
    def update(self, dt, ball, teammates, opponents):
        """Update player position and behavior"""
        # Update stamina
        self._update_stamina(dt)
        
        # Check for collisions with other players (repulsion)
        all_players = teammates + opponents
        self._handle_collisions(all_players, dt)
        
        # Check if opponent can steal ball
        if self.has_ball_control:
            self._check_ball_steal(ball, opponents, dt)
        
        # Check for ball interception
        self._check_interception(ball, teammates, opponents, dt)
        
        distance_to_ball = (self.position - ball.position).magnitude()
        
        # Update ball control status
        self.has_ball_control = distance_to_ball < BALL_CONTROL_RADIUS
        
        # Adapt formation position based on ball position
        self._adapt_formation_to_ball(ball)
        
        # Check if ball is near boundaries - always pursue
        ball_near_boundary = self._is_ball_near_boundary(ball)
        reaction_distance = BALL_BOUNDARY_REACTION_DISTANCE if ball_near_boundary else BALL_REACTION_DISTANCE
        
        # Balance between formation adherence and ball attraction
        if distance_to_ball < reaction_distance:
            # Move toward ball with strength based on distance and attraction parameter
            self._react_to_ball_position(ball, dt, distance_to_ball, reaction_distance)
        
        # Formation adherence movement - allow players to break formation to get ball
        # When ball is very close, prioritize ball retrieval over formation
        if distance_to_ball >= reaction_distance:
            ball_influence = 1.0  # Full formation adherence when ball is far
        elif distance_to_ball < BALL_CLOSE_DISTANCE:
            # Ball is very close - almost no formation adherence, prioritize ball retrieval
            ball_influence = 0.01  # Only 1% formation adherence when ball is very close (was 10%)
        else:
            # Calculate how close ball is (0.0 = touching, 1.0 = at edge of reaction distance)
            closeness = (distance_to_ball - BALL_CLOSE_DISTANCE) / (reaction_distance - BALL_CLOSE_DISTANCE)
            closeness = max(0.0, min(1.0, closeness))  # Clamp between 0 and 1
            
            # Gradually increase formation adherence as ball gets farther
            # When ball is at BALL_CLOSE_DISTANCE, ball_influence = 0.01
            # When ball is at reaction_distance, ball_influence = 0.7
            ball_influence = 0.01 + (closeness * 0.69)  # Range from 0.01 to 0.7
            
            # If ball is near boundary, reduce formation adherence even more to pursue ball
            if ball_near_boundary:
                ball_influence *= 0.2  # Even less formation adherence when ball near boundary
        
        # Elastic formation system (adds to velocity)
        self._adhere_to_formation_elastic(dt, ball_influence)
        
        # Apply acceleration/deceleration with inertia and update position
        self._apply_movement_physics(dt)
        
        # Keep within field bounds
        self.position.x = max(self.radius, min(FIELD_WIDTH - self.radius, self.position.x))
        self.position.y = max(self.radius, min(FIELD_LENGTH - self.radius, self.position.y))
        
        # Act on ball if touching
        if distance_to_ball < self.radius + ball.radius + 0.1:  # touching ball
            self._react_to_ball(ball, teammates, opponents, dt)
    
    def _react_to_ball_position(self, ball, dt, distance_to_ball, reaction_distance):
        """Move toward ball when it's nearby - stronger pursuit when ball is close"""
        to_ball = ball.position - self.position
        direction = to_ball.normalize()
        
        if direction.magnitude() > 0:
            # Attraction strength increases dramatically as ball gets closer
            # When ball is very close (within BALL_CLOSE_DISTANCE), move at full speed
            # When ball is at edge of reaction distance, move at reduced speed
            if distance_to_ball < BALL_CLOSE_DISTANCE:
                # Ball is very close - move at maximum speed to retrieve it
                distance_factor = 1.0
                base_speed = 1.0  # 100% speed when ball is very close
            else:
                # Ball is farther - gradual speed increase as it gets closer
                distance_factor = max(0, 1.0 - (distance_to_ball - BALL_CLOSE_DISTANCE) / (reaction_distance - BALL_CLOSE_DISTANCE))
                # Minimum 60% speed, up to 100% when approaching BALL_CLOSE_DISTANCE
                base_speed = 0.6 + (distance_factor * 0.4)  # 60% to 100% of max speed
            
            # Attraction multiplier - stronger overall with increased BALL_ATTRACTION_STRENGTH
            attraction_multiplier = 0.7 + (BALL_ATTRACTION_STRENGTH * 0.3)  # 0.7 to 1.0
            
            # Apply stamina effect
            stamina_factor = 0.5 + 0.5 * (self.stamina / self.max_stamina)
            target_speed = self.effective_max_speed * base_speed * attraction_multiplier * stamina_factor
            
            # Update velocity toward ball (acceleration-based)
            target_velocity = direction * target_speed
            velocity_diff = target_velocity - self.velocity
            if velocity_diff.magnitude() > 0:
                acceleration_dir = velocity_diff.normalize()
                # Increase acceleration when ball is close for more responsive movement
                accel_multiplier = 1.5 if distance_to_ball < BALL_CLOSE_DISTANCE else 1.0
                accel_magnitude = min(self.acceleration * accel_multiplier, velocity_diff.magnitude() / max(dt, 0.001))
                self.velocity = self.velocity + acceleration_dir * accel_magnitude * dt
    
    def _is_ball_near_boundary(self, ball):
        """Check if ball is near field boundaries"""
        boundary_threshold = 3.0  # meters from boundary
        return (ball.position.x < boundary_threshold or 
                ball.position.x > FIELD_WIDTH - boundary_threshold or
                ball.position.y < boundary_threshold or 
                ball.position.y > FIELD_LENGTH - boundary_threshold)
    
    def _adapt_formation_to_ball(self, ball):
        """Adapt formation position based on ball position"""
        # Skip if position role not yet determined
        if self.position_role is None:
            return
        
        # Team 0 defends bottom (y=0), Team 1 defends top (y=FIELD_LENGTH)
        defending_y = 0.0 if self.team_id == 0 else FIELD_LENGTH
        attacking_y = FIELD_LENGTH if self.team_id == 0 else 0.0
        
        if self.position_role == 'goalkeeper':
            # Goalkeeper positions relative to ball but stays near goal
            goal_y = defending_y
            goal_center_x = FIELD_WIDTH / 2
            
            # Move goalkeeper horizontally toward ball, but limit range
            ball_x = ball.position.x
            gk_x = goal_center_x + np.clip(ball_x - goal_center_x, -GK_POSITIONING_RANGE, GK_POSITIONING_RANGE)
            
            # Goalkeeper stays near goal line but can move slightly forward
            gk_y = goal_y + (2.0 if self.team_id == 0 else -2.0)  # Slightly forward from goal line
            
            self.base_position = Vector2D(gk_x, gk_y)
            
        elif self.position_role == 'defender':
            # Defenders: defensive line follows ball at fixed depth
            # Calculate defensive line Y position based on ball
            ball_y = ball.position.y
            
            # Defensive line follows ball but maintains depth
            if self.team_id == 0:
                # Home team: defensive line is behind ball (toward y=0)
                defensive_line_y = max(ball_y - DEFENSIVE_LINE_DEPTH * FIELD_LENGTH, 2.0)
            else:
                # Away team: defensive line is behind ball (toward y=FIELD_LENGTH)
                defensive_line_y = min(ball_y + DEFENSIVE_LINE_DEPTH * FIELD_LENGTH, FIELD_LENGTH - 2.0)
            
            # Keep original X position but adapt Y to defensive line
            original_x = self.original_base_position.x
            self.base_position = Vector2D(original_x, defensive_line_y)
            
        elif self.position_role == 'forward':
            # Forwards: push forward toward ball from striker position
            ball_y = ball.position.y
            original_y = self.original_base_position.y
            
            # Calculate how much to push forward toward opponent goal
            if self.team_id == 0:
                # Home team: attack toward y=0 (opponent goal)
                # Push forward (toward y=0) when ball is in attacking half
                if ball_y < FIELD_LENGTH / 2:  # Ball in attacking half
                    push_distance = (FIELD_LENGTH / 2 - ball_y) * FORWARD_PUSH_RATE
                    target_y = max(original_y - push_distance, 2.0)  # Push forward
                else:
                    target_y = original_y  # Stay back when ball is defensive
            else:
                # Away team: attack toward y=FIELD_LENGTH (opponent goal)
                # Push forward (toward y=FIELD_LENGTH) when ball is in attacking half
                if ball_y > FIELD_LENGTH / 2:  # Ball in attacking half
                    push_distance = (ball_y - FIELD_LENGTH / 2) * FORWARD_PUSH_RATE
                    target_y = min(original_y + push_distance, FIELD_LENGTH - 2.0)  # Push forward
                else:
                    target_y = original_y  # Stay back when ball is defensive
            
            # Keep original X position but adapt Y forward
            original_x = self.original_base_position.x
            self.base_position = Vector2D(original_x, target_y)
            
        else:  # midfielder
            # Midfielders: adapt to ball position but less aggressively
            ball_y = ball.position.y
            original_y = self.original_base_position.y
            
            # Move toward ball but maintain midfield position
            adaptation = FORMATION_ADAPTATION_RATE * (ball_y - original_y) * 0.3
            adapted_y = original_y + adaptation
            
            # Keep original X
            original_x = self.original_base_position.x
            self.base_position = Vector2D(original_x, adapted_y)
    
    def _update_stamina(self, dt):
        """Update player stamina based on movement"""
        current_speed = self.velocity.magnitude()
        if current_speed > 0.1:  # Moving
            self.stamina = max(0, self.stamina - PLAYER_STAMINA_DECAY * dt)
        else:  # Stationary
            self.stamina = min(self.max_stamina, self.stamina + PLAYER_STAMINA_RECOVERY * dt)
        
        # Stamina affects max speed
        stamina_factor = 0.5 + 0.5 * (self.stamina / self.max_stamina)  # 50% to 100% speed
        self.effective_max_speed = self.max_speed * stamina_factor
    
    def _handle_collisions(self, all_players, dt):
        """Handle collisions with other players (repulsion) - aggressive spacing"""
        total_repulsion = Vector2D(0, 0)
        
        for other in all_players:
            if other.player_id == self.player_id and other.team_id == self.team_id:
                continue  # Skip self
            
            distance = (self.position - other.position).magnitude()
            min_distance = self.collision_radius + other.collision_radius
            
            if distance > 0 and distance < min_distance * 1.5:  # Apply repulsion even before full overlap
                # Calculate repulsion force
                direction = (self.position - other.position).normalize()
                
                if distance < min_distance:
                    # Overlapping - strong repulsion
                    overlap = min_distance - distance
                    repulsion_force = PLAYER_REPULSION_STRENGTH * (1.0 + overlap * 2.0)  # Much stronger when overlapping
                else:
                    # Close but not overlapping - proactive spacing
                    closeness = 1.0 - (distance / (min_distance * 1.5))
                    repulsion_force = PLAYER_REPULSION_STRENGTH * closeness * 0.5  # Weaker but still present
                
                repulsion_acceleration = repulsion_force / 1.0  # Assume mass = 1
                repulsion_vector = direction * repulsion_acceleration * dt
                total_repulsion = total_repulsion + repulsion_vector
        
        # Apply total repulsion
        if total_repulsion.magnitude() > 0:
            self.position = self.position + total_repulsion
            # Also push away in velocity more aggressively
            self.velocity = self.velocity + total_repulsion * 2.0  # Stronger velocity push
    
    def _check_ball_steal(self, ball, opponents, dt):
        """Check if opponent can steal the ball"""
        for opponent in opponents:
            distance_to_opponent = (self.position - opponent.position).magnitude()
            if distance_to_opponent < BALL_STEAL_DISTANCE:
                # Opponent attempts steal
                if np.random.random() < BALL_STEAL_STRENGTH:
                    # Successful steal
                    opponent.steals += 1
                    self.has_ball_control = False
                    # Ball is knocked away
                    steal_direction = (ball.position - self.position).normalize()
                    ball.velocity = steal_direction * ball.velocity.magnitude() * 0.5
    
    def _check_interception(self, ball, teammates, opponents, dt):
        """Check if player can intercept a moving ball"""
        if ball.velocity.magnitude() < 1.0:  # Ball not moving fast enough
            return
        
        # Check if ball trajectory passes near player
        ball_speed = ball.velocity.magnitude()
        ball_direction = ball.velocity.normalize()
        
        # Project ball position forward
        future_ball_pos = ball.position + ball_direction * ball_speed * dt * 5  # Look 5 steps ahead
        
        # Check if player is in interception range
        distance_to_trajectory = (self.position - ball.position).magnitude()
        if distance_to_trajectory < BALL_INTERCEPTION_RANGE:
            # Move toward interception point
            to_intercept = future_ball_pos - self.position
            intercept_direction = to_intercept.normalize()
            if intercept_direction.magnitude() > 0:
                intercept_speed = min(self.max_speed * 0.8, distance_to_trajectory / max(dt, 0.001))
                intercept_velocity = intercept_direction * intercept_speed
                self.velocity = self.velocity + intercept_velocity * dt * 0.3
    
    def _adhere_to_formation_elastic(self, dt, ball_influence=1.0):
        """Elastic formation system with damping - strong pull to formation position"""
        # Calculate displacement from formation position
        displacement = self.base_position - self.position
        distance = displacement.magnitude()
        
        if distance > 0:
            direction = displacement.normalize()
            
            # For defenders, add extra adherence to defensive line
            adherence_multiplier = 1.0
            if self.position_role == 'defender':
                adherence_multiplier = 1.0 + DEFENSIVE_LINE_ADHERENCE  # Extra pull for defenders
            elif self.position_role is None:
                # Fallback if role not determined yet
                adherence_multiplier = 1.0
            
            # Strong elastic force (spring force): F = -kx
            # But scale down dramatically when ball is close (ball_influence is small)
            elastic_force = self.elasticity * distance * ball_influence * adherence_multiplier
            
            # Damping force: F = -cv (opposes velocity)
            damping_force = self.damping * self.formation_velocity.magnitude()
            
            # Net force direction - ensure always pulling toward formation
            force_magnitude = max(0, elastic_force - damping_force)
            force = direction * force_magnitude
            
            # Update formation velocity (acceleration = force)
            self.formation_velocity = self.formation_velocity + force * dt
            
            # Apply damping to formation velocity
            self.formation_velocity = self.formation_velocity * (1.0 - self.damping * dt)
            
            # Strong formation contribution - high adherence rate means strong pull
            # But reduce dramatically when ball is close
            adherence_weight = self.adherence_rate * ball_influence * adherence_multiplier
            formation_contribution = self.formation_velocity * adherence_weight
            
            # Directly add to velocity - this is the primary movement toward formation
            self.velocity = self.velocity + formation_contribution
            
            # Also directly move toward formation if far away (stronger than elastic system alone)
            # But only when ball is not nearby (ball_influence is high)
            if distance > self.fuzziness * 2.0 and ball_influence > 0.5:  # Very far from formation AND ball is not close
                direct_pull = direction * self.max_speed * self.adherence_rate * 0.8 * adherence_multiplier * ball_influence * dt
                self.position = self.position + direct_pull
            
            # Add minimal random variation only when very close to formation
            if distance < self.fuzziness * 0.5:
                wander_strength = 0.1 * ball_influence  # Reduced wandering
                random_wander = Vector2D(
                    np.random.normal(0, wander_strength),
                    np.random.normal(0, wander_strength)
                )
                self.velocity = self.velocity + random_wander * dt * 0.5
        else:
            # Reset formation velocity when at target
            self.formation_velocity = Vector2D(0, 0)
    
    def _apply_movement_physics(self, dt):
        """Apply acceleration/deceleration with inertia and update position"""
        current_speed = self.velocity.magnitude()
        
        # Limit velocity to effective max speed (considering stamina)
        if current_speed > self.effective_max_speed:
            self.velocity = self.velocity.normalize() * self.effective_max_speed
        
        # Apply inertia: smooth velocity changes
        # (Velocity already updated by ball reaction and formation)
        
        # Update position based on velocity
        self.position = self.position + self.velocity * dt
        
        # Apply friction/deceleration when not actively accelerating
        if current_speed > 0.1:
            decel_factor = 1.0 - (self.deceleration * dt / max(current_speed, 0.1))
            self.velocity = self.velocity * max(0, decel_factor)
    
    def _react_to_ball(self, ball, teammates, opponents, dt):
        """Decide action when ball is nearby"""
        distance_to_ball = (self.position - ball.position).magnitude()
        
        if distance_to_ball < self.radius + ball.radius + 0.1:  # touching ball
            self.touches += 1
            
            # Decide action based on propensities
            action = np.random.choice(
                ['pass', 'shoot', 'deflect'],
                p=[self.pass_propensity, self.shoot_propensity, self.deflect_propensity]
            )
            
            if action == 'pass':
                self._pass_ball(ball, teammates)
            elif action == 'shoot':
                self._shoot_ball(ball)
            else:
                self._deflect_ball(ball)
    
    def _pass_ball(self, ball, teammates):
        """Pass to nearest teammate with accuracy"""
        self.passes_made += 1
        
        # Find nearest teammate
        nearest = None
        min_dist = float('inf')
        for teammate in teammates:
            if teammate.player_id != self.player_id:
                dist = (teammate.position - self.position).magnitude()
                if dist < min_dist and dist < PASS_DISTANCE_MAX:
                    min_dist = dist
                    nearest = teammate
        
        if nearest:
            direction = nearest.position - self.position
            distance = direction.magnitude()
            
            # Calculate pass accuracy based on distance and base accuracy
            distance_penalty = min(1.0, distance / PASS_DISTANCE_MAX)  # 0-1
            accuracy = PASS_ACCURACY_BASE * (1.0 - distance_penalty * 0.3)  # Lose up to 30% accuracy
            
            # Apply accuracy: add random error
            if np.random.random() > accuracy:
                # Inaccurate pass - add error
                error_angle = np.random.normal(0, 0.2)  # radians
                cos_a, sin_a = np.cos(error_angle), np.sin(error_angle)
                direction = Vector2D(
                    direction.x * cos_a - direction.y * sin_a,
                    direction.x * sin_a + direction.y * cos_a
                )
            
            power = min(12.0, distance * PASS_SPEED_FACTOR)
            ball.kick(direction, power)
            self.has_ball_control = False
        else:
            # Random pass forward (toward opponent's goal)
            # Team 0 shoots toward y=0, Team 1 shoots toward y=FIELD_LENGTH
            direction = Vector2D(0, -1 if self.team_id == 0 else 1)
            ball.kick(direction, 5.0 * PASS_SPEED_FACTOR)
            self.has_ball_control = False
    
    def _shoot_ball(self, ball):
        """Shoot toward goal with accuracy based on angle and distance"""
        self.shots_taken += 1
        
        # Determine goal position (opponent's goal)
        # Team 0 (home) goal is at y=0, so they shoot toward y=0
        # Team 1 (away) goal is at y=FIELD_LENGTH, so they shoot toward y=FIELD_LENGTH
        goal_y = 0.0 if self.team_id == 0 else FIELD_LENGTH
        goal_center = Vector2D(FIELD_WIDTH / 2, goal_y)
        
        direction = goal_center - self.position
        distance = direction.magnitude()
        
        if distance < SHOOT_DISTANCE_MAX:
            # Calculate shot accuracy based on distance and angle
            distance_penalty = min(1.0, distance / SHOOT_DISTANCE_MAX)  # 0-1
            
            # Angle penalty: shots from wider angles are less accurate
            angle_to_goal = abs(np.arctan2(direction.x, abs(direction.y)))
            angle_penalty = min(1.0, angle_to_goal / (np.pi / 3))  # Penalty up to 60 degrees
            
            # Combined accuracy
            accuracy = SHOT_ACCURACY_BASE * (1.0 - distance_penalty * 0.4) * (1.0 - angle_penalty * 0.3)
            
            # Apply accuracy: add random error if inaccurate
            if np.random.random() > accuracy:
                # Inaccurate shot - add error
                error_angle = np.random.normal(0, 0.15)  # radians
                cos_a, sin_a = np.cos(error_angle), np.sin(error_angle)
                direction = Vector2D(
                    direction.x * cos_a - direction.y * sin_a,
                    direction.x * sin_a + direction.y * cos_a
                )
            
            power = min(20.0, 10.0 + distance * SHOT_SPEED_FACTOR * 0.5)
            ball.kick(direction, power)
            self.has_ball_control = False
    
    def _deflect_ball(self, ball):
        """Deflect ball slightly"""
        # Deflect in random direction or toward goal
        goal_y = 0.0 if self.team_id == 0 else FIELD_LENGTH
        goal_center = Vector2D(FIELD_WIDTH / 2, goal_y)
        direction = goal_center - self.position
        
        # Add significant randomness
        direction.x += np.random.normal(0, 1.0)
        direction.y += np.random.normal(0, 1.0)
        
        power = ball.velocity.magnitude() * 0.3  # 30% of current speed
        ball.deflect(direction, power)
    
    def set_formation_position(self, x, y):
        """Update formation position"""
        self.base_position = Vector2D(x, y)
        self.original_base_position = Vector2D(x, y)  # Also update original for adaptation
        
        # Determine player role based on Y position (defender, midfielder, forward)
        if self.position_role is None:
            if self.role == 'goalkeeper':
                self.position_role = 'goalkeeper'
            else:
                # Team 0 defends bottom (y=0), Team 1 defends top (y=FIELD_LENGTH)
                if self.team_id == 0:
                    # Home team: defenders near y=0, forwards near y=FIELD_LENGTH
                    normalized_y = y / FIELD_LENGTH
                else:
                    # Away team: defenders near y=FIELD_LENGTH, forwards near y=0
                    normalized_y = (FIELD_LENGTH - y) / FIELD_LENGTH
                
                if normalized_y < 0.35:
                    self.position_role = 'defender'
                elif normalized_y < 0.65:
                    self.position_role = 'midfielder'
                else:
                    self.position_role = 'forward'
    
    def get_state(self):
        """Get current state for visualization"""
        return {
            'x': self.position.x,
            'y': self.position.y,
            'team': self.team_id,
            'id': self.player_id,
            'role': self.role,
            'passes': self.passes_made,
            'shots': self.shots_taken,
            'touches': self.touches
        }

