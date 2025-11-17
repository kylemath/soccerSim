"""
Pinball-style physics engine for soccer simulation
"""

import numpy as np
from config import *


class Vector2D:
    """2D vector for position and velocity"""
    def __init__(self, x=0.0, y=0.0):
        self.x = float(x)
        self.y = float(y)
    
    def __add__(self, other):
        return Vector2D(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        return Vector2D(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar):
        return Vector2D(self.x * scalar, self.y * scalar)
    
    def __truediv__(self, scalar):
        return Vector2D(self.x / scalar, self.y / scalar)
    
    def magnitude(self):
        return np.sqrt(self.x**2 + self.y**2)
    
    def normalize(self):
        mag = self.magnitude()
        if mag > 0:
            return Vector2D(self.x / mag, self.y / mag)
        return Vector2D(0, 0)
    
    def to_array(self):
        return np.array([self.x, self.y])
    
    def __repr__(self):
        return f"Vector2D({self.x:.2f}, {self.y:.2f})"


class Ball:
    """Ball with physics properties"""
    def __init__(self, x, y):
        self.position = Vector2D(x, y)
        self.velocity = Vector2D(0, 0)
        self.radius = BALL_RADIUS
        self.mass = BALL_MASS
        
    def update(self, dt):
        """Update ball position based on velocity, friction, and air resistance"""
        speed = self.velocity.magnitude()
        if speed > 0:
            # Apply ground friction with random variation (field conditions)
            friction_variation = np.random.uniform(0.95, 1.05)  # ±5% friction variation
            friction_force = BALL_FRICTION * friction_variation * self.mass * 9.81
            friction_deceleration = friction_force / self.mass
            
            # Apply air resistance (proportional to speed squared)
            air_resistance = BALL_AIR_RESISTANCE * speed * speed
            air_deceleration = air_resistance / self.mass
            
            # Total deceleration
            total_deceleration = friction_deceleration + air_deceleration
            new_speed = max(0, speed - total_deceleration * dt)
            
            if new_speed > 0:
                # Add small random drift to ball path (ball imperfections, field irregularities)
                direction = self.velocity.normalize()
                if speed > 1.0:  # Only add drift when ball is moving with some speed
                    # Random angle deviation (very small, max ±2 degrees per frame)
                    angle_deviation = np.random.normal(0, 0.035)  # ~2 degrees in radians
                    cos_a = np.cos(angle_deviation)
                    sin_a = np.sin(angle_deviation)
                    new_dir_x = direction.x * cos_a - direction.y * sin_a
                    new_dir_y = direction.x * sin_a + direction.y * cos_a
                    direction = Vector2D(new_dir_x, new_dir_y).normalize()
                
                self.velocity = direction * new_speed
            else:
                self.velocity = Vector2D(0, 0)
        
        # Update position
        self.position = self.position + self.velocity * dt
        
        # Check boundaries and bounce
        self._check_boundaries()
    
    def _check_boundaries(self):
        """Handle ball bouncing off field boundaries with random variation"""
        bounced = False
        
        # Left/right walls (touchlines)
        if self.position.x - self.radius < 0:
            self.position.x = self.radius
            # Add random variation to bounce (±10% energy retention variation)
            bounce_variation = np.random.uniform(0.9, 1.1)
            self.velocity.x *= -WALL_BOUNCE_DAMPING * bounce_variation
            # Add small random angle change on bounce
            angle_change = np.random.uniform(-0.1, 0.1)
            self.velocity.y += self.velocity.x * angle_change
            bounced = True
        elif self.position.x + self.radius > FIELD_WIDTH:
            self.position.x = FIELD_WIDTH - self.radius
            bounce_variation = np.random.uniform(0.9, 1.1)
            self.velocity.x *= -WALL_BOUNCE_DAMPING * bounce_variation
            angle_change = np.random.uniform(-0.1, 0.1)
            self.velocity.y += self.velocity.x * angle_change
            bounced = True
        
        # Top/bottom walls (goal lines)
        if self.position.y - self.radius < 0:
            self.position.y = self.radius
            bounce_variation = np.random.uniform(0.9, 1.1)
            self.velocity.y *= -WALL_BOUNCE_DAMPING * bounce_variation
            angle_change = np.random.uniform(-0.1, 0.1)
            self.velocity.x += self.velocity.y * angle_change
            bounced = True
        elif self.position.y + self.radius > FIELD_LENGTH:
            self.position.y = FIELD_LENGTH - self.radius
            bounce_variation = np.random.uniform(0.9, 1.1)
            self.velocity.y *= -WALL_BOUNCE_DAMPING * bounce_variation
            angle_change = np.random.uniform(-0.1, 0.1)
            self.velocity.x += self.velocity.y * angle_change
            bounced = True
        
        return bounced
    
    def kick(self, direction, power):
        """Kick the ball in a direction with given power"""
        direction_norm = direction.normalize()
        speed = min(power, BALL_MAX_SPEED)
        
        # Add random error to kick direction (player inaccuracy)
        angle_error = np.random.normal(0, 0.05)  # ~3 degree standard deviation
        cos_e = np.cos(angle_error)
        sin_e = np.sin(angle_error)
        error_dir_x = direction_norm.x * cos_e - direction_norm.y * sin_e
        error_dir_y = direction_norm.x * sin_e + direction_norm.y * cos_e
        direction_norm = Vector2D(error_dir_x, error_dir_y).normalize()
        
        # Add random power variation (±5%)
        power_variation = np.random.uniform(0.95, 1.05)
        speed = min(speed * power_variation, BALL_MAX_SPEED)
        
        # Add some angular momentum effect (spin affects trajectory slightly)
        if BALL_ANGULAR_MOMENTUM > 0:
            # Random spin direction and magnitude
            spin_magnitude = np.random.uniform(0.5, 1.5) * BALL_ANGULAR_MOMENTUM
            # Create a slight perpendicular component based on spin
            perpendicular = Vector2D(-direction_norm.y, direction_norm.x)
            spin_effect = perpendicular * (speed * spin_magnitude * 0.1)
            self.velocity = direction_norm * speed + spin_effect
        else:
            self.velocity = direction_norm * speed
    
    def deflect(self, direction, power):
        """Deflect the ball (slight change in direction)"""
        current_speed = self.velocity.magnitude()
        if current_speed > 0:
            # Blend current direction with new direction
            blend = 0.3  # 30% new direction, 70% current
            current_dir = self.velocity.normalize()
            new_dir = direction.normalize()
            blended_dir = (current_dir * (1 - blend) + new_dir * blend).normalize()
            self.velocity = blended_dir * min(current_speed + power * 0.5, BALL_MAX_SPEED)
        else:
            self.kick(direction, power)
    
    def get_state(self):
        """Get current state for visualization"""
        return {
            'x': self.position.x,
            'y': self.position.y,
            'vx': self.velocity.x,
            'vy': self.velocity.y,
            'speed': self.velocity.magnitude()
        }

