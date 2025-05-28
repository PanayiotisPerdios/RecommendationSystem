from datetime import datetime, timedelta
import uuid, random
from faker import Faker
from app import db
from app.config import Config
from app.db_models_shared import User
from app.db_models_master import Casino
from random import randint
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import psycopg2
from app.db_models_shared import SharedBase  

fake = Faker()
db_engine_cache = {}
cached_casino_ids = None
cached_user_ids = None

def generate_unique_user_id(session, Model):
    while True :
        candidate_id = randint(1, 1_000_000)
        exists = session.query(Model.id).filter_by(id=candidate_id).first()
        if not exists:
            return candidate_id
        
def get_random_casino_id():
    global cached_casino_ids 

    if cached_casino_ids is None:
        cached_casino_ids = [] 
        result = db.session.query(Casino.id).all()
        print(f"Fetched {len(result)} casinos from DB.")
        
        for row in result:
            casino_id = row[0]
            cached_casino_ids.append(casino_id)
        
    if cached_casino_ids:
        return random.choice(cached_casino_ids)
    else:
        print("No casino IDs available.")
        return None
    
def get_random_user_id(casino_id):
    session = get_casino_db_session(casino_id)
    
    global cached_user_ids 
    
    if cached_user_ids is None:
        cached_user_ids = [] 
        result = session.query(User.id).all()

        for row in result:
            user_id = row[0]
            cached_user_ids.append(user_id)
        
    if cached_user_ids:
        return random.choice(cached_user_ids)
    else:
        return None
    
def create_db_per_casino(casino_id):
    db_name = f"casino_{casino_id}"
    db_url = f"postgresql://{Config.POSTGRES_USER}:{Config.POSTGRES_PASSWORD}@{Config.POSTGRES_HOST}:{Config.POSTGRES_PORT}/{db_name}"

    connection = psycopg2.connect(
        user=Config.POSTGRES_USER,
        password=Config.POSTGRES_PASSWORD,
        dbname="postgres",
        host=Config.POSTGRES_HOST,
        port=Config.POSTGRES_PORT
    )
    connection.autocommit = True
    
    try:
        cursor = connection.cursor()
        try:
            cursor.execute(f"CREATE DATABASE {db_name}")
            print(f"Database {db_name} created successfully.")
        except psycopg2.errors.DuplicateDatabase:
            print(f"Database {db_name} already exists.")
        finally:
            cursor.close()
    finally:
        connection.close()
        
    engine = create_engine(db_url)
    SharedBase.metadata.create_all(engine)
    print(f"Tables created for {db_name}.")
        
    return db_name

def get_casino_db_session(casino_id):
    db_name = f"casino_{casino_id}"
    db_url = f"postgresql://{Config.POSTGRES_USER}:{Config.POSTGRES_PASSWORD}@{Config.POSTGRES_HOST}:{Config.POSTGRES_PORT}/{db_name}"
    
    if casino_id not in db_engine_cache:
        engine = create_engine(db_url)
        db_engine_cache[casino_id] = engine
    
    engine = db_engine_cache[casino_id]
    Session = sessionmaker(bind=engine)
    return Session()

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
        name = fake.first_name()
        surname = fake.last_name()

        user_data = {
            "birth_year": fake.random_int(min=1950, max=2005),
            "currency": fake.random_element(elements=("EUR", "USD", "GBP")),
            "country": country,
            "gender": fake.random_element(elements=("MALE", "FEMALE", "OTHER")),
            "timestamp": timestamp,
            "name": name,
            "surname": surname,
            "favorite_sport": fake.random_element(elements=("FOOTBALL", "BASKETBALL", "HANDBALL"))
        }
        
        user_data_list.append(user_data)
        
    return user_data_list

def generate_dummy_casinos(n=3):
    casino_data_list = []
    
    for i in range(n):
        timestamp = datetime.utcnow().isoformat()
        random_int = random.randint(1000000000000, 9999999999999)
        name = "Casino" + str(random_int)
        
        casino_data = {
            "db_name": name,
            "timestamp": timestamp
        }
        
        casino_data_list.append(casino_data)
        
    return casino_data_list

    
def generate_dummy_events(teams, n=3):
    event_data_list = []
    
    for i in range(n):
        sport = fake.random_element(elements=["FOOTBALL", "HANDBALL", "BASKETBALL"])
        league = Config.get_random_league(sport)
        country = fake.random_element(elements=Config.countries)
        
        begin = random_begin_timestamp()
        end = random_end_timestamp(begin)
        
        sport_teams = [team for team in teams if team['sport'] == sport]
        if len(sport_teams) < 2:
             continue 
        
        home_team = fake.random_element(elements=sport_teams)
        away_team = fake.random_element(elements=[t for t in sport_teams if t != home_team])

        
        event_data = {
           "begin_timestamp": begin,
           "end_timestamp": end,
           "country": country,
           "league": league,
           "home_team": home_team["name"],
           "away_team": away_team["name"],
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
        sport = fake.random_element(elements=("FOOTBALL", "HANDBALL", "BASKETBALL"))

        team_data = {
            "name": team,
            "sport": sport
        }
        
        team_data_list.append(team_data)


    return team_data_list

def generate_dummy_purchased_coupons(events, user_id, n=1):

    if len(events) < 3:
        raise ValueError("Not enough events to generate coupons")

    coupon_data_list = []

    for i in range(n):
        selected_events = random.sample(events, 3)

        event_data = [
            {
                "country":  event["country"],
                "league":   event["league"],
                "home_team": event["home_team"],
                "away_team": event["away_team"],
                "sport":   event["sport"],
                "odd":     event["odd"]
            }
            for event in selected_events
        ]

        coupon_data = {
            "user_id": user_id,
            "stake": round(random.uniform(5, 100), 2),
            "timestamp": datetime.utcnow().isoformat(),
            "recommended_events": event_data
        }

        coupon_data_list.append(coupon_data)

    return coupon_data_list, user_id

def generate_dummy_purchased_coupons_with_dummy_events(teams, user_id, n=1):
    total_events_needed = n * 3
    events = generate_dummy_events(teams, total_events_needed)

    coupon_data_list = []

    for i in range(n):
        selected_events = events[i * 3:(i + 1) * 3]

        event_data = [
            {
                "country":   event["country"],
                "league":   event["league"],
                "home_team": event["home_team"],
                "away_team": event["away_team"],
                "sport":   event["sport"],
                "odd": event["odd"]
            }
            for event in selected_events
        ]

        coupon_data = {
            "user_id": user_id,
            "stake": round(random.uniform(5, 100), 2),
            "timestamp": datetime.utcnow().isoformat(),
            "recommended_events": event_data
        }

        coupon_data_list.append(coupon_data)

    return coupon_data_list

def uppercase_dict(data):
    if isinstance(data, dict):
        return {k: uppercase_dict(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [uppercase_dict(item) for item in data]
    elif isinstance(data, str):
        return data.upper()
    else:
        return data



