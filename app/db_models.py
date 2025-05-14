from datetime import datetime
from app import db
from sqlalchemy import Integer


event_teams = db.Table(
    'event_teams',
    db.Column('event_id', Integer, db.ForeignKey('events.id'), primary_key=True), 
    db.Column('team_id', Integer, db.ForeignKey('teams.id'), primary_key=True)
)

user_casino = db.Table(
    'user_casino',
    db.Column('user_id', Integer, db.ForeignKey('users.id'), primary_key=True), 
    db.Column('casino_id', Integer, db.ForeignKey('casinos.id'), primary_key=True)
)



class User(db.Model):
    __tablename__ = "users"
    
    id = db.Column(Integer, primary_key=True, autoincrement=True)  
    birth_year = db.Column(db.Integer, nullable = False)
    currency = db.Column(db.String(30), nullable = False)
    country = db.Column(db.String(50), nullable = False)
    gender = db.Column(db.String(10), nullable = False)
    timestamp = db.Column(db.String(30), nullable = False)
    favorite_sport = db.Column(db.String(30))
    favorite_league = db.Column(db.String(40))
    
    purchased_coupons = db.relationship("PurchasedCoupon", back_populates="user")
    casinos = db.relationship('Casino', secondary=user_casino, back_populates='users')
    user_profile = db.relationship("UserProfile", back_populates="user", uselist=False)
    
    def __repr__(self):
       return f"<User {self.id}>"
   
class UserProfile(db.Model):
    __tablename__ = "users_profile"

    id = db.Column(Integer, primary_key=True, nullable = False)
    user_id = db.Column(Integer, db.ForeignKey("users.id"), nullable=False, index=True, unique=True)
    favorite_sport_league_json = db.Column(db.Text)
    purchases_at_last_update = db.Column(db.Integer, default=0, nullable = False)
    last_updated = db.Column(db.String(30), default=datetime.utcnow, nullable = False)


    user = db.relationship("User", back_populates="user_profile")

class Event(db.Model):
    __tablename__ = "events"
    
    id = db.Column(Integer, primary_key=True, autoincrement=True) 
    country = db.Column(db.String(50), nullable = False)
    begin_timestamp = db.Column(db.String(30), nullable = False)
    end_timestamp = db.Column(db.String(30), nullable = False)
    league = db.Column(db.String(100), nullable = False)
    sport = db.Column(db.String(50), nullable=False)
    odd = db.Column(db.Float, nullable=False)
    home_team_id = db.Column(Integer, nullable=False) 
    away_team_id = db.Column(Integer, nullable=False) 
    
    teams = db.relationship("Team", secondary=event_teams, back_populates="events")
    
    def __repr__(self):
        return f"<Event {self.id} - {self.sport} in {self.country}>"

class Team(db.Model):
    __tablename__ = "teams"
    
    id = db.Column(Integer, primary_key=True, autoincrement=True) 
    name = db.Column(db.String(100), unique = True, nullable = False)
    sport = db.Column(db.String(30), nullable = False)
    
    events = db.relationship("Event", secondary=event_teams, back_populates="teams")
    
    def __repr__(self):
        return f"<Team {self.id} - {self.name}>"

class Casino(db.Model):
    __tablename__ = "casinos"

    id = db.Column(Integer, primary_key=True, autoincrement=True)  
    name = db.Column(db.String(40), nullable = False)
    recommender_type = db.Column(db.String(30))
    recommendation_schema = db.Column(db.JSON)
    timestamp = db.Column(db.String(30), nullable = False)
    users = db.relationship("User", backref="casino")
    
    users = db.relationship('User', secondary=user_casino, back_populates='casinos')
    
    def __repr__(self):
        return f"<Casino {self.id} - {self.name}>"
    
class PurchasedCoupon(db.Model):
    __tablename__ = "purchased_coupons"
    
    id = db.Column(Integer, primary_key=True, autoincrement=True)  
    user_id = db.Column(Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    stake = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.String(30), nullable = False)
    recommended_events = db.Column(db.JSON, nullable=False)
    
    user = db.relationship("User", back_populates="purchased_coupons")

    
    

