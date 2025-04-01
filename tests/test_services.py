import unittest 
from unittest.mock import patch, MagicMock
from flask import Flask
from uuid import UUID
from app.services import create_participants, create_users, create_events, populate_db, generate_dummy_recommendation
from app.db_models import Event

class TestCreateParticipants(unittest.TestCase):
     '''
     def setUp(self):
         self.app = Flask(__name__)
         self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
         self.app_context = self.app.app_context()
         self.app_context.push()
   
     def tearDown(self):
         self.app_context.pop()
     '''
     @patch('app.services.db.session')
     @patch('app.services.ParticipantSchema')
     
     def test_create_participants(self, MockParticipantSchema, mock_session):
         
         mock_schema = MagicMock()
         MockParticipantSchema.return_value = mock_schema
         mock_schema.load.return_value = {
            "participant_id": UUID("3831a419-a5ec-4c25-a5e5-fc63bad3d04d"),
            "name": "Team3904668074",
            "sport": "football"
         }
         
         mock_session.commit = MagicMock()
         mock_session.add = MagicMock()
         
         participants = create_participants(3)  
         
         self.assertEqual(len(participants), 3)
         self.assertEqual(mock_session.add.call_count, 3)
         self.assertEqual(mock_schema.load.call_count, 3)
         mock_session.commit.assert_called_once()

         self.assertEqual(participants[0].participant_id, UUID('3831a419-a5ec-4c25-a5e5-fc63bad3d04d'))
         self.assertEqual(participants[0].name, 'Team3904668074')
         self.assertEqual(participants[0].sport, 'football')
         
class TestCreateUsers(unittest.TestCase):
    '''
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        self.app_context.pop()
    '''
    @patch('app.services.db.session')
    @patch('app.services.UserResponseSchema')
    
    def test_create_users(self, MockUserResponseSchema, mock_session):
        
        mock_schema = MagicMock()
        MockUserResponseSchema.return_value = mock_schema
        mock_schema.load.return_value = {
            "birth_year": 2003,
            "currency": "EUR",
            "country": "GREECE",
            "gender": "MALE",
            "timestamp": "2025-03-29T11:20:20.182205",
            "user_id": UUID("3127f844-6cf5-4ca5-853b-78b3e50328a6")
        }
        
        mock_session.commit = MagicMock()
        mock_session.add = MagicMock()
        
        users = create_users(3)
        
        self.assertEqual(len(users), 3)
        self.assertEqual(mock_session.add.call_count, 3)
        self.assertEqual(mock_schema.load.call_count, 3)
        mock_session.commit.assert_called_once()

        self.assertEqual(users[0].birth_year, 2003)
        self.assertEqual(users[0].currency, 'EUR')
        self.assertEqual(users[0].country, 'GREECE')
        self.assertEqual(users[0].gender, 'MALE')
        self.assertEqual(users[0].timestamp, '2025-03-29T11:20:20.182205')
        self.assertEqual(users[0].user_id, UUID('3127f844-6cf5-4ca5-853b-78b3e50328a6'))
        
