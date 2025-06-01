import unittest
from unittest.mock import patch, MagicMock
from app.utils import generate_unique_user_id, get_random_casino_id, get_random_user_id, create_db_per_casino, \
db_engine_cache, get_casino_db_session, generate_dummy_users, generate_dummy_casinos, generate_dummy_events, \
generate_dummy_teams, generate_dummy_purchased_coupons, generate_dummy_purchased_coupons_with_dummy_events
from app.config import Config
import psycopg2
from datetime import datetime

'''
class TestUtils(unittest.TestCase):
'''    
class TestGenerateUniqueUserId(unittest.TestCase):
    @patch('app.utils.randint')
    def test_generate_unique_user_id(self, mock_randint):
        session = MagicMock()
        Model = MagicMock()
        
        mock_randint.side_effect = [123, 456]
        
        session.query().filter_by().first.side_effect = [True, None]
        
        result = generate_unique_user_id(session, Model)
        
        self.assertEqual(result, 456)
        self.assertEqual(mock_randint.call_count, 2)
        session.query.assert_called_with(Model.id)
    
class TestGetRandomCasinoId(unittest.TestCase):
    def setUp(self):
        global cached_casino_ids
        cached_casino_ids = None
    
    @patch('app.utils.db')
    @patch('app.utils.random.choice')
    def test_returns_random_casino_id_after_fetch(self, mock_choice, mock_db):        
        mock_db.session.query.return_value.all.return_value = [(1,), (2,), (3,)]
        mock_choice.return_value = 2
        
        casino_id = get_random_casino_id()
        
        self.assertEqual(casino_id, 2)
        mock_db.session.query.assert_called_once()
        mock_choice.assert_called_once_with([1, 2, 3])
        
class TestGetRandomUserId:
    def setUp(self):
        global cached_user_ids
        cached_user_ids = None
    
    @patch('app.utils.get_casino_db_session')
    @patch('app.utils.random.choice')
    def test_returns_random_user_id_after_fetch(self, mock_choice, mock_get_session):
        mock_session = MagicMock()
        mock_session.query.return_value.all.return_value = [(1,), (2,), (3,)]
        mock_get_session.return_value = mock_session
        mock_choice.return_value = 2
        
        casino_id = 111
        user_id = get_random_user_id(casino_id=casino_id)
        
        self.assertEqual(user_id, 2)
        mock_session.query.assert_called_once()
        mock_choice.assert_called_once_with([1, 2, 3])
        mock_get_session.assert_called_once_with(casino_id)
        
class TestCreateDbPerCasino(unittest.TestCase):

    @patch('app.utils.SharedBase.metadata.create_all')
    @patch('app.utils.create_engine')
    @patch('app.utils.psycopg2.connect')
    def test_create_db_successfully(self, mock_connect, mock_create_engine, mock_create_all):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        db_name = create_db_per_casino(123)

        self.assertEqual(db_name, "casino_123")
        mock_connect.assert_called_once()
        mock_cursor.execute.assert_called_with("CREATE DATABASE casino_123")
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()
        mock_create_engine.assert_called_once()
        mock_create_all.assert_called_once()

    @patch('app.utils.SharedBase.metadata.create_all')
    @patch('app.utils.create_engine')
    @patch('app.utils.psycopg2.connect')
    def test_create_db_already_exists(self, mock_connect, mock_create_engine, mock_create_all):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = psycopg2.errors.DuplicateDatabase
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        db_name = create_db_per_casino(456)

        self.assertEqual(db_name, "casino_456")
        mock_cursor.execute.assert_called_once_with("CREATE DATABASE casino_456")
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()
        mock_create_engine.assert_called_once()
        mock_create_all.assert_called_once()
        
