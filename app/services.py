import random
from datetime import datetime, timedelta
from app.schemas import EventSchema, UserResponseSchema, TeamSchema, CasinoSchema, PurchasedCouponSchema,\
UserProfileSchema
from faker import Faker
from app import db
from app.db_models_shared import User, Event, Team, PurchasedCoupon, UserProfile
from app.db_models_master import Casino
from app.utils import  generate_value, generate_dummy_users, generate_dummy_casinos, generate_dummy_events, \
generate_dummy_teams, create_db_per_casino, get_casino_db_session, uppercase_dict, generate_unique_user_id
from collections import Counter
from sqlalchemy.orm import load_only
import json


fake = Faker()

def create_casinos(casino_data_list, commit=True):
    casinos = []
    schema = CasinoSchema()
    
    with db.session.begin():
        for casino_data in casino_data_list:
            try:
                casino_data["id"] = generate_unique_user_id(db.session, Casino)
                casino_data_upper = uppercase_dict(casino_data)
                validated_data = schema.load(casino_data_upper, session=db.session)
                c = Casino(**validated_data)
                db.session.add(c)
                db.session.flush()
                
                create_db_per_casino(c.id)
                
                casinos.append(c)

            except Exception as exc:
                print(f"Validation error: {exc}")

    if commit:
        db.session.commit()

    return casinos
    
def create_user_profile(user_id, session):
    
    profile_id = generate_unique_user_id(session, UserProfile)
    profile = UserProfile(id = profile_id, 
                          user_id = user_id,
                          purchases_at_last_update = 0,
                          last_updated = datetime.utcnow().isoformat())
    session.add(profile)
    
def create_users(user_data_list, casino_id, commit=True):
    users = []
    session = get_casino_db_session(casino_id)
    schema = UserResponseSchema()
    
    for user_data in user_data_list:
        try:
            user_data["id"] = generate_unique_user_id(session, User)
            
            user_data_upper = uppercase_dict(user_data)
            validated_data = schema.load(user_data_upper, session=session)
            u = User(**validated_data)
        
            existing_user = session.query(User).filter((User.name == u.name) & (User.surname == u.surname)).first()
            if existing_user:
                print(f"Duplicate user detected with name {u.name} and surname {u.surname} , skipping.")
                continue
            
            session.add(u)
            session.flush()
            create_user_profile(u.id, session=session)
            users.append(u)
                    
        except Exception as exc:
            print(f"Validation error for user {user_data}: {exc}")
    
    if commit:
        try:
            session.commit()
            
        except Exception as exc:
            print(f"Commit error: {exc}")
            session.rollback()
    session.close()
            
    return users

def create_teams(team_data_list, casino_id, commit=True):
    teams = []
    session = get_casino_db_session(casino_id)
    schema = TeamSchema()
    
    for team_data in team_data_list:
        try:
            team_data["id"] = generate_unique_user_id(session, Team)
            team_data_upper = uppercase_dict(team_data)
            validated_data = schema.load(team_data_upper, session=session)
            t = Team(**validated_data)
            
            existing_team = session.query(Team).filter((Team.name == t.name) & (Team.sport == t.sport)).first()
            if existing_team:
                print(f"Duplicate team detected with name {t.name} and sport {t.sport} , skipping.")
                continue
            session.add(t)
            teams.append(t)
    
        except Exception as exc:
            print(f"Validation error for team {team_data}: {exc}")
    
    if commit:
        try:
            session.commit()
            
        except Exception as exc:
            print(f"Commit error: {exc}")
            session.rollback()
    session.close()
            
    return teams
    
