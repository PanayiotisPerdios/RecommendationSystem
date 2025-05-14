import random
from datetime import datetime, timedelta
from marshmallow import ValidationError
import uuid, random
from faker import Faker
from app.config import Config
from app.schemas import Event, User, Team
from random import randint
from app import db

fake = Faker()

def random_begin_timestamp():
    return (datetime.utcnow() - timedelta(days=random.randint(10, 30))).replace(microsecond=0).isoformat()

def random_end_timestamp(begin_time):
    begin_dt = datetime.fromisoformat(begin_time)
    return (begin_dt + timedelta(minutes=60)).replace(microsecond=0).isoformat()

def clean_for_json(data):
    if isinstance(data, dict):
        return {k: clean_for_json(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [clean_for_json(item) for item in data]
    elif isinstance(data, (uuid.UUID, datetime)):
        return str(data)
    elif hasattr(data, 'isoformat'):
        return data.isoformat()
    return data
        

def generate_value(value_type):
    if value_type == "uuid":
        return str(uuid.uuid4())
    elif value_type == "float":
        return round(random.uniform(10, 100), 2)
    elif value_type == "string":
        return "example"
    elif value_type == "list":
        return ["test", "mock"]
    elif value_type == "int":
        return random.randint(1, 100)
    else:
      return None

def generate_dummy_users(n=10):
    user_data_list = []
    
    for i in range(n):
        timestamp = datetime.utcnow().isoformat()
        country = fake.random_element(elements=Config.countries)

        user_data = {
            "birth_year": fake.random_int(min=1950, max=2005),
            "currency": fake.random_element(elements=("EUR", "USD", "GBP")),
            "country": country,
            "gender": fake.random_element(elements=("MALE", "FEMALE", "OTHER")),
            "timestamp": timestamp,
            "id": randint(1, 1000000),
            "favorite_sport": fake.random_element(elements=("football", "basketball", "handball"))
        }
        
        user_data_list.append(user_data)
        
    return user_data_list

def generate_dummy_casinos(n=3, users=[]):
    casino_data_list = []
    
    for i in range(n):
        timestamp = datetime.utcnow().isoformat()
        random_int = random.randint(1000000000000, 9999999999999)
        name = "Casino" + str(random_int)
        
        casino_data = {
            "id": randint(1, 1000000),
            "name": name,
            "timestamp": timestamp
        }
        
        casino_data_list.append(casino_data)
        
    return casino_data_list

    
def generate_dummy_events(n=3):
    event_data_list = []
    
    teams = db.session.query(Team).all()

    for i in range(n):
        sport = fake.random_element(elements=["football", "handball", "basketball"])
        league = Config.get_random_league(sport)
        country = fake.random_element(elements=Config.countries)
        
        begin = random_begin_timestamp()
        end = random_end_timestamp(begin)
        
        sport_teams = [team for team in teams if team.sport == sport]
        if len(sport_teams) < 2:
             continue 
        
        home_team = fake.random_element(elements=teams)
        away_team = fake.random_element(elements=[t for t in sport_teams if t != home_team])

        
        event_data = {
           "id": randint(1, 1000000),
           "begin_timestamp": begin,
           "end_timestamp": end,
           "country": country,
           "league": league,
           "home_team_id": home_team.id,
           "away_team_id": away_team.id,
           "sport": sport,
           "odd": round(random.uniform(1.5, 3.5), 2),
        }
        
        event_data_list.append(event_data)


    return event_data_list

def generate_dummy_teams(n=10):
    team_data_list = []

    for i in range(n):
        random_int = random.randint(1000000000000, 9999999999999)
        team = "Team" + str(random_int)
        sport = fake.random_element(elements=("football", "basketball", "handball"))

        team_data = {
            "id": randint(1, 1000000), 
            "name": team,
            "sport": sport
        }
        
        team_data_list.append(team_data)


    return team_data_list

def generate_dummy_purchased_coupons(user_id, event_limit=10, n=1):

    events = db.session.query(Event).limit(event_limit).all()
    if len(events) < 3:
        raise ValueError("Not enough events to generate coupons")

    coupon_data_list = []

    for i in range(n):
        selected_events = random.sample(events, 3)

        event_data = [
            {
                "id": event.event_id,
                "odd": event.odd
            }
            for event in selected_events
        ]

        coupon_data = {
            "id": random.randint(100000, 999999),
            "user_id": user_id,
            "stake": round(random.uniform(5, 100), 2),
            "timestamp": datetime.utcnow().isoformat(),
            "recommended_events": event_data
        }

        coupon_data_list.append(coupon_data)

    return coupon_data_list, user_id

def generate_dummy_purchased_coupons_random_user(event_limit=10, n=1):

    events = db.session.query(Event).limit(event_limit).all()
    
    result = db.session.query(User.id).all()
    user_ids = []
    for row in result:
        user_ids.append(row[0])
        
    selected_user_id = random.choice(user_ids)  
    
    if len(events) < 3:
        raise ValueError("Not enough events to generate coupons")

    coupon_data_list = []

    for i in range(n):
        selected_events = random.sample(events, 3)

        event_data = [
            {
                "id": event.id,
                "odd": event.odd
            }
            for event in selected_events
        ]

        coupon_data = {
            "id": random.randint(100000, 999999),
            "user_id": selected_user_id,
            "stake": round(random.uniform(5, 100), 2),
            "timestamp": datetime.utcnow().isoformat(),
            "recommended_events": event_data
        }

        coupon_data_list.append(coupon_data)

    return coupon_data_list