class TestGetCasinoDbSession(unittest.TestCase):
    
    def setUp(self):
        db_engine_cache.clear()
    
    @patch('app.utils.create_engine')
    @patch('app.utils.sessionmaker')
    def test_get_casino_db_session_successfully(self, mock_session_maker, mock_create_engine):
        casino_id = 42
        mock_engine = MagicMock(name='Engine')
        mock_create_engine.return_value = mock_engine
        
        mock_session = MagicMock(name='Session')
        mock_session_maker.return_value = MagicMock(return_value=mock_session)
        
        session = get_casino_db_session(casino_id)
        
        mock_create_engine.assert_called_once()
        called_url = mock_create_engine.call_args[0][0]
        self.assertIn(f"casino_{casino_id}", called_url)
        
        mock_session_maker.assert_called_once_with(bind=mock_engine)
        self.assertEqual(session, mock_session)

        self.assertIn(casino_id, db_engine_cache)
        self.assertEqual(db_engine_cache[casino_id], mock_engine)
        
    @patch('app.utils.create_engine')
    @patch('app.utils.sessionmaker')
    def test_uses_cached_engine_if_exists(self, mock_session_maker, mock_create_engine):
        casino_id = 99
        mock_engine = MagicMock(name='CachedEngine')
        db_engine_cache[casino_id] = mock_engine
        mock_session = MagicMock(name='Session')
        mock_session_maker.return_value = MagicMock(return_value=mock_session)

        session = get_casino_db_session(casino_id)
        mock_create_engine.assert_not_called()

        mock_session_maker.assert_called_once_with(bind=mock_engine)

        self.assertEqual(session, mock_session)
        
        
class TestGenerateDummyUsers(unittest.TestCase):
    def test_generate_dummy_users_default_count(self):
        users = generate_dummy_users()
        self.assertEqual(len(users), 10)

    def test_generate_dummy_users_custom_count(self):
        users = generate_dummy_users(5)
        self.assertEqual(len(users), 5)

    def test_generate_dummy_users_data_structure(self):
        users = generate_dummy_users(3)
        required_keys = {
            "birth_year", "currency", "country", "gender",
            "timestamp", "name", "surname", "favorite_sport"
        }

        for user in users:
            self.assertTrue(required_keys.issubset(user.keys()))

            self.assertIsInstance(user["birth_year"], int)
            self.assertIn(user["currency"], ("EUR", "USD", "GBP"))
            self.assertIn(user["country"], Config.countries)
            self.assertIn(user["gender"], ("MALE", "FEMALE", "OTHER"))
            self.assertIn(user["favorite_sport"], ("FOOTBALL", "BASKETBALL", "HANDBALL"))

            try:
                datetime.fromisoformat(user["timestamp"])
            except ValueError:
                self.fail("timestamp is not a valid ISO 8601 string")

            self.assertIsInstance(user["name"], str)
            self.assertIsInstance(user["surname"], str)

class TestGenerateDummyCasinos(unittest.TestCase):
    def test_generate_dummy_casinos_default_count(self):
        casinos = generate_dummy_casinos()
        self.assertEqual(len(casinos), 3)

    def test_generate_dummy_casinos_custom_count(self):
        casinos = generate_dummy_casinos(5)
        self.assertEqual(len(casinos), 5)
    
    @patch('app.utils.random.randint')
    def test_generate_dummy_casinos_data_structure(self, mock_randint):
        mock_randint.return_value = 123
        casinos = generate_dummy_casinos(1)
         
        self.assertEqual(len(casinos), 1)
        casino = casinos[0]
        
        self.assertEqual(casino["db_name"], "Casino123")
        
        try:
            datetime.fromisoformat(casino["timestamp"])
        except ValueError:
            self.fail("timestamp is not a valid ISO string")

class TestGenerateDummyTeams(unittest.TestCase):
    def test_generate_dummy_teams_count_and_structure(self):
        teams = generate_dummy_teams(5)
        self.assertEqual(len(teams), 5)

        for team in teams:
            self.assertIn("name", team)
            self.assertTrue(team["name"].startswith("Team"))
            self.assertTrue(team["name"][4:].isdigit())
            self.assertIn("sport", team)
            self.assertIn(team["sport"], ("FOOTBALL", "HANDBALL", "BASKETBALL"))
            

