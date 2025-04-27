import random
from random import randint
from datetime import datetime, timedelta
from app.schemas import EventSchema, UserResponseSchema, RecommendationSchema, TeamSchema, CasinoSchema, PurchasedCouponSchema, RecommendedEventSchema,\
UserProfile
from faker import Faker
from app import db
from app.config import Config
from app.db_models import User, Event, Team, Casino, PurchasedCoupon
from app.utils import random_begin_timestamp, random_end_timestamp, generate_value,\
generate_dummy_users, generate_dummy_casinos, generate_dummy_events, generate_dummy_teams, generate_dummy_purchased_coupons
from collections import Counter
from sqlalchemy.orm import load_only
import json


fake = Faker()

def create_user_profile(user_id):
    
    profile_id = randint(1, 1000000)
    profile = UserProfile(profile_id = profile_id, 
                          user_id = user_id,
                          purchases_at_last_update = 0,
                          last_updated = datetime.utcnow().isoformat())
    db.session.add(profile)
    
def create_users(user_data_list, commit=True):
    users = []
    schema = UserResponseSchema()
    
    with db.session.begin():
        for user_data in user_data_list:
            try:
                validated_data = schema.load(user_data, session=db.session)                
                u = User(**validated_data)
                db.session.add(u)
                db.session.flush()
                create_user_profile(u.user_id)
                users.append(u)
                
            except Exception as exc:
                print(f"Validation error: {exc}")

        if commit:
            db.session.commit()

    return users
        
def create_casinos(casino_data_list, users=[], commit=True):
    casinos = []
    schema = CasinoSchema()
    
    with db.session.begin():
        for casino_data in casino_data_list:
            try:
                validated_data = schema.load(casino_data, session=db.session)
                c = Casino(**validated_data)
                db.session.add(c)
                casinos.append(c)
                
                if users:
                   for user in users:
                       c.users.append(user)

            except Exception as exc:
                print(f"Validation error: {exc}")

        if commit:
            db.session.commit()

    return casinos

def create_teams(team_data_list, commit=True):
    teams = []
    schema = TeamSchema()
    
    with db.session.begin():
        for team_data in team_data_list:
            try:
                validated_data = schema.load(team_data, session=db.session)
                t = Team(**validated_data)
                db.session.add(t)
                teams.append(t)

            except Exception as exc:
                print(f"Validation error: {exc}")

        if commit:
            db.session.commit()

    return teams
    
def create_events(event_data_list, commit=True):
    events = []
    schema = EventSchema()
    
    with db.session.begin():
        for event_data in event_data_list:
            try:
                validated_data = schema.load(event_data, session=db.session)

                e = Event(**validated_data) 
                
                home_team = db.session.query(Team).filter_by(team_id=e.home_team_id).first()
                away_team = db.session.query(Team).filter_by(team_id=e.away_team_id).first()

                if home_team:
                    e.teams.append(home_team)
                if away_team:
                    e.teams.append(away_team)

                events.append(e)
                db.session.add(e)

            except Exception as exc:
                print(f"Validation error: {exc}")

        if commit:
            db.session.commit()

    return events
        
def create_purchased_coupons(coupon_data_list, user_id, commit=True):
    coupons = []
    schema = PurchasedCouponSchema()

    profile = db.session.query(UserProfile).filter_by(user_id=user_id).first()
    if not profile:
        raise ValueError("User profile not found")

    try:
        for coupon_data in coupon_data_list:
            validated_data = schema.load(coupon_data, session=db.session)
            coupon = PurchasedCoupon(**validated_data)
            
            profile.purchases_at_last_update += 1

            db.session.add(coupon)
            coupons.append(coupon)

        if commit:
            db.session.commit()

        return coupons

    except Exception as e:
        db.session.rollback()
        raise ValueError(f"Failed to create purchased coupons: {e}")
                
recommender_registry = {}

'''
def register_recommendation(func):
    recommender_registry[func.__name__] = func
    return func
'''

def register_recommendation(name):
    def wrapper(func):
        recommender_registry[name.lower()] = func
        return func
    return wrapper

def get_user_coupon_count(user_id):
    return db.session.query(PurchasedCoupon).filter_by(user_id=user_id).count()

def get_all_sport_league_tuples():
    events = db.session.query(Event.sport, Event.league).distinct().all()
    return [(sport, league) for sport, league in events]

def get_user_coupon_history(user_id, delta_days=30):
    
    time_threshold = (datetime.now() - timedelta(days=delta_days)).strftime("%Y-%m-%d %H:%M:%S")

    coupons = db.session.query(PurchasedCoupon)\
        .filter_by(user_id=user_id)\
        .filter(PurchasedCoupon.timestamp >= time_threshold)\
        .options(load_only(PurchasedCoupon.recommended_events))\
        .all()
    
    event_ids = []
    for coupon in coupons:
        for event in coupon.recommended_events:
            event_id = event.get('event_id')
            if event_id:
               event_ids.append(event_id)
    
    if not event_ids:
        return [], set()

    events = db.session.query(Event).filter(Event.event_id.in_(event_ids)).all()
    sport_league_tuples = [(event.sport, event.league) for event in events]
    
    return sport_league_tuples, set(event_ids)

