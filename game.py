"""
Game simulation with physics, players, and rules
"""

import numpy as np
import random
import time
from physics import Ball, Vector2D
from player import Player
from formation import Formation
from config import *


class Team:
    """Team with players and formation"""
    def __init__(self, team_id, formation, is_home=True):
        self.team_id = team_id
        self.formation = formation
        self.is_home = is_home
        self.players = []
        self._create_players()
        formation.apply_to_team(self, is_home)
    
    def _create_players(self):
        """Create 7 players (1 GK + 6 field players)"""
        # Goalkeeper
        gk_pos = (FIELD_WIDTH / 2, 2.0 if self.is_home else FIELD_LENGTH - 2.0)
        gk = Player(self.team_id, 0, gk_pos, role='goalkeeper')
        self.players.append(gk)
        
        # Field players (will be positioned by formation)
        for i in range(1, 7):
            pos = (FIELD_WIDTH / 2, FIELD_LENGTH / 2)  # temporary
            player = Player(self.team_id, i, pos, role='field')
            self.players.append(player)
    
    def get_all_players(self):
        return self.players
    
    def get_field_players(self):
        return [p for p in self.players if p.role == 'field']
    
    def get_goalkeeper(self):
        return [p for p in self.players if p.role == 'goalkeeper'][0]


