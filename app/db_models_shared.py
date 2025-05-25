from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, JSON, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

SharedBase = declarative_base()
    
event_teams = Table(
    'event_teams',
    SharedBase.metadata,
    Column('event_id', Integer, ForeignKey('events.id'), primary_key=True), 
    Column('team_id', Integer, ForeignKey('teams.id'), primary_key=True)
)

class User(SharedBase):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)  
    name = Column(String(40), autoincrement=True)  
    surname = Column(String(40), autoincrement=True)  
    birth_year = Column(Integer, nullable = False)
    currency = Column(String(30), nullable = False)
    country = Column(String(50), nullable = False)
    gender = Column(String(10), nullable = False)
    timestamp = Column(String(30), nullable = False)
    favorite_sport = Column(String(30))
    favorite_league = Column(String(40))
    
    purchased_coupons = relationship("PurchasedCoupon", back_populates="user")
    user_profile = relationship("UserProfile", back_populates="user", uselist=False)
    
    def __repr__(self):
       return f"<User {self.id}>"
   
class UserProfile(SharedBase):
    __tablename__ = "users_profile"

    id = Column(Integer, primary_key=True, nullable = False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, unique=True)
    favorite_sport_league_json = Column(Text)
    purchases_at_last_update = Column(Integer, default=0, nullable = False)
    last_updated = Column(String(30), default=datetime.utcnow, nullable = False)


    user = relationship("User", back_populates="user_profile")

class Event(SharedBase):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, autoincrement=True) 
    country = Column(String(50), nullable = False)
    begin_timestamp = Column(String(30), nullable = False)
    end_timestamp = Column(String(30), nullable = False)
    league = Column(String(100), nullable = False)
    sport = Column(String(50), nullable=False)
    odd = Column(Float, nullable=False)
    home_team = Column(String(40), nullable=False) 
    away_team = Column(String(40), nullable=False) 
    
    teams = relationship("Team", secondary=event_teams, back_populates="events")
    
    def __repr__(self):
        return f"<Event {self.id} - {self.sport} in {self.country}>"

class Team(SharedBase):
    __tablename__ = "teams"
    
    id = Column(Integer, primary_key=True, autoincrement=True) 
    name = Column(String(100), unique = True, nullable = False)
    sport = Column(String(30), nullable = False)
    
    events = relationship("Event", secondary=event_teams, back_populates="teams")
    
    def __repr__(self):
        return f"<Team {self.id} - {self.name}>"
    
class PurchasedCoupon(SharedBase):
    __tablename__ = "purchased_coupons"
    
    id = Column(Integer, primary_key=True, autoincrement=True)  
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    stake = Column(Float, nullable=False)
    timestamp = Column(String(30), nullable = False)
    recommended_events = Column(JSON, nullable=False)
    
    user = relationship("User", back_populates="purchased_coupons")

    
    

