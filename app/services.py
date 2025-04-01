import random
from datetime import datetime, timedelta
from app.schemas import EventSchema, UserResponseSchema, RecommendationSchema, ParticipantSchema
import uuid
from faker import Faker
from app import db
from app.config import Config, fake 
from app.db_models import User, Event, Participant
from app.utils import random_begin_timestamp, random_end_timestamp

fake = Faker()
    
def create_users(n=10):
    users = []
    schema = UserResponseSchema()
    
    with db.session.begin():
        for i in range(n):
            timestamp = datetime.utcnow().isoformat()
            user_data = {
                "birth_year": fake.random_int(min=1950, max=2005),
                "currency": fake.random_element(elements=("EUR", "USD", "GBP")),
                "country": fake.random_element(elements=("GREECE", "USA")),
                "gender": fake.random_element(elements=("MALE", "FEMALE", "OTHER")),
                "timestamp": timestamp,
                "user_id": uuid.uuid4(),
                "favorite_sport": fake.random_element(elements=("football", "basketball", "handball"))
            }
            try:
                validated_data = schema.load(user_data, session=db.session)                
                u = User(**validated_data)
                db.session.add(u)
                users.append(u)
                
            except Exception as e:
                print(f"User validation error: {e}")     
          
        db.session.commit()
    return users

def create_participants(n=10):
    participants = []
    schema = ParticipantSchema()
     
    
    with db.session.begin():
        for i in range(n):
            random_int = random.randint(1000000000, 9999999999)
            team = "Team" + str(random_int)
            sport = fake.random_element(elements=("football", "basketball", "handball"))

            participant_data = {
                "participant_id": uuid.uuid4(), 
                "name": team,
                "sport": sport
            }
            
            try:
                validated_data = schema.load(participant_data, session=db.session)
                p = Participant(**validated_data)
                db.session.add(p)
                participants.append(p)
                
            except Exception as e:
                print(f"Participant Validation error: {e}") 
            
        db.session.commit()
    return participants    
    
def create_events(n=3, participants=[]):
    events = []
    schema = EventSchema()
    
    sport = fake.random_element(elements=["football", "handball", "basketball"])
    league = Config.get_random_league(sport)
    
    with db.session.begin():
        for i in range(n):
            begin = random_begin_timestamp()
            end = random_end_timestamp(begin)
            
            event_data = {
               "event_id": uuid.uuid4(),
               "begin_timestamp": begin,
               "end_timestamp": end,
               "country": fake.random_element(elements=["GREECE", "USA"]),
               "league": league,
               "sport": sport,
               "odd": round(random.uniform(1.5, 3.5), 2),
               "participants": [{"participant_id": p.participant_id, "name": p.name, "sport": p.sport} for p in fake.random_sample(elements=participants, length = fake.random_int(min=1, max=len(participants)))]
            }
            try: 
                validated_data = schema.load(event_data, session=db.session)
                
                e = Event(
                   event_id = validated_data["event_id"],
                   begin_timestamp = validated_data["begin_timestamp"],
                   end_timestamp = validated_data["end_timestamp"],
                   country = validated_data["country"],
                   league = validated_data["league"],
                   sport = validated_data["sport"],
                   odd = validated_data["odd"]
                )
                
                
                db.session.add(e)
                
                for p_data in validated_data["participants"]:
                    participant = next((p for p in participants if p.participant_id == p_data["participant_id"]), None)
                    if participant:
                        e.participants.append(participant)
                        
                events.append(e)
        
            except Exception as e:
                print(f"Validation error: {e}")            
                    
        db.session.commit()
    return events

def generate_dummy_recommendation(user_id, favorite_sport, events = 3):
    events = Event.query.filter_by(sport=favorite_sport).limit(events).all()
    event_data = []
    
    for e in events:
        filtered_participants = [
           {
               "participant_id": p.participant_id,
               "name": p.name,
               "sport": p.sport
           }
           for p in e.participants if p.sport == favorite_sport
       ]
        if filtered_participants:
             event_data.append({
                    "country": e.country,
                    "event_id": e.event_id,
                    "begin_timestamp": e.begin_timestamp,
                    "end_timestamp": e.end_timestamp,
                    "league": e.league,
                    "sport": e.sport,
                    "odd": e.odd,
                    "participants": filtered_participants
             })
    
    timestamp = datetime.utcnow().isoformat() if user_id else None 
    
    return{
        "user_id": user_id,
        "stake": round(random.uniform(1.5, 50.5), 2),
        "recommended_events": event_data,
        "timestamp": timestamp
    }

def populate_db():
    
    users = create_users()
    participants = create_participants()
    events = create_events(n=3,participants=participants)
    
    print(f"Inserted {len(users)} users, {len(participants)} participants, and {len(events)} events.")