class Game:
    """Complete game simulation"""
    def __init__(self, team1_formation, team2_formation, game_id=None, random_seed=None):
        self.game_id = game_id
        
        # Set random seed for reproducibility but different each game by default
        if random_seed is None:
            random_seed = int(time.time() * 1000) % (2**32)  # Use current time as seed
        self.random_seed = random_seed
        np.random.seed(random_seed)
        random.seed(random_seed)
        
        self.team1 = Team(0, team1_formation, is_home=True)
        self.team2 = Team(1, team2_formation, is_home=False)
        
        # Ball starts at center with small random offset
        kickoff_offset_x = np.random.uniform(-0.2, 0.2)
        kickoff_offset_y = np.random.uniform(-0.2, 0.2)
        self.ball = Ball(KICKOFF_X + kickoff_offset_x, KICKOFF_Y + kickoff_offset_y)
        
        # Game state
        self.time = 0.0
        self.duration = GAME_DURATION_SECONDS
        self.is_running = True
        self.game_state = 'kickoff'  # 'in_play', 'out_of_bounds', 'goal', 'kickoff', 'throw_in', 'corner_kick', 'goal_kick'
        self.restart_timer = 0.0  # countdown for restart
        self.last_touch_team = -1  # track which team last touched ball
        self.out_of_bounds_location = None  # (x, y) where ball went out
        self.out_of_bounds_type = None  # 'sideline', 'goal_line', 'corner'
        
        # Game phase (4 phases as mentioned by user)
        self.phase = 0  # 0: kickoff, 1: early, 2: mid, 3: late
        
        # Stats
        self.stats = {
            'team1': {
                'goals': 0,
                'shots': 0,
                'passes': 0,
                'possession_time': 0.0,
                'touches': 0
            },
            'team2': {
                'goals': 0,
                'shots': 0,
                'passes': 0,
                'possession_time': 0.0,
                'touches': 0
            },
            'ball_possession': 0,  # 0 = team1, 1 = team2, -1 = neutral
            'last_possession_change': 0.0
        }
        
        # Event log
        self.events = []
    
    def update(self, dt):
        """Update game state"""
        if not self.is_running or self.time >= self.duration:
            self.is_running = False
            return
        
        self.time += dt
        
        # Update game phase
        self._update_phase()
        
        # Handle restart timer
        if self.game_state in ['throw_in', 'corner_kick', 'goal_kick', 'kickoff']:
            self.restart_timer -= dt
            if self.restart_timer <= 0:
                self._execute_restart()
                self.game_state = 'in_play'
        
        # Update ball only if in play
        if self.game_state == 'in_play':
            self.ball.update(dt)
            
            # Check for rim collisions and out of bounds
            self._check_out_of_bounds()
        
        # Update players (but freeze during restart countdown)
        all_players = self.team1.get_all_players() + self.team2.get_all_players()
        if self.game_state == 'in_play' or self.restart_timer < 0.5:  # Allow movement shortly before restart
            for player in all_players:
                teammates = self.team1.get_all_players() if player.team_id == 0 else self.team2.get_all_players()
                opponents = self.team2.get_all_players() if player.team_id == 0 else self.team1.get_all_players()
                player.update(dt, self.ball, teammates, opponents)
        
        # Check for goals
        if self.game_state == 'in_play':
            self._check_goals()
        
        # Update possession and track last touch
        self._update_possession(dt)
        
        # Update stats
        self._update_stats()
    
    def _update_phase(self):
        """Update game phase based on time"""
        phase_duration = self.duration / 4
        self.phase = int(self.time / phase_duration)
        self.phase = min(3, self.phase)
    
    def _check_goals(self):
        """Check if ball enters goal"""
        ball_x, ball_y = self.ball.position.x, self.ball.position.y
        
        # Team 1 goal (y = 0, bottom)
        if ball_y - self.ball.radius <= 0:
            goal_center_x = FIELD_WIDTH / 2
            if abs(ball_x - goal_center_x) < GOAL_WIDTH / 2:
                # Check if goalkeeper saves
                gk = self.team2.get_goalkeeper()
                gk_dist = (self.ball.position - gk.position).magnitude()
                
                if gk_dist > GK_RADIUS + self.ball.radius + 0.5:  # GK too far
                    self.stats['team2']['goals'] += 1
                    self.events.append({
                        'time': self.time,
                        'type': 'goal',
                        'team': 1,
                        'scorer': None
                    })
                    # Reset ball to center for kickoff
                    self.game_state = 'kickoff'
                    self.restart_timer = RESTART_FREEZE_TIME
                    return  # Early return to avoid double processing
            else:
                # Ball hit goal post or went wide - bounce back
                self.ball.position.y = self.ball.radius
                self.ball.velocity.y *= -BOUNCE_DAMPING
        
        # Team 2 goal (y = FIELD_LENGTH, top)
        elif ball_y + self.ball.radius >= FIELD_LENGTH:
            goal_center_x = FIELD_WIDTH / 2
            if abs(ball_x - goal_center_x) < GOAL_WIDTH / 2:
                # Check if goalkeeper saves
                gk = self.team1.get_goalkeeper()
                gk_dist = (self.ball.position - gk.position).magnitude()
                
                if gk_dist > GK_RADIUS + self.ball.radius + 0.5:  # GK too far
                    self.stats['team1']['goals'] += 1
                    self.events.append({
                        'time': self.time,
                        'type': 'goal',
                        'team': 0,
                        'scorer': None
                    })
                    # Reset ball to center
                    self.ball.position = Vector2D(KICKOFF_X, KICKOFF_Y)
                    self.ball.velocity = Vector2D(0, 0)
                    return  # Early return to avoid double processing
            else:
                # Ball hit goal post or went wide - bounce back
                self.ball.position.y = FIELD_LENGTH - self.ball.radius
                self.ball.velocity.y *= -BOUNCE_DAMPING
    
    def _update_possession(self, dt):
        """Track which team has possession"""
        # Find nearest player to ball
        min_dist = float('inf')
        nearest_team = -1
        
        for player in self.team1.get_all_players():
            dist = (player.position - self.ball.position).magnitude()
            if dist < min_dist:
                min_dist = dist
                nearest_team = 0
        
        for player in self.team2.get_all_players():
            dist = (player.position - self.ball.position).magnitude()
            if dist < min_dist:
                min_dist = dist
                nearest_team = 1
        
        # If ball is within possession distance of a player, that team has possession
        if min_dist < POSSESSION_DISTANCE:
            if self.stats['ball_possession'] != nearest_team:
                self.stats['last_possession_change'] = self.time
            self.stats['ball_possession'] = nearest_team
            self.last_touch_team = nearest_team  # Track last touch for restarts
            
            # Update possession time
            if nearest_team == 0:
                self.stats['team1']['possession_time'] += dt
            else:
                self.stats['team2']['possession_time'] += dt
        else:
            self.stats['ball_possession'] = -1
    
    def _update_stats(self):
        """Update game statistics"""
        # Count passes and shots from players
        self.stats['team1']['passes'] = sum(p.passes_made for p in self.team1.get_all_players())
        self.stats['team1']['shots'] = sum(p.shots_taken for p in self.team1.get_all_players())
        self.stats['team1']['touches'] = sum(p.touches for p in self.team1.get_all_players())
        
        self.stats['team2']['passes'] = sum(p.passes_made for p in self.team2.get_all_players())
        self.stats['team2']['shots'] = sum(p.shots_taken for p in self.team2.get_all_players())
        self.stats['team2']['touches'] = sum(p.touches for p in self.team2.get_all_players())
    
    def _check_out_of_bounds(self):
        """Check if ball goes out of bounds with rim physics"""
        ball_x, ball_y = self.ball.position.x, self.ball.position.y
        ball_speed = self.ball.velocity.magnitude()
        
        # Check if ball has enough speed to roll over rim
        can_roll_over = ball_speed > 2.0  # needs some speed to go over rim
        
        # Check sidelines (left/right)
        if ball_x < -OUT_OF_BOUNDS_MARGIN:
            if can_roll_over:
                # Ball went out - throw-in for opposite team
                self.out_of_bounds_location = (0, ball_y)
                self.out_of_bounds_type = 'sideline'
                self.game_state = 'throw_in'
                self.restart_timer = RESTART_FREEZE_TIME
                self.events.append({'time': self.time, 'type': 'throw_in', 'team': 1 - self.last_touch_team if self.last_touch_team >= 0 else 0})
            else:
                # Bounce off rim
                self.ball.position.x = self.ball.radius
                self.ball.velocity.x *= -FIELD_RIM_DAMPING
        elif ball_x > FIELD_WIDTH + OUT_OF_BOUNDS_MARGIN:
            if can_roll_over:
                self.out_of_bounds_location = (FIELD_WIDTH, ball_y)
                self.out_of_bounds_type = 'sideline'
                self.game_state = 'throw_in'
                self.restart_timer = RESTART_FREEZE_TIME
                self.events.append({'time': self.time, 'type': 'throw_in', 'team': 1 - self.last_touch_team if self.last_touch_team >= 0 else 0})
            else:
                self.ball.position.x = FIELD_WIDTH - self.ball.radius
                self.ball.velocity.x *= -FIELD_RIM_DAMPING
        
        # Check goal lines (top/bottom) - already handled in _check_goals for goals
        # Here we handle when ball goes wide of goal
        goal_center_x = FIELD_WIDTH / 2
        goal_left = goal_center_x - GOAL_WIDTH / 2
        goal_right = goal_center_x + GOAL_WIDTH / 2
        
        # Bottom goal line (y=0)
        if ball_y < -OUT_OF_BOUNDS_MARGIN:
            if can_roll_over:
                # Determine if corner kick or goal kick
                if ball_x < goal_left - 2.0 or ball_x > goal_right + 2.0:
                    # Corner kick for attacking team
                    self.out_of_bounds_type = 'corner'
                    self.game_state = 'corner_kick'
                    corner_x = CORNER_KICK_DISTANCE if ball_x < FIELD_WIDTH/2 else FIELD_WIDTH - CORNER_KICK_DISTANCE
                    self.out_of_bounds_location = (corner_x, CORNER_KICK_DISTANCE)
                    self.events.append({'time': self.time, 'type': 'corner_kick', 'team': 1 if self.last_touch_team == 0 else 0})
                else:
                    # Goal kick for defending team
                    self.out_of_bounds_type = 'goal_line'
                    self.game_state = 'goal_kick'
                    self.out_of_bounds_location = (FIELD_WIDTH/2, GOAL_KICK_Y_DISTANCE)
                    self.events.append({'time': self.time, 'type': 'goal_kick', 'team': 0})
                self.restart_timer = RESTART_FREEZE_TIME
            else:
                self.ball.position.y = self.ball.radius
                self.ball.velocity.y *= -FIELD_RIM_DAMPING
        
        # Top goal line (y=FIELD_LENGTH)
        elif ball_y > FIELD_LENGTH + OUT_OF_BOUNDS_MARGIN:
            if can_roll_over:
                if ball_x < goal_left - 2.0 or ball_x > goal_right + 2.0:
                    # Corner kick
                    self.out_of_bounds_type = 'corner'
                    self.game_state = 'corner_kick'
                    corner_x = CORNER_KICK_DISTANCE if ball_x < FIELD_WIDTH/2 else FIELD_WIDTH - CORNER_KICK_DISTANCE
                    self.out_of_bounds_location = (corner_x, FIELD_LENGTH - CORNER_KICK_DISTANCE)
                    self.events.append({'time': self.time, 'type': 'corner_kick', 'team': 0 if self.last_touch_team == 1 else 1})
                else:
                    # Goal kick
                    self.out_of_bounds_type = 'goal_line'
                    self.game_state = 'goal_kick'
                    self.out_of_bounds_location = (FIELD_WIDTH/2, FIELD_LENGTH - GOAL_KICK_Y_DISTANCE)
                    self.events.append({'time': self.time, 'type': 'goal_kick', 'team': 1})
                self.restart_timer = RESTART_FREEZE_TIME
            else:
                self.ball.position.y = FIELD_LENGTH - self.ball.radius
                self.ball.velocity.y *= -FIELD_RIM_DAMPING
    
    def _execute_restart(self):
        """Execute the restart (throw-in, corner, goal kick, or kickoff) with randomization"""
        if self.game_state == 'kickoff':
            # Place ball at center with small random offset
            offset_x = np.random.uniform(-0.1, 0.1)
            offset_y = np.random.uniform(-0.1, 0.1)
            self.ball.position = Vector2D(KICKOFF_X + offset_x, KICKOFF_Y + offset_y)
            self.ball.velocity = Vector2D(0, 0)
        elif self.game_state in ['throw_in', 'corner_kick', 'goal_kick']:
            # Place ball at out of bounds location
            if self.out_of_bounds_location:
                self.ball.position = Vector2D(*self.out_of_bounds_location)
                self.ball.velocity = Vector2D(0, 0)
                # Give ball small initial velocity toward field with randomization
                if self.game_state == 'throw_in':
                    # Throw in with random velocity and angle
                    direction_x = 1.0 if self.out_of_bounds_location[0] == 0 else -1.0
                    speed = np.random.uniform(2.5, 4.0)  # Random throw strength
                    angle = np.random.uniform(-0.3, 0.3)  # Random angle variation
                    self.ball.velocity = Vector2D(direction_x * speed, speed * np.tan(angle))
                elif self.game_state == 'corner_kick':
                    # Corner kick toward goal with randomization
                    # Random target point near goal
                    target_x = FIELD_WIDTH/2 + np.random.uniform(-3.0, 3.0)
                    target_y = FIELD_LENGTH/2 + np.random.uniform(-5.0, 5.0)
                    direction = Vector2D(target_x - self.ball.position.x, target_y - self.ball.position.y).normalize()
                    speed = np.random.uniform(4.0, 7.0)  # Random kick strength
                    self.ball.velocity = direction * speed
                elif self.game_state == 'goal_kick':
                    # Goal kick toward midfield with randomization
                    direction_y = 1.0 if self.out_of_bounds_location[1] < FIELD_LENGTH/2 else -1.0
                    speed = np.random.uniform(6.0, 10.0)  # Random kick strength
                    # Add random lateral component
                    lateral = np.random.uniform(-2.0, 2.0)
                    self.ball.velocity = Vector2D(lateral, direction_y * speed)
    
    def get_state(self):
        """Get current game state for visualization"""
        return {
            'time': self.time,
            'time_remaining': max(0, self.duration - self.time),
            'phase': self.phase,
            'game_state': self.game_state,
            'restart_timer': self.restart_timer,
            'ball': self.ball.get_state(),
            'team1_players': [p.get_state() for p in self.team1.get_all_players()],
            'team2_players': [p.get_state() for p in self.team2.get_all_players()],
            'stats': self.stats.copy(),
            'score': {
                'team1': self.stats['team1']['goals'],
                'team2': self.stats['team2']['goals']
            }
        }
    
    def run_full_game(self):
        """Run complete game simulation"""
        while self.is_running and self.time < self.duration:
            self.update(TIME_STEP)
        
        return self.get_final_stats()
    
    def get_final_stats(self):
        """Get final game statistics"""
        return {
            'game_id': self.game_id,
            'duration': self.time,
            'final_score': {
                'team1': self.stats['team1']['goals'],
                'team2': self.stats['team2']['goals']
            },
            'team1_stats': self.stats['team1'].copy(),
            'team2_stats': self.stats['team2'].copy(),
            'events': self.events,
            'team1_formation': self.team1.formation.name,
            'team2_formation': self.team2.formation.name
        }