class TestCreateEvents(unittest.TestCase):
    '''
    def setUp(self):
       self.app = Flask(__name__)
       self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
       self.app_context = self.app.app_context()
       self.app_context.push()
   
    def tearDown(self):
       self.app_context.pop()
    '''
    @patch('app.services.random_begin_timestamp', return_value = "2025-03-09T11:20:20")
    @patch('app.services.random_end_timestamp', return_value = "2025-04-02T11:20:20")
    @patch('app.services.db.session')
    @patch('app.services.EventSchema')
    @patch('app.config.Config.get_random_league', return_value="Champions League")  
    def test_create_events(self, mock_get_league, MockEventSchema, mock_session, mock_random_begin, mock_random_end):
        
        mock_schema = MagicMock()
        MockEventSchema.return_value = mock_schema
        
        participant1 = {
           "participant_id": UUID('5fe12ce2-b3e6-40ad-b670-87ea22bddfd4'),
           "name": "Team1172902903",
           "sport": "football"
        }
        participant2 = {
           "participant_id": UUID('ce2ec9ba-afb7-4efc-bd7e-3d79420ffe0f'),
           "name": "Team3904668074",
           "sport": "football"
        }
        
        mock_schema.load.return_value = {
            "event_id": "1680812c-79af-4e57-b8bf-d1e6cdf61fe6",
            "begin_timestamp": mock_random_begin.return_value,
            "end_timestamp":  mock_random_end.return_value,
            "country": "GREECE",
            "league": "Champions League",
            "sport": "football",
            "odd": 3.5,
            "participants": [participant1,participant2]
        }
        
        mock_session.commit = MagicMock()
        mock_session.add = MagicMock()
        
        mock_participants = [
          MagicMock(participant_id = participant1["participant_id"], name = participant1["name"]),
          MagicMock(participant_id = participant2["participant_id"], name = participant2["name"])
        ]
        
        events = create_events(n=2, participants = mock_participants)
        
        self.assertEqual(len(events), 2)
        self.assertEqual(mock_session.add.call_count, 2)
        self.assertEqual(mock_schema.load.call_count, 2)
        mock_session.commit.assert_called_once()
        
        
        self.assertEqual(events[0].begin_timestamp, mock_random_begin.return_value)
        self.assertEqual(events[0].end_timestamp, mock_random_end.return_value)
        self.assertEqual(events[0].country, "GREECE")
        self.assertEqual(events[0].league, "Champions League")
        self.assertEqual(events[0].sport, "football")
        self.assertEqual(events[0].odd, 3.5)
        
