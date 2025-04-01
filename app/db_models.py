from datetime import datetime
from app import db
from sqlalchemy.dialects.postgresql import UUID
import uuid

event_participants = db.Table(
    'event_participants',
    db.Column('event_id', UUID(as_uuid=True), db.ForeignKey('events.event_id'), primary_key=True),
    db.Column('participant_id', UUID(as_uuid=True), db.ForeignKey('participants.participant_id'), primary_key=True)
)

class User(db.Model):
    __tablename__ = "users"
    
    user_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    birth_year = db.Column(db.Integer, nullable = False)
    currency = db.Column(db.String(30), nullable = False)
    country = db.Column(db.String(40), nullable = False)
    gender = db.Column(db.String(10), nullable = False)
    timestamp = db.Column(db.String(30), nullable = False)
    favorite_sport = db.Column(db.String(30), nullable = False)
    
    def __repr__(self):
       return f"<User {self.user_id}>"
   
class Event(db.Model):
    __tablename__ = "events"
    
    event_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    country = db.Column(db.String(20), nullable = False)
    begin_timestamp = db.Column(db.String(30), nullable = False)
    end_timestamp = db.Column(db.String(30), nullable = False)
    league = db.Column(db.String(100), nullable = False)
    sport = db.Column(db.String(50), nullable=False)
    odd = db.Column(db.Float, nullable=False)
    
    participants = db.relationship(
        "Participant",
        secondary = event_participants,
        back_populates="events",
    )
    
    def __repr__(self):
        return f"<Event {self.event_id} - {self.sport} in {self.country}>"

class Participant(db.Model):
    __tablename__ = "participants"
    
    participant_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(100), unique=True, nullable=False)
    sport = db.Column(db.String(30), nullable=False)
    
    events = db.relationship(
        "Event",
        secondary=event_participants,
        back_populates="participants",
    )
    
    def __repr__(self):
        return f"<Participant {self.participant_id} - {self.name}>"
    