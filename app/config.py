import os
from faker import Faker
import random

fake = Faker()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "postgresql://user:1234@localhost:5432/recommendation_system"
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

 
    @staticmethod
    def get_random_league(sport="football"):
    
        import random
        if sport == "football":
            return random.choice(Config.FOOTBALL_LEAGUES)
        elif sport == "basketball":
            return random.choice(Config.BASKETBALL_LEAGUES)
        elif sport == "handball":
            return random.choice(Config.HANDBALL_LEAGUES)
        else:
            raise ValueError("Unsupported sport type")