class TestGenerateDummyEvents(unittest.TestCase):
    @patch('app.utils.Config.get_random_league', return_value="Premier League")
    @patch('app.utils.random_end_timestamp')
    @patch('app.utils.random_begin_timestamp')
    def test_generate_dummy_events_structure(self, mock_begin, mock_end, mock_league):
        mock_begin.return_value = "2025-01-01T10:00:00Z"
        mock_end.return_value = "2025-01-01T12:00:00Z"
        
        teams = [
            {
                "name": "Team123410", 
                "sport": "FOOTBALL"
            },
            {
                "name": "Team256754", 
                "sport": "FOOTBALL"
            },
            {
                "name": "Team348743", 
                "sport": "BASKETBALL"
            },
            {
                "name": "Team433829", 
                "sport": "BASKETBALL"
            },  
            {
                "name": "Team555246", 
                "sport": "HANDBALL"
            },
            {
                "name": "Team698767", 
                "sport": "HANDBALL"
            },
        ]

        events = generate_dummy_events(teams, n=2)
        self.assertTrue(len(events) > 0)

        for event in events:
            self.assertIn("begin_timestamp", event)
            self.assertIn("end_timestamp", event)
            self.assertIn("country", event)
            self.assertIn("league", event)
            self.assertIn("home_team", event)
            self.assertIn("away_team", event)
            self.assertIn("sport", event)
            self.assertIn("odd", event)
            self.assertIsInstance(event["odd"], float)
            

class TestGenerateDummyPurchasedCoupons(unittest.TestCase):
    def test_generate_dummy_coupons_structure_and_count(self):
        events = [
            {
                "country": "USA", 
                "league": "NBA", 
                "home_team": "Lakers", 
                "away_team": "Bulls", 
                "sport": "BASKETBALL", 
                "odd": 2.1
            },
            {
                "country": "Greece", 
                "league": "La Liga", 
                "home_team": "Arsenal", 
                "away_team": "Chelsea", 
                "sport": "FOOTBALL", 
                "odd": 1.8
            },
            {
                "country": "Germany", 
                "league": "Bundesliga", 
                "home_team": "Bayern", 
                "away_team": "Dortmund", 
                "sport": "FOOTBALL", 
                "odd": 2.5
            },
            {
                "country": "France", 
                "league": "Ligue1", 
                "home_team": "PSG", 
                "away_team": "Lyon", 
                "sport": "FOOTBALL", 
                "odd": 1.9
            },
        ]
        coupons, user_id = generate_dummy_purchased_coupons(events, user_id="123", n=2)
        self.assertEqual(len(coupons), 2)
        self.assertEqual(user_id, "123")

        for coupon in coupons:
            self.assertIn("user_id", coupon)
            self.assertIn("stake", coupon)
            self.assertIn("timestamp", coupon)
            self.assertIn("recommended_events", coupon)
            self.assertEqual(len(coupon["recommended_events"]), 3)

    def test_generate_dummy_coupons_fails_on_few_events(self):
        events = [{"country": "USA", 
                   "league": "NBA", 
                   "home_team": "Bayern", 
                   "away_team": "Dortmund", 
                   "sport": "BASKETBALL", 
                   "odd": 2.0}]
        with self.assertRaises(ValueError):
            generate_dummy_purchased_coupons(events, user_id="222")
            
            
            
class TestGenerateDummyPurchasedCouponsWithDummyEvents(unittest.TestCase):

    @patch("app.utils.generate_dummy_events")
    @patch("app.utils.random.uniform")
    @patch("app.utils.datetime")
    def test_coupon_generation_with_dummy_events(self, mock_datetime, mock_uniform, mock_generate_events):
    
        fixed_time = datetime(2025, 1, 1, 12, 0, 0)
        mock_datetime.utcnow.return_value = fixed_time
        mock_uniform.return_value = 50.0
    
        teams = [{"name": f"Team{i}", "sport": "FOOTBALL"} for i in range(6)]
    
        mock_generate_events.return_value = [
            {
                "country": "UK",
                "league": "EPL",
                "home_team": f"TeamA{i}",
                "away_team": f"TeamB{i}",
                "sport": "FOOTBALL",
                "odd": 2.0 + i * 0.1
            }
            for i in range(6)
        ]
    
        user_id = "123"
        coupons = generate_dummy_purchased_coupons_with_dummy_events(teams, user_id, n=2)
    
        self.assertEqual(len(coupons), 2)
    
        for coupon in coupons:
            self.assertEqual(coupon["user_id"], user_id)
            self.assertEqual(coupon["stake"], 50.0)
            self.assertEqual(coupon["timestamp"], fixed_time.isoformat())
            self.assertEqual(len(coupon["recommended_events"]), 3)
            
            




    
        








