import unittest 
from unittest.mock import patch, MagicMock
from flask import Flask
from uuid import UUID
from app.services import create_teams, create_users, create_events, populate_db, recommendation_generator,\
    create_casinos ,create_user_profile, create_purchased_coupons
from app.db_models import Event
from marshmallow import ValidationError

class TestCreateUserProfile(unittest.TestCase):
    
    @patch('app.services.db.session')
    @patch('app.services.UserProfile')
    @patch('app.services.randint') 
    def test_create_user_profile(self, mock_randint, MockUserProfile, mock_session):
        mock_randint.return_value = 976877

        mock_user_profile_instance = MagicMock()
        MockUserProfile.return_value = mock_user_profile_instance
        
        user_id = 917918
        
        profile_id = mock_randint.return_value

        
        create_user_profile(user_id)
        
        MockUserProfile.assert_called_once()
        args, kwargs = MockUserProfile.call_args
        
        self.assertEqual(kwargs['profile_id'], profile_id)
        self.assertEqual(kwargs['user_id'], user_id)
        self.assertEqual(kwargs['purchases_at_last_update'], 0)
        self.assertIn('last_updated', kwargs)
        
        mock_session.add.assert_called_once_with(mock_user_profile_instance)

        
        
class TestCreateTeams(unittest.TestCase):
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
     @patch('app.services.Team')
     @patch('app.services.TeamSchema')
     
     def test_create_teams(self, MockTeamSchema, MockTeam, mock_session):
         
         team_data_list = [
           {'team_id': 412264,'name': 'Team1479550626201', 'sport': "football"},
           {'team_id': 510759,'name': 'Team2008486497112', 'sport': "basketball"}
         ]
         
         mock_schema = MagicMock()

         
         mock_schema.load.side_effect = [
             {'team_id': 412264,'name': 'Team1479550626201', 'sport': "football"},
             {'team_id': 510759,'name': 'Team2008486497112', 'sport': "basketball"}
         ]
         
         MockTeamSchema.return_value = mock_schema
         
         mock_team1 = MagicMock()
         mock_team2 = MagicMock()
         MockTeam.side_effect = [mock_team1, mock_team2] 
             
         
         teams = create_teams(team_data_list)  
         
         self.assertEqual(teams, [mock_team1, mock_team2])
         self.assertEqual(mock_schema.load.call_count, 2)
         self.assertEqual(mock_session.add.call_count, 2)
         mock_session.add.assert_any_call(mock_team1)
         mock_session.add.assert_any_call(mock_team2)
         self.assertTrue(mock_session.commit.called)
         
     @patch('app.services.db.session')
     @patch('app.services.Team')
     @patch('app.services.TeamSchema')
     def test_create_teams_with_validation_error(self, MockTeamSchema, MockTeam, mock_session):
          
         team_data_list = [
             {'name': 'Team1479550626201'},
             {'bad_data': True}  
         ]
          
         mock_schema = MagicMock()
         mock_schema.load.side_effect = [
             {'team_id': 412264,'name': 'Team1479550626201', 'sport': "football"},
             ValidationError("Invalid team data") 
         ]
         MockTeamSchema.return_value = mock_schema
          
         mock_team = MagicMock()
         mock_team.team_id = 412264
         MockTeam.return_value = mock_team
        
         with patch('builtins.print') as mock_print:
            teams = create_teams(team_data_list)
        
            self.assertEqual(teams, [mock_team])
            mock_print.assert_called_once_with(
                    "Validation error: Invalid team data"
            )
          
         self.assertEqual(mock_schema.load.call_count, 2)
         self.assertEqual(mock_session.add.call_count, 1)
         self.assertTrue(mock_session.commit.called)
         
         
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
    @patch('app.services.create_user_profile')
    @patch('app.services.db.session')
    @patch('app.services.User')
    @patch('app.services.UserResponseSchema')
    
    def test_create_users(self, MockUserResponseSchema, MockUser, mock_session, mock_create_profile):
        
        user_data_list = [
            {'user_id': 917918,'birth_year': 1995, 'currency': 'USD', 'country': 'USA', 'gender': 'OTHER', \
             'timestamp': '2025-04-25T08:11:11.663775', 'favorite_sport': 'football'
             },
            {'user_id': 702249,'birth_year': 1961, 'currency': 'EUR', 'country': 'Australia', 'gender': 'FEMALE', \
             'timestamp': '2025-04-25T08:11:11.663906', 'favorite_sport': 'basketball'
             }
        ]
        
        mock_schema = MagicMock()

        mock_schema.load.side_effect = [
            {'user_id': 917918,'birth_year': 1995, 'currency': 'USD', 'country': 'USA', 'gender': 'OTHER', \
             'timestamp': '2025-04-25T08:11:11.663775', 'favorite_sport': 'football'
             },
            {'user_id': 702249,'birth_year': 1961, 'currency': 'EUR', 'country': 'Australia', 'gender': 'FEMALE', \
             'timestamp': '2025-04-25T08:11:11.663906', 'favorite_sport': 'basketball'
             }
            ]
        MockUserResponseSchema.return_value = mock_schema
        
        mock_user1 = MagicMock(user_id=917918)
        mock_user2 = MagicMock(user_id=702249)
        MockUser.side_effect = [mock_user1, mock_user2] 
        
        users = create_users(user_data_list)  
        
        self.assertEqual(users, [mock_user1, mock_user2])
        self.assertEqual(mock_schema.load.call_count, 2)
        self.assertEqual(mock_session.add.call_count, 2)
        self.assertEqual(mock_session.flush.call_count, 2)
        self.assertTrue(mock_session.commit.called)

        self.assertEqual(mock_create_profile.call_count, 2)
        mock_create_profile.assert_any_call(917918)
        mock_create_profile.assert_any_call(702249)
    
    @patch('app.services.create_user_profile') 
    @patch('app.services.db.session')
    @patch('app.services.User')
    @patch('app.services.UserResponseSchema')
    def test_create_users_with_validation_error(self, MockUserResponseSchema, MockUser, mock_session, mock_create_profile):
             
        user_data_list = [
            {'user_id': 917918},
            {'bad_data': True}  
        ]
             
        mock_schema = MagicMock()
        mock_schema.load.side_effect = [
            {'user_id': 917918,'birth_year': 1995, 'currency': 'USD', 'country': 'USA', 'gender': 'OTHER', \
                'timestamp': '2025-04-25T08:11:11.663775', 'favorite_sport': 'football'
            },
            ValidationError("Invalid user data")
        ]
        MockUserResponseSchema.return_value = mock_schema
        
        mock_user = MagicMock()
        mock_user.user_id = 917918
        MockUser.return_value = mock_user
             
        
        with patch('builtins.print') as mock_print:
            users = create_users(user_data_list)
     
            mock_print.assert_called_once_with(
                "Validation error: Invalid user data"
            )
                          
        self.assertEqual(users, [mock_user])
        self.assertEqual(mock_schema.load.call_count, 2)
        self.assertEqual(mock_session.add.call_count, 1)
        self.assertEqual(mock_session.flush.call_count, 1)
        self.assertTrue(mock_session.commit.called)
        
        mock_create_profile.assert_called_once_with(917918)
        