def create_events(event_data_list, casino_id, commit=True):
    events = []
    session = get_casino_db_session(casino_id)
    schema = EventSchema()
    
    for event_data in event_data_list:
        try:
            event_data["id"] = generate_unique_user_id(session, Event)
            event_data_upper = uppercase_dict(event_data)
            validated_data = schema.load(event_data_upper, session=session)
            e = Event(**validated_data) 
                    
            home_team = session.query(Team).filter_by(name=e.home_team).first()
            away_team = session.query(Team).filter_by(name=e.away_team).first()
    
            if home_team:
                e.teams.append(home_team)
            if away_team:
                e.teams.append(away_team)
    
            events.append(e)
            session.add(e)
    
        except Exception as exc:
            print(f"Validation error for event {event_data}: {exc}")
            
    if commit:
        try:
            session.commit()
            
        except Exception as exc:
            print(f"Commit error: {exc}")
            session.rollback()
            
    session.close()
        
    return events
        
def create_purchased_coupons(coupon_data_list, casino_id, session=None, commit=True):
    coupons = []
    close_session = False
    
    if session is None:
        session = get_casino_db_session(casino_id)
        close_session = True
        
    schema = PurchasedCouponSchema()
    
    for coupon_data in coupon_data_list:
        try:
            user_id = coupon_data.get("user_id")
            profile = session.query(UserProfile).filter_by(user_id=user_id).first()
            if not profile:
                raise ValueError(f"User profile not found for user_id {user_id}")
                
            coupon_data["id"] = generate_unique_user_id(session, PurchasedCoupon)
            coupon_data_upper = uppercase_dict(coupon_data)
            validated_data = schema.load(coupon_data_upper, session=session)
            coupon = PurchasedCoupon(**validated_data)
            
            profile.purchases_at_last_update += 1

            session.add(coupon)
            coupons.append(coupon)

        except Exception as exc:
            print(f"Validation error for coupon {coupon_data}: {exc}")

    if commit:
        try:
            session.commit()
        except Exception as exc:
            print(f"Commit error: {exc}")
            session.rollback()

    if close_session:
        session.close()
    
    return coupons
                
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

def get_all_sport_league_tuples(casino_id):
    session = get_casino_db_session(casino_id)

    try:
        events = session.query(Event.sport, Event.league).distinct().all()
        
        result = []
        for event in events:
            sport = event[0]
            league = event[1]
            result.append((sport, league))    
    finally:
       session.close()
    return result

def get_frequent_sport_league_tuples(user_id, casino_id, n = 4, delta_days = 30):
    threshold = 5
    session = get_casino_db_session(casino_id)
    
    try:
        profile = session.query(UserProfile).filter_by(user_id=user_id).first()
        
        # Extract (sport, league) tuples directly from coupons
        coupons = session.query(PurchasedCoupon)\
            .filter_by(user_id=user_id)\
            .filter(PurchasedCoupon.timestamp >= (datetime.utcnow() - timedelta(days=delta_days)).isoformat())\
            .options(load_only(PurchasedCoupon.recommended_events))\
            .all()
        
        user_sport_league = []
        for coupon in coupons:
            for event in coupon.recommended_events:
                sport = event.get("sport")
                league = event.get("league")
                if sport and league:
                    user_sport_league.append((sport, league))
                    
        if not profile:
            create_user_profile(user_id, session=session)
            profile = session.query(UserProfile).filter_by(user_id=user_id).first()

        if profile and profile.favorite_sport_league_json and profile.purchases_at_last_update < threshold:
            cached = json.loads(profile.favorite_sport_league_json)
            result = []
            for item in cached:
                result.append(tuple(item))
            return result[:n]

        if not user_sport_league:
            sampled = random.sample(get_all_sport_league_tuples(casino_id), k=n)
            return sampled

        pair_counts = Counter(user_sport_league)
        result = []

        #add pairs that appear more than once to n times
        for pair, count in pair_counts.most_common():
            if count > 1 and len(result) < n:
                result.append(pair)

        #add pairs that appear once if needed
        if len(result) < n:
            for pair, count in pair_counts.most_common():
                if count == 1 and len(result) < n:
                    result.append(pair)

        #fill remaining with random choices
        if len(result) < n:
            all_pairs = get_all_sport_league_tuples(casino_id)
            available_pairs = list(set(all_pairs) - set(result))
            remaining = n - len(result)
            remaining = min(remaining, len(available_pairs))
            if remaining > 0:
                result.extend(random.sample(available_pairs, k=remaining))

        if profile and (not profile.favorite_sport_league_json or profile.purchases_at_last_update >= threshold):
            profile.favorite_sport_league_json = json.dumps(result[:20])
            profile.purchases_at_last_update = 0
            profile.last_updated = datetime.utcnow().isoformat()
            session.commit()

    finally:
        session.close()
    
    return result  