def get_frequent_sport_league_tuples(user_id, n = 4, delta_days = 30):
    threshold = 5
    
    profile = db.session.query(UserProfile).filter_by(user_id=user_id).first()
    user_events, event_id_blacklist = get_user_coupon_history(user_id, delta_days=delta_days)
    
    if not profile:
        create_user_profile(user_id)
        profile = db.session.query(UserProfile).filter_by(user_id=user_id).first()
    
    if profile and profile.favorite_sport_league_json and profile.purchases_at_last_update < threshold:            
        cached = json.loads(profile.favorite_sport_league_json)
        return [tuple(item) for item in cached][:n], set()
    
    if not user_events:
        sampled = random.sample(get_all_sport_league_tuples(), k=n)
        return sampled, event_id_blacklist
    
    pair_counts = Counter(user_events)
    result = []
    
    "add all pairs that appear more than once to n times"
    for pair, count in pair_counts.most_common():
        if count > 1 and len(result) < n:
            result.append(pair)
    
    "if we need more, add pairs that appear once"
    if len(result) < n:
        remaining = n - len(result)
        for pair, count in pair_counts.most_common():
            if count == 1 and len(result) < n:
                result.append(pair)
                
    "if we dont have enough add with random choices"
    if len(result) < n:
        all_pairs = get_all_sport_league_tuples()
        remaining = n - len(result)
        available_pairs = list(set(all_pairs) - set(result))
        remaining = min(remaining, len(available_pairs))
        if remaining > 0:
            result.extend(random.sample(available_pairs, k=remaining))
            
    if profile and (not profile.favorite_sport_league_json or profile.purchases_at_last_update >= threshold):
        profile.favorite_sport_league_json = json.dumps(result[:20])
        profile.purchases_at_last_update = 0
        profile.last_updated = datetime.utcnow().isoformat()
        db.session.commit()
    
    return result, event_id_blacklist    

@register_recommendation("inference")    
def inference_recommendation(user_id, event_limit = 3):
    all_events = []
    event_data = []
    counter = 0
    
    sport_league_tuples, excluded_event_ids = get_frequent_sport_league_tuples(user_id, event_limit, delta_days = 30)
    
    while len(all_events) < event_limit and counter < len(sport_league_tuples):
       infer_sport, infer_league = sport_league_tuples[counter]

       query = Event.query.filter_by(sport=infer_sport, league=infer_league)
       if excluded_event_ids:
           query = query.filter(~Event.event_id.in_(excluded_event_ids))

       events = query.limit(event_limit - len(all_events)).all()
       all_events.extend(events)
       counter += 1
        
    for e in all_events:
        event_data.append({
          "event_id": e.event_id,
          "odd": e.odd
        })
    return{
        "user_id": user_id,
        "stake": round(random.uniform(1.5, 50.5), 2),
        "recommended_events": event_data,
        "timestamp": datetime.utcnow().isoformat(),
    }

@register_recommendation("dynamic")
def dynamic_recommendation(user_id, event_limit = 3):
    user = User.query.get(user_id)
    events = Event.query.filter_by(sport=user.favorite_sport).limit(event_limit).all()
    event_data = []
    
    for e in events:
        event_data.append({
          "event_id": e.event_id,
          "odd": e.odd
        })
    return{
        "user_id": user_id,
        "stake": round(random.uniform(1.5, 50.5), 2),
        "recommended_events": event_data,
        "timestamp": datetime.utcnow().isoformat(),
    }

@register_recommendation("static")
def static_recommendation(user_id, event_limit = 3):
    event_data = [
        {
          "event_id": 1,
          "odd": 2.57
        },
        {
          "event_id": 2,
          "odd": 2.97
        },
        {
          "event_id": 3,
          "odd": 2.94
        }
    ]
    
    return{
        "user_id": user_id,
        "stake": 45,
        "recommended_events": event_data,
        "timestamp": datetime.utcnow().isoformat(),
    }
'''
def inference_recommendation(user_id, e, n, time_window_start, time_window_end):
'''

def recommendation_generator(config, user_id):
    recommendation_schema = config["recommendation_schema"]
    recommender_type = config["recommender_type"]
    
    print("RECOMMENDER TYPE:", recommender_type) 
    
    if recommender_type not in recommender_registry:
       raise ValueError(f"Unsupported recommender_type: {recommender_type}")
       
    recommender_func = recommender_registry[recommender_type]
    
    full_data = recommender_func(user_id=user_id)

    
    recommendation = {}
        
    for output_field, config_value in recommendation_schema.items():
        if isinstance(config_value, dict):
            source_field = config_value.get("source_field", output_field)
            field_type = config_value["type"]
        else:
            source_field = output_field
            field_type = config_value

        value = full_data.get(source_field)
        if value is None:
            value = generate_value(field_type)
        
        recommendation[output_field] = value

    return recommendation

def populate_db():
    dummy_users = generate_dummy_users()
    created_users = create_users(dummy_users)
    
    dummy_teams = generate_dummy_teams()
    created_teams = create_teams(dummy_teams)
    
    dummy_events = generate_dummy_events(n=30, teams=dummy_teams)
    created_events = create_events(dummy_events)
    
    dummy_casinos = generate_dummy_casinos(n=5,users=created_users)
    created_casinos = create_casinos(dummy_casinos, users=created_users)
    
    print(f"Inserted {len(created_users)} users, {len(created_teams)} teams,{len(created_casinos)} casinos and {len(created_events)} events")