class TestCreateCasinos(unittest.TestCase):

    @patch('app.services.db.session')
    @patch('app.services.Casino')
    @patch('app.services.CasinoSchema')
    def test_create_casinos(self, MockCasinoSchema, MockCasino, mock_session):
        
        casino_data_list = [
            {'casino_id': 936470, 'name': 'Casino9404070009711', 'timestamp': '2025-04-25T08:11:11.825439'},
            {'casino_id': 211956, 'name': 'Casino7052112767381', 'timestamp': '2025-04-25T08:11:11.825454'}
        ]

        mock_schema = MagicMock()
        mock_schema.load.side_effect = casino_data_list
        MockCasinoSchema.return_value = mock_schema

        mock_casino1 = MagicMock()
        mock_casino2 = MagicMock()
        MockCasino.side_effect = [mock_casino1, mock_casino2]

        mock_user1 = MagicMock()
        mock_user2 = MagicMock()
        users = [mock_user1, mock_user2]

        casinos = create_casinos(casino_data_list, users=users)

        self.assertEqual(casinos, [mock_casino1, mock_casino2])
        self.assertEqual(mock_schema.load.call_count, 2)
        self.assertEqual(mock_session.add.call_count, 2)
        self.assertTrue(mock_session.commit.called)

        self.assertEqual(mock_casino1.users.extend.call_count, 0)
        self.assertEqual(mock_casino1.users.append.call_count, 2)
        self.assertEqual(mock_casino2.users.append.call_count, 2)
        mock_casino1.users.append.assert_any_call(mock_user1)
        mock_casino1.users.append.assert_any_call(mock_user2)

    @patch('app.services.db.session')
    @patch('app.services.Casino')
    @patch('app.services.CasinoSchema')
    def test_create_casinos_with_validation_error(self, MockCasinoSchema, MockCasino, mock_session):
        casino_data_list = [
            {'casino_id': 936470, 'name': 'Casino9404070009711', 'timestamp': '2025-04-25T08:11:11.825439'},
            {'invalid': 'data'}
        ]

        mock_schema = MagicMock()
        mock_schema.load.side_effect = [
            {'casino_id': 936470, 'name': 'Casino9404070009711', 'timestamp': '2025-04-25T08:11:11.825439'},
            Exception("Invalid casino data")
        ]
        MockCasinoSchema.return_value = mock_schema

        mock_casino = MagicMock()
        mock_casino.casino_id = 936470
        MockCasino.return_value = mock_casino

        with patch('builtins.print') as mock_print:
            casinos = create_casinos(casino_data_list)
    
            self.assertEqual(casinos, [mock_casino])
            mock_print.assert_called_once_with(
                "Validation error: Invalid casino data"
            )

        self.assertEqual(mock_schema.load.call_count, 2)
        self.assertEqual(mock_session.add.call_count, 1)
        self.assertTrue(mock_session.commit.called)

    @patch('app.services.db.session')
    @patch('app.services.Casino')
    @patch('app.services.CasinoSchema')
    def test_create_casinos_no_commit(self, MockCasinoSchema, MockCasino, mock_session):
        casino_data_list = [{'casino_id': 936470, 'name': 'Casino9404070009711', 'timestamp': '2025-04-25T08:11:11.825439'},]

        mock_schema = MagicMock()
        mock_schema.load.return_value = casino_data_list[0]
        MockCasinoSchema.return_value = mock_schema

        mock_casino = MagicMock()
        MockCasino.return_value = mock_casino

        casinos = create_casinos(casino_data_list, commit=False)

        self.assertEqual(casinos, [mock_casino])
        self.assertFalse(mock_session.commit.called)
       
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

    @patch('app.services.db.session')
    @patch('app.services.Event')
    @patch('app.services.EventSchema')
    @patch('app.services.Team')
    def test_create_events(self, MockTeam, MockEventSchema, MockEvent, mock_session):
        
        event_data_list = [
            {'event_id': 541823, 'home_team_id': 601225, 'away_team_id': 494044, 'sport': 'football',
             'begin_timestamp': '2025-03-28T08:11:11', 'end_timestamp': '2025-03-28T09:11:11',
             'country': 'USA', 'league': 'NBA', 'odd': 2.5}
        ]

        mock_schema = MagicMock()
        mock_schema.load.return_value = event_data_list[0]
        MockEventSchema.return_value = mock_schema

        mock_event = MagicMock()
        mock_event.home_team_id = 601225
        mock_event.away_team_id = 494044
        MockEvent.return_value = mock_event

        mock_home_team = MagicMock()
        mock_away_team = MagicMock()
        
        mock_query = MagicMock()
        mock_query.filter_by.side_effect = lambda **kwargs: MagicMock(
            first=MagicMock(return_value=mock_home_team if kwargs['team_id'] == 601225 else mock_away_team)
        )
        
        mock_session.query.return_value = mock_query

        events = create_events(event_data_list)

        self.assertEqual(events, [mock_event])
        self.assertEqual(mock_schema.load.call_count, 1)
        self.assertEqual(mock_event.teams.append.call_count, 2)
        mock_event.teams.append.assert_any_call(mock_home_team)
        mock_event.teams.append.assert_any_call(mock_away_team)
        mock_session.add.assert_called_once_with(mock_event)
        mock_session.commit.assert_called_once()

