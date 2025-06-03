import os
from faker import Faker
import random
from marshmallow import fields

fake = Faker()

class Config:
    POSTGRES_USER = os.getenv("POSTGRES_USER", "user")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "1234")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "db")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
    MASTER_DATABASE_NAME = os.getenv("MASTER_DATABASE_NAME", "recommendation_system")
    
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{MASTER_DATABASE_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
 
    FOOTBALL_LEAGUES = [
        "La Liga", "Premier League", "Bundesliga", "Serie A", "Ligue 1", 
        "Champions League", "Europa League", "Eredivisie", "Primeira Liga", "Major League Soccer"
    ]

    BASKETBALL_LEAGUES = [
        "NBA", "EuroLeague", "WNBA", "Chinese Basketball Association", "NCAA Basketball",
        "Liga ACB", "NBA G-League", "Australian NBL", "CBA"
    ]
 
    HANDBALL_LEAGUES = [
        "EHF Champions League", "Lidl Starligue", "Handball Bundesliga", "La Liga ASOBAL", 
        "SEHA League", "Danish Handball League", "Hungarian Handball League", "Romanian Handball League"
    ]
    
    DEFAULT_FIELDS = {
        "user_id": fields.UUID(required=True),
        "stake": fields.Float(required=True),
        "timestamp": fields.String(required=True),
        "recommended_events": fields.List(fields.Nested("RecommendedEventSchema"), required=True)
    }
    
    countries = [
        "USA", "Brazil", "Argentina", "Spain", "India", 
        "Australia", "Germany", "France", "Kenya", "Japan"
    ]
    
    events_data = {
    'dd5a5764-f41c-4ebe-8680-05a358bed9f0': [
       # Handball
       {'event_id': 139267, 'sport': 'handball', 'league': 'La Liga ASOBAL', 'country': 'Spain', 'odd': 3.06, 'begin_timestamp': '2025-04-01T14:25:48', 'end_timestamp': '2025-04-01T15:25:48'},
       {'event_id': 489726, 'sport': 'handball', 'league': 'La Liga ASOBAL', 'country': 'Spain', 'odd': 3.43, 'begin_timestamp': '2025-03-27T14:25:48', 'end_timestamp': '2025-03-27T15:25:48'},
       {'event_id': 744528, 'sport': 'handball', 'league': 'EHF Champions League', 'country': 'Germany', 'odd': 2.98, 'begin_timestamp': '2025-03-22T14:25:48', 'end_timestamp': '2025-03-22T15:25:48'},
       {'event_id': 518664, 'sport': 'handball', 'league': 'Lidl Starligue', 'country': 'France', 'odd': 3.15, 'begin_timestamp': '2025-03-10T14:25:48', 'end_timestamp': '2025-03-10T15:25:48'},
       
       # Basketball
       {'event_id': 312669, 'sport': 'basketball', 'league': 'EuroLeague', 'country': 'Spain', 'odd': 2.44, 'begin_timestamp': '2025-03-25T14:25:48', 'end_timestamp': '2025-03-25T15:25:48'},
       {'event_id': 820137, 'sport': 'basketball', 'league': 'NBA', 'country': 'USA', 'odd': 2.85, 'begin_timestamp': '2025-03-19T14:25:48', 'end_timestamp': '2025-03-19T15:25:48'},
       {'event_id': 968555, 'sport': 'basketball', 'league': 'EuroLeague', 'country': 'France', 'odd': 2.35, 'begin_timestamp': '2025-03-15T14:25:48', 'end_timestamp': '2025-03-15T15:25:48'},
       
       # Football
       {'event_id': 10948, 'sport': 'football', 'league': 'Premier League', 'country': 'UK', 'odd': 2.77, 'begin_timestamp': '2025-03-28T14:25:48', 'end_timestamp': '2025-03-28T15:25:48'},
       {'event_id': 458703, 'sport': 'football', 'league': 'La Liga', 'country': 'Spain', 'odd': 2.65, 'begin_timestamp': '2025-03-26T14:25:48', 'end_timestamp': '2025-03-26T15:25:48'},
       {'event_id': 862186, 'sport': 'football', 'league': 'Champions League', 'country': 'Germany', 'odd': 3.22, 'begin_timestamp': '2025-03-18T14:25:48', 'end_timestamp': '2025-03-18T15:25:48'}
    ]
}

 
    @staticmethod
    def get_random_league(sport="FOOTBALL"):
    
        if sport == "FOOTBALL":
            return random.choice(Config.FOOTBALL_LEAGUES)
        elif sport == "BASKETBALL":
            return random.choice(Config.BASKETBALL_LEAGUES)
        elif sport == "HANDBALL":
            return random.choice(Config.HANDBALL_LEAGUES)
        else:
            raise ValueError("Unsupported sport type")