class TestGenerateDummyRecommendation(unittest.TestCase):
    
    def setUp(self):
       self.app = Flask(__name__)
       self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
       self.app_context = self.app.app_context()
       self.app_context.push()
   
    def tearDown(self):
       self.app_context.pop()
    
    @patch('app.db_models.Event.query')    
    
    def test_generate_dummy_recommendation(self, mock_query):
        '''
        mock_query = MagicMock()
        MockEventQuery.return_value = mock_query
        '''
        
        mock_event1 = MagicMock(spec=Event)
        mock_event1.event_id = UUID("1680812c-79af-4e57-b8bf-d1e6cdf61fe6")
        mock_event1.begin_timestamp = "2025-03-09T11:20:20.196715"
        mock_event1.end_timestamp = "2025-04-02T11:20:20.196726"
        mock_event1.country = "USA"
        mock_event1.league = "Champions League"
        mock_event1.sport = "football"
        mock_event1.odd = 2.5
        
        mock_participant1 = MagicMock()
        mock_participant1.participant_id = UUID("8f7be065-12cb-4c25-ac1f-46e8ecfb3939")
        mock_participant1.name = "Team3904668074"
        mock_participant1.sport = "football"
        mock_event1.participants = [mock_participant1]
        
        mock_event2 = MagicMock(spec=Event)
        mock_event2.event_id = UUID("ccf716e6-eac5-46eb-a608-b369ad6cb59a")
        mock_event2.begin_timestamp = "2025-03-08T11:20:20.70354"
        mock_event2.end_timestamp = "2025-04-27T11:20:20.703546"
        mock_event2.country = "Greece"
        mock_event2.league = "Europa League"
        mock_event2.sport = "football"
        mock_event2.odd = 1.8
        
        mock_participant2 = MagicMock()
        mock_participant2.participant_id = UUID("fc2e7fa0-9af3-4594-8506-8cd56948a5ba")
        mock_participant2.name = "Team1172902903"
        mock_participant2.sport = "football"
        mock_event2.participants = [mock_participant2]
     
        
        mock_filter_by = MagicMock()
        mock_filter_by.limit.return_value.all.return_value = [mock_event1, mock_event2]
        mock_query.filter_by.return_value = mock_filter_by      
        
        mock_user_id = UUID("550e8400-e29b-41d4-a716-446655440000")
        recommendation = generate_dummy_recommendation(user_id = mock_user_id, events = 2, favorite_sport = "football")
        
        self.assertEqual(len(recommendation["recommended_events"]), 2)
        self.assertEqual(recommendation["user_id"], mock_user_id)
        self.assertIsNotNone(recommendation["timestamp"])
        self.assertGreaterEqual(recommendation["stake"], 1.5)
        self.assertLessEqual(recommendation["stake"], 50.5)
        

        event1 = recommendation["recommended_events"][0]
        self.assertEqual(event1["event_id"], UUID("1680812c-79af-4e57-b8bf-d1e6cdf61fe6"))
        self.assertEqual(event1["begin_timestamp"], "2025-03-09T11:20:20.196715")
        self.assertEqual(event1["end_timestamp"], "2025-04-02T11:20:20.196726")
        self.assertEqual(event1["country"], "USA")
        self.assertEqual(event1["league"], "Champions League")
        self.assertEqual(event1["sport"], "football")
        self.assertEqual(event1["odd"], 2.5)
        self.assertEqual(event1["participants"][0]["participant_id"], UUID("8f7be065-12cb-4c25-ac1f-46e8ecfb3939"))
        self.assertEqual(event1["participants"][0]["name"], "Team3904668074")
        self.assertEqual(event1["participants"][0]["sport"], "football")

        event2 = recommendation["recommended_events"][1]
        self.assertEqual(event2["event_id"], UUID("ccf716e6-eac5-46eb-a608-b369ad6cb59a"))
        self.assertEqual(event2["begin_timestamp"], "2025-03-08T11:20:20.70354")
        self.assertEqual(event2["end_timestamp"], "2025-04-27T11:20:20.703546")
        self.assertEqual(event2["country"], "Greece")
        self.assertEqual(event2["league"], "Europa League")
        self.assertEqual(event2["sport"], "football")
        self.assertEqual(event2["odd"], 1.8)
        self.assertEqual(event2["participants"][0]["participant_id"], UUID("fc2e7fa0-9af3-4594-8506-8cd56948a5ba"))
        self.assertEqual(event2["participants"][0]["name"], "Team1172902903")
        self.assertEqual(event2["participants"][0]["sport"], "football")
        
        self.assertEqual(recommendation["user_id"], mock_user_id)  
        self.assertIsNotNone(recommendation["timestamp"])
        self.assertGreaterEqual(recommendation["stake"], 1.5)
        self.assertLessEqual(recommendation["stake"], 50.5)
        
class TestPopulateDb(unittest.TestCase):
    '''
    def setUp(self):
       self.app = Flask(__name__)
       self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
       self.app_context = self.app.app_context()
       self.app_context.push()
   
    def tearDown(self):
       self.app_context.pop()
    '''

    @patch('app.services.create_users')
    @patch('app.services.create_participants')
    @patch('app.services.create_events')
    @patch('builtins.print')
    
    def test_populate_db(self, mock_print, mock_create_events, mock_create_participants, mock_create_users):
        mock_users = [MagicMock for i in range(5)]
        mock_participants = [MagicMock() for i in range(3)]
        mock_events = [MagicMock() for i in range(3)]
        
        mock_create_users.return_value = mock_users
        mock_create_participants.return_value = mock_participants
        mock_create_events.return_value = mock_events
        
        result = populate_db()
        
        mock_create_users.assert_called_once()
        mock_create_participants.assert_called_once
        mock_create_events.assert_called_once_with(n = 3, participants = mock_participants)
        
        mock_print.assert_called_once_with(f"Inserted {len(mock_users)} users, "
                                           f"{len(mock_participants)} participants, "
                                           f"and {len(mock_events)} events.")
        self.assertIsNone(result)
   
            
if __name__ == '__main__':
    unittest.main()
             