class TestCreatePurchasedCoupons(unittest.TestCase):

    @patch('app.services.db.session')
    @patch('app.services.PurchasedCouponSchema')
    @patch('app.services.PurchasedCoupon')
    @patch('app.services.UserProfile')
    def test_create_purchased_coupons(self, MockUserProfile, MockPurchasedCoupon, MockPurchasedCouponSchema, mock_session):
        
        coupon_data_list = [
            {
                'coupon_id': 296770,
                'user_id': 917918,
                'stake': 37.81,
                'timestamp': '2025-04-25T12:49:15.399950',
                'recommended_events': [
                    {'event_id': 870729, 'odd': 3.43},
                    {'event_id': 418502, 'odd': 2.35},
                    {'event_id': 542066, 'odd': 1.7}
                ]
            }
        ]
        user_id = 917918

        mock_profile = MagicMock()
        mock_profile.purchases_at_last_update = 5
        MockUserProfile.query.filter_by.return_value.first.return_value = mock_profile

        mock_schema = MagicMock()
        mock_schema.load.side_effect = coupon_data_list
        MockPurchasedCouponSchema.return_value = mock_schema

        mock_coupon = MagicMock()
        MockPurchasedCoupon.return_value = mock_coupon

        coupons = create_purchased_coupons(coupon_data_list, user_id)

        self.assertEqual(coupons, [mock_coupon])
        mock_session.add.assert_called_with(mock_coupon)
        mock_session.commit.assert_called_once()
    '''
    @patch('app.services.db.session')
    @patch('app.services.PurchasedCouponSchema')
    @patch('app.services.PurchasedCoupon')
    @patch('app.services.UserProfile')
    def test_create_purchased_coupons_user_profile_not_found(self, MockUserProfile, MockPurchasedCoupon, MockPurchasedCouponSchema, mock_session):
        
        coupon_data_list = [
            {
                'coupon_id': 123,
                'stake': 20.0,
                'timestamp': '2025-12-31T23:59:59',
                'recommended_events': [
                    {'event_id': 1001, 'odd': 1.8},
                    {'event_id': 1002, 'odd': 2.0},
                    {'event_id': 1003, 'odd': 1.5}
                ]
            }
        ]
        user_id = 789

        MockUserProfile.query.filter_by.return_value.first.return_value = None
        
        print("Running test_create_purchased_coupons_user_profile_not_found")

        with self.assertRaises(ValueError) as context:
            create_purchased_coupons(coupon_data_list, user_id)

        self.assertTrue("User profile not found" in str(context.exception))
    '''
    @patch('app.services.db.session')
    @patch('app.services.PurchasedCouponSchema')
    @patch('app.services.PurchasedCoupon')
    @patch('app.services.UserProfile')
    def test_create_purchased_coupons_exception_handling(self, MockUserProfile, MockPurchasedCoupon, MockPurchasedCouponSchema, mock_session):

        coupon_data_list = [
            {
                'coupon_id': 123,
                'user_id': 789,
                'stake': 20.0,
                'timestamp': '2025-12-31T23:59:59',
                'recommended_events': [
                    {'event_id': 1001, 'odd': 1.8},
                    {'event_id': 1002, 'odd': 2.0},
                    {'event_id': 1003, 'odd': 1.5}
                ]
            }
        ]
        user_id = 789

        mock_profile = MagicMock()
        MockUserProfile.query.filter_by.return_value.first.return_value = mock_profile

        mock_schema = MagicMock()
        mock_schema.load.side_effect = Exception("Validation error")
        MockPurchasedCouponSchema.return_value = mock_schema

        with self.assertRaises(ValueError) as context:
            create_purchased_coupons(coupon_data_list, user_id)

        self.assertTrue("Failed to create purchased coupons" in str(context.exception))

        mock_session.rollback.assert_called_once()
        mock_session.commit.assert_not_called()
