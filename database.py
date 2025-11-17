"""
Database models for storing games and results
"""

from sqlalchemy import create_engine, Column, Integer, Float, String, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json

Base = declarative_base()


class GameRecord(Base):
    """Database model for game results"""
    __tablename__ = 'games'
    
    id = Column(Integer, primary_key=True)
    game_id = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Formations
    team1_formation = Column(String)
    team2_formation = Column(String)
    team1_formation_data = Column(JSON)  # Store formation positions
    team2_formation_data = Column(JSON)
    
    # Final score
    team1_goals = Column(Integer)
    team2_goals = Column(Integer)
    
    # Statistics
    team1_stats = Column(JSON)  # passes, shots, possession_time, touches
    team2_stats = Column(JSON)
    
    # Game events
    events = Column(JSON)
    
    # Duration
    duration = Column(Float)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'game_id': self.game_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'team1_formation': self.team1_formation,
            'team2_formation': self.team2_formation,
            'team1_formation_data': self.team1_formation_data,
            'team2_formation_data': self.team2_formation_data,
            'team1_goals': self.team1_goals,
            'team2_goals': self.team2_goals,
            'team1_stats': self.team1_stats,
            'team2_stats': self.team2_stats,
            'events': self.events,
            'duration': self.duration
        }


class Database:
    """Database interface"""
    def __init__(self, db_path='soccer_sim.db'):
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    
    def save_game(self, game_result):
        """Save game result to database"""
        record = GameRecord(
            game_id=game_result.get('game_id', f"game_{datetime.now().timestamp()}"),
            team1_formation=game_result.get('team1_formation'),
            team2_formation=game_result.get('team2_formation'),
            team1_goals=game_result['final_score']['team1'],
            team2_goals=game_result['final_score']['team2'],
            team1_stats=game_result['team1_stats'],
            team2_stats=game_result['team2_stats'],
            events=game_result.get('events', []),
            duration=game_result.get('duration', 0)
        )
        
        self.session.add(record)
        self.session.commit()
        return record.id
    
    def get_all_games(self):
        """Get all games"""
        return [g.to_dict() for g in self.session.query(GameRecord).all()]
    
    def get_game(self, game_id):
        """Get specific game"""
        game = self.session.query(GameRecord).filter_by(game_id=game_id).first()
        return game.to_dict() if game else None
    
    def close(self):
        """Close database connection"""
        self.session.close()