@register_recommendation("inference")
def inference_recommendation(user_id, casino_id, event_limit=3):
    session = get_casino_db_session(casino_id)
    try:
        all_events = []
        event_data = []
        counter = 0
        
        sport_league_tuples = get_frequent_sport_league_tuples(user_id, casino_id, n=event_limit, delta_days=30)
        
        while len(all_events) < event_limit and counter < len(sport_league_tuples):
            infer_sport, infer_league = sport_league_tuples[counter]

            query = session.query(Event).filter_by(sport=infer_sport, league=infer_league)

            events = query.limit(event_limit - len(all_events)).all()
            all_events.extend(events)
            counter += 1
            
        for e in all_events:
            event_data.append({
                "country":  e.country,
                "league":   e.league,
                "home_team": e.home_team,
                "away_team": e.away_team,
                "sport":   e.sport,
                "odd":     e.odd
            })
    finally:
        session.close()

    return {
        "user_id": user_id,
        "stake": round(random.uniform(1.5, 50.5), 2),
        "recommended_events": event_data,
        "timestamp": datetime.utcnow().isoformat(),
    }

@register_recommendation("inference_score")
def inference_score_recommendation(user_id, casino_id, event_limit=3):
    session = get_casino_db_session(casino_id)
    score_list = []
    
    try:
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            raise ValueError(f"User {user_id} not found in casino {casino_id}")
            
        coupons = session.query(PurchasedCoupon).filter_by(user_id=user_id)\
            .options(load_only(PurchasedCoupon.recommended_events)).all()
        
        top_sports, top_leagues, top_countries = [], [], []
        top_home_teams, top_away_teams = [], []
        
        if coupons:
            coupon_events_sports, coupon_events_league, coupon_events_country = [], [], []
            coupon_events_home_team, coupon_events_away_team = [], []
            
            for coupon in coupons:
                for event in coupon.recommended_events:
                    coupon_events_sports.append(event.get("sport"))
                    coupon_events_league.append(event.get("league"))
                    coupon_events_country.append(event.get("country"))
                    coupon_events_home_team.append(event.get("home_team"))
                    coupon_events_away_team.append(event.get("away_team"))
            
                                
            for item in Counter(coupon_events_sports).most_common(2):
                if item[0]:
                    top_sports.append(item[0])
            
            for item in Counter(coupon_events_league).most_common(2):
                if item[0]:
                    top_leagues.append(item[0])
            
            for item in Counter(coupon_events_country).most_common(2):
                if item[0]:
                    top_countries.append(item[0])
            
            for item in Counter(coupon_events_home_team).most_common(2):
                if item[0]:
                    top_home_teams.append(item[0])
            
            for item in Counter(coupon_events_away_team).most_common(2):
                if item[0]:
                    top_away_teams.append(item[0])

            
        events = session.query(Event).all()
        if not events:
           raise ValueError("No available events in the system.")
           
        for event in events:
            score = 0
            if event.country in user.country:
                score += 1
            if event.sport in user.favorite_sport:
                score += 1
            if event.country in top_countries[:1]:
                score += 2
            elif event.country in top_countries[1:2]:
                score += 1
            if event.sport in top_sports[:1]:
                score += 2
            elif event.sport in top_sports[1:2]:
                score += 1
            if event.league in top_leagues[:1]:
                score += 3
            elif event.league in top_leagues[1:2]:
                score += 2
            if event.home_team in top_home_teams[:1]:
                score += 4
            elif event.home_team in top_home_teams[1:2]:
                score += 3
            if event.away_team in top_away_teams[:1]:
                score += 4
            elif event.away_team in top_away_teams[1:2]:
                score += 3

                
            score_list.append((event.id,
                               event.country,
                               event.begin_timestamp,
                               event.end_timestamp,
                               event.league,
                               event.sport,
                               event.odd,
                               event.home_team,
                               event.away_team,
                               score))
            
        # Handle empty or low-score case
        if not score_list:
            top_events = random.sample(events, k=min(event_limit, len(events)))
        else:
            sorted_score_list = sorted(score_list, key=lambda x: x[-1], reverse=True)
            
            top_events = sorted_score_list[:event_limit]
            
        event_data = []
        for e in top_events:
            event_data.append({
                "country": e[1],
                "league": e[4],
                "home_team": e[7],
                "away_team": e[8],
                "sport": e[5],
                "odd": e[6],
            })
            
    finally:
        session.close()
    
    return {
        "user_id": user_id,
        "stake": round(random.uniform(1.5, 50.5), 2),
        "recommended_events": event_data,
        "timestamp": datetime.utcnow().isoformat(),
    }
        