'''        
class TestGenerateDynamicRecommendation(unittest.TestCase):
    
    def setUp(self):
       self.app = Flask(__name__)
       self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
       self.app_context = self.app.app_context()
       self.app_context.push()
   
    def tearDown(self):
       self.app_context.pop()
    
    @patch('app.db_models.Event.query')    
    
    def test_generate_dynamic_recommendation(self, mock_query):
        
        mock_event1 = MagicMock(spec=Event)
        mock_event1.event_id = UUID("1680812c-79af-4e57-b8bf-d1e6cdf61fe6")
        mock_event1.odd = 2.5
        
        
        mock_event2 = MagicMock(spec=Event)
        mock_event2.event_id = UUID("ccf716e6-eac5-46eb-a608-b369ad6cb59a")
        mock_event2.odd = 1.8
        
        mock_event3 = MagicMock(spec=Event)
        mock_event3.event_id = UUID("815f6ea0-d240-4e61-bf85-4a1c03afdd62")
        mock_event3.odd = 3.8
        
        mock_filter_by = MagicMock()
        mock_filter_by.limit.return_value.all.return_value = [mock_event1, mock_event2, mock_event3]
        mock_query.filter_by.return_value = mock_filter_by      
        
        mock_user_id = UUID("550e8400-e29b-41d4-a716-446655440000")
        recommendation = dynamic_recommendation(user_id = mock_user_id, events = 3, favorite_sport = "football")
        
        self.assertEqual(len(recommendation["recommended_events"]), 3)
        self.assertEqual(recommendation["user_id"], mock_user_id)
        self.assertIsNotNone(recommendation["timestamp"])
        self.assertGreaterEqual(recommendation["stake"], 1.5)
        self.assertLessEqual(recommendation["stake"], 50.5)
        

        event1 = recommendation["recommended_events"][0]
        self.assertEqual(event1["event_id"], UUID("1680812c-79af-4e57-b8bf-d1e6cdf61fe6"))
        self.assertEqual(event1["odd"], 2.5)

        event2 = recommendation["recommended_events"][1]
        self.assertEqual(event2["event_id"], UUID("ccf716e6-eac5-46eb-a608-b369ad6cb59a"))
        self.assertEqual(event2["odd"], 1.8)
        
        event3 = recommendation["recommended_events"][2]
        self.assertEqual(event3["event_id"], UUID("815f6ea0-d240-4e61-bf85-4a1c03afdd62"))
        self.assertEqual(event3["odd"], 3.8)
        
        self.assertEqual(recommendation["user_id"], mock_user_id)  
        self.assertIsNotNone(recommendation["timestamp"])
        self.assertGreaterEqual(recommendation["stake"], 1.5)
        self.assertLessEqual(recommendation["stake"], 50.5)

class TestRecommendationGenerator(unittest.TestCase):
    
    
    @patch("app.services.generate_value")
    @patch("app.services.static_recommendation")
    
    def test_static_recommender(self, mock_static_recommendation, mock_generate_value):
        config = {
            "recommender_type": "Static",
            "recommendation_schema": {
                "user_id": {"type": "uuid"},
                "stake": {"type": "float"},
                "timestamp": {"type": "string"},
                "custom_field": {"type": "string", "source_field": "missing_field"}
            }
        }
        
        user_id = "123e4567-e89b-12d3-a456-426614174000"
        favorite_sport = "football"
        
        
        mock_static_recommendation.return_value = {
            "user_id": user_id,
            "stake": 5.0,
            "timestamp": "2025-04-04T12:00:00"
        }
        
        mock_generate_value.return_value = "default_value"
        
        result = recommendation_generator(config, user_id, favorite_sport)
        
        self.assertEqual(result["user_id"], user_id)
        self.assertEqual(result["stake"], 5.0)
        self.assertEqual(result["timestamp"], "2025-04-04T12:00:00")
        self.assertEqual(result["custom_field"], "default_value")
    
    
    @patch("app.services.generate_value")
    @patch("app.services.dynamic_recommendation")
    
    def test_dynamic_recommender(self, mock_dynamic_recommendation, mock_generate_value):
        
        config = {
           "recommender_type": "Dynamic",
           "recommendation_schema": {
               "events": {"type": "list", "source_field": "recommended_events"}
           }
        }
        
        user_id = "123e4567-e89b-12d3-a456-426614174000"
        favorite_sport = "basketball"
        
        mock_dynamic_recommendation.return_value = {
            "recommended_events": ["event1", "event2"]
        }
        
        mock_generate_value.return_value = []

        result = recommendation_generator(config, user_id, favorite_sport)
        
        self.assertEqual(result["events"], ["event1", "event2"])


'''

'''        
class TestPopulateDb(unittest.TestCase):

    @patch('app.services.create_users')
    @patch('app.services.create_teams')
    @patch('app.services.create_events')
    @patch('builtins.print')
    
    def test_populate_db(self, mock_print, mock_create_events, mock_create_teams, mock_create_users):
        mock_users = [MagicMock for i in range(5)]
        mock_teams = [MagicMock() for i in range(3)]
        mock_events = [MagicMock() for i in range(3)]
        
        mock_create_users.return_value = mock_users
        mock_create_teams.return_value = mock_teams
        mock_create_events.return_value = mock_events
        
        result = populate_db()
        
        mock_create_users.assert_called_once()
        mock_create_teams.assert_called_once
        mock_create_events.assert_called_once_with(n = 3, teams = mock_teams)
        
        mock_print.assert_called_once_with(f"Inserted {len(mock_users)} users, "
                                           f"{len(mock_teams)} teams, "
                                           f"and {len(mock_events)} events.")
        self.assertIsNone(result)
   
'''            
if __name__ == '__main__':
    unittest.main()
             