@register_recommendation("dynamic")
def dynamic_recommendation(user_id, casino_id, event_limit=3):
    session = get_casino_db_session(casino_id)
    try:
        user = session.query(User).get(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found in casino {casino_id}")

        events = session.query(Event).filter_by(sport=user.favorite_sport).limit(event_limit).all()
        event_data = []

        for e in events:
            event_data.append({
                "country":  e.country,
                "league":   e.league,
                "home_team": e.home_team,
                "away_team": e.away_team,
                "sport":   e.sport,
                "odd":     e.odd
            })
    finally:
        session.close()

    return {
        "user_id": user_id,
        "stake": round(random.uniform(1.5, 50.5), 2),
        "recommended_events": event_data,
        "timestamp": datetime.utcnow().isoformat(),
    }

@register_recommendation("static")
def static_recommendation(user_id, casino_id, event_limit = 3):
    event_data = [
        {
          "country":  "ITALY",
          "league":   "EUROLEAGUE",
          "home_team": "TEAM23142",
          "away_team": "TEAM12423",
          "sport":   "FOOTBALL",
          "odd": 2.57
        },
        {
          "country":  "GREECE",
          "league":   "SEHA LEAGUE",
          "home_team": "TEAM00987",
          "away_team": "TEAM77432",
          "sport":   "HANDBALL",
          "odd": 2.97
        },
        {
          "country":  "USA",
          "league":   "NBA",
          "home_team": "TEAM23577",
          "away_team": "TEAM90876",
          "sport":   "BASKETBALL",
          "odd": 2.94
        }
    ]
    
    return{
        "user_id": user_id,
        "stake": 45,
        "recommended_events": event_data,
        "timestamp": datetime.utcnow().isoformat(),
    }

def recommendation_generator(config, casino_id, user_id):
    recommendation_schema = config["recommendation_schema"]
    recommender_type = config["recommender_type"]
    
    print("RECOMMENDER TYPE:", recommender_type) 
    
    if recommender_type not in recommender_registry:
       raise ValueError(f"Unsupported recommender_type: {recommender_type}")
       
    recommender_func = recommender_registry[recommender_type]
    
    full_data = recommender_func(user_id=user_id, casino_id=casino_id)
    
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
    dummy_teams = generate_dummy_teams()
    dummy_events = generate_dummy_events(dummy_teams, n=30)
    
    dummy_casinos = generate_dummy_casinos(n=5)
    created_casinos = create_casinos(dummy_casinos)

    total_users, total_teams, total_events = 0, 0, 0
    
    for casino in created_casinos:
        casino_id = casino.id

        
        create_db_per_casino(casino_id)

        users = create_users(dummy_users, casino_id=casino_id)
        teams = create_teams(dummy_teams, casino_id=casino_id)
        events = create_events(dummy_events, casino_id=casino_id)

        total_users += len(users)
        total_teams += len(teams)
        total_events += len(events)

    print(f"Inserted {total_users} users, {total_teams} teams, {len(created_casinos)} casinos and {total_events} events")