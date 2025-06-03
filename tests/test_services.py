import unittest 
from unittest.mock import patch, MagicMock
from app.services import create_teams, create_users, create_events, recommendation_generator,\
create_casinos, create_user_profile, create_purchased_coupons, register_recommendation, recommender_registry,\
get_all_sport_league_tuples, dynamic_recommendation, inference_score_recommendation, populate_db
from marshmallow import ValidationError
from datetime import datetime
import json


class TestCreateUserProfile(unittest.TestCase):
    
    @patch('app.services.generate_unique_id')
    @patch('app.services.UserProfile')
    def test_create_user_profile(self, MockUserProfile, mock_generate_id):
        profile_id = 976877
        user_id = 917918
        
        mock_generate_id.return_value = profile_id
        mock_user_profile_instance = MagicMock()
        MockUserProfile.return_value = mock_user_profile_instance

        mock_session = MagicMock()

        
        create_user_profile(user_id, mock_session)

        
        MockUserProfile.assert_called_once()
        args, kwargs = MockUserProfile.call_args

        self.assertEqual(kwargs['id'], profile_id)
        self.assertEqual(kwargs['user_id'], user_id)
        self.assertEqual(kwargs['purchases_at_last_update'], 0)
        self.assertIn('last_updated', kwargs)

        mock_session.add.assert_called_once_with(mock_user_profile_instance)

        
        
class TestCreateTeams(unittest.TestCase):
    
     @patch('app.services.uppercase_dict')
     @patch('app.services.generate_unique_id')
     @patch('app.services.get_casino_db_session')
     @patch('app.services.Team')
     @patch('app.services.TeamSchema')     
     def test_create_teams(self, MockTeamSchema, MockTeam, mock_get_session, mock_generate_id,
                           mock_uppercase_dict):
         
         casino_id = 23341
         team_data_list = [
           {
            'name': 'Team1479550626201', 
            'sport': "football"
           },
           {
            'name': 'Team2008486497112', 
            'sport': "basketball"
           }
         ]
         
         mock_generate_id.side_effect = [917918, 702249]
         
         mock_session = MagicMock()
         mock_get_session.return_value = mock_session
         
         team_data_upper_1 = {
             'id': 917918,
             'name': 'TEAM1479550626201', 
             'sport': "FOOTBALL"
         }
         team_data_upper_2 = {
             'id': 702249,
             'name': 'TEAM2008486497112', 
             'sport': "BASKETBALL"
         }
         
         mock_uppercase_dict.side_effect = [team_data_upper_1, team_data_upper_2]
         
         mock_schema = MagicMock()
         mock_schema.load.side_effect = [team_data_upper_1, team_data_upper_2]
         MockTeamSchema.return_value = mock_schema
         
         mock_team1 = MagicMock(id=917918)
         mock_team2 = MagicMock(id=702249)
         MockTeam.side_effect = [mock_team1, mock_team2]
         
         mock_session.query().filter().first.return_value = None
         
         teams = create_teams(team_data_list, casino_id=casino_id)  
         
         MockTeamSchema.return_value = mock_schema
         
         self.assertEqual(teams, [mock_team1, mock_team2])
         self.assertEqual(mock_schema.load.call_count, 2)
         self.assertEqual(mock_session.add.call_count, 2)
         mock_session.add.assert_any_call(mock_team1)
         mock_session.add.assert_any_call(mock_team2)
         self.assertTrue(mock_session.commit.called)
     
     @patch('app.services.uppercase_dict')
     @patch('app.services.generate_unique_id')
     @patch('app.services.get_casino_db_session')
     @patch('app.services.Team')
     @patch('app.services.TeamSchema')
     def test_create_teams_with_validation_error(self, MockTeamSchema, MockTeam, mock_get_session, mock_generate_id,
                                                 mock_uppercase_dict):
         team_data_list = [
             {'name': 'Team1479550626201',
              'sport': "football"},
             {'bad_data': True}  
         ]
         
         mock_generate_id.side_effect = [917918, 999999]

         mock_session = MagicMock()
         mock_get_session.return_value = mock_session
         
         mock_session.query.return_value.filter.return_value.first.return_value = None
         
         team_data_upper_1 = {
             'id': 917918,
             'name': 'TEAM1479550626201',
             'sport': "FOOTBALL"
         }
         
         team_data_upper_2 = {'bad_data': True}
         
         mock_uppercase_dict.side_effect = [team_data_upper_1, team_data_upper_2]
         
         mock_schema = MagicMock()
         mock_schema.load.side_effect = [
             team_data_upper_1,
             ValidationError("Invalid team data")
         ]
          
         MockTeamSchema.return_value = mock_schema
         
         mock_team = MagicMock()
         mock_team.id = 917918
         MockTeam.return_value = mock_team
         
         with patch('builtins.print') as mock_print:
             teams = create_teams(team_data_list,  casino_id=784672)
             printed_calls = [call.args[0] for call in mock_print.call_args_list]
             self.assertTrue(
                 any("Validation error for team" in msg and "Invalid team data" in msg for msg in printed_calls),
                 f"Expected error message not found in: {printed_calls}"
            )
         self.assertEqual(teams, [mock_team])
         self.assertEqual(mock_schema.load.call_count, 2)
         self.assertEqual(mock_session.add.call_count, 1)
         self.assertEqual(mock_session.flush.call_count, 0)
         self.assertTrue(mock_session.commit.called)
         
         
class TestCreateUsers(unittest.TestCase):

    @patch('app.services.uppercase_dict')
    @patch('app.services.create_user_profile')
    @patch('app.services.generate_unique_id')
    @patch('app.services.get_casino_db_session')
    @patch('app.services.User')
    @patch('app.services.UserResponseSchema')
    def test_create_users(self, MockUserResponseSchema, MockUser, mock_get_session, mock_generate_id,
                          mock_create_profile, mock_uppercase_dict):
        
        casino_id = 23341
        user_data_list = [
            {'birth_year': 1995,
             'currency': 'USD', 
             'country': 'USA', 
             'gender': 'OTHER', 
             'timestamp': '2025-04-25T08:11:11.663775', 
             'favorite_sport': 'football'
             },
            {'birth_year': 1961, 
             'currency': 'EUR', 
             'country': 'Australia', 
             'gender': 'FEMALE', 
             'timestamp': '2025-04-25T08:11:11.663906', 
             'favorite_sport': 'basketball'
             }
        ]
            
        mock_generate_id.side_effect = [917918, 702249]
        
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session
        
        user_data_upper_1 = {
            'id': 917918,
            'birth_year': 1995,
            'currency': 'USD',
            'country': 'USA',
            'gender': 'OTHER',
            'timestamp': '2025-04-25T08:11:11.663775',
            'favorite_sport': 'FOOTBALL'
        }
        user_data_upper_2 = {
            'id': 702249,
            'birth_year': 1961,
            'currency': 'EUR',
            'country': 'AUSTRALIA',
            'gender': 'FEMALE',
            'timestamp': '2025-04-25T08:11:11.663906',
            'favorite_sport': 'BASKETBALL'
        }
        
        mock_uppercase_dict.side_effect = [user_data_upper_1, user_data_upper_2]

        mock_schema = MagicMock()
        mock_schema.load.side_effect = [user_data_upper_1, user_data_upper_2]
        MockUserResponseSchema.return_value = mock_schema
        
        mock_user1 = MagicMock(id=917918)
        mock_user2 = MagicMock(id=702249)
        MockUser.side_effect = [mock_user1, mock_user2]
        
        mock_session.query().filter().first.return_value = None
        
        users = create_users(user_data_list, casino_id=casino_id)  
        
        self.assertEqual(users, [mock_user1, mock_user2])
        self.assertEqual(mock_schema.load.call_count, 2)
        self.assertEqual(mock_session.add.call_count, 2)
        self.assertEqual(mock_session.flush.call_count, 2)
        self.assertTrue(mock_session.commit.called)

        self.assertEqual(mock_create_profile.call_count, 2)
        mock_create_profile.assert_any_call(917918, session=mock_session)
        mock_create_profile.assert_any_call(702249, session=mock_session)
    
    @patch('app.services.uppercase_dict')
    @patch('app.services.create_user_profile')
    @patch('app.services.generate_unique_id')
    @patch('app.services.get_casino_db_session')
    @patch('app.services.User')
    @patch('app.services.UserResponseSchema')
    def test_create_users_with_validation_error(self, MockUserResponseSchema, MockUser, mock_get_session, mock_generate_id,
                                                mock_create_profile, mock_uppercase_dict):
             
        user_data_list = [
            {'birth_year': 1995, 
             'currency': 'USD', 
             'country': 'USA', 
             'gender': 'OTHER',
             'timestamp': '2025-04-25T08:11:11.663775', 
             'favorite_sport': 'football'},
            {'bad_data': True}
        ]
        
        mock_generate_id.side_effect = [917918, 999999]

        mock_session = MagicMock()
        mock_get_session.return_value = mock_session
        
        mock_session.query.return_value.filter.return_value.first.return_value = None
        
        user_data_upper_1 = {
            'id': 917918,
            'birth_year': 1995,
            'currency': 'USD',
            'country': 'USA',
            'gender': 'OTHER',
            'timestamp': '2025-04-25T08:11:11.663775',
            'favorite_sport': 'FOOTBALL'
        }
        
        user_data_upper_2 = {'bad_data': True}
        
        mock_uppercase_dict.side_effect = [user_data_upper_1, user_data_upper_2]
        
        mock_schema = MagicMock()
        mock_schema.load.side_effect = [
            user_data_upper_1,
            ValidationError("Invalid user data")
        ]
        
        MockUserResponseSchema.return_value = mock_schema
        
        mock_user = MagicMock()
        mock_user.id = 917918
        MockUser.return_value = mock_user
        
        with patch('builtins.print') as mock_print:
            users = create_users(user_data_list,  casino_id=784672)
     
            printed_calls = [call.args[0] for call in mock_print.call_args_list]
            self.assertTrue(
                any("Validation error for user" in msg and "Invalid user data" in msg for msg in printed_calls),
                f"Expected error message not found in: {printed_calls}"
            )
                          
        self.assertEqual(users, [mock_user])
        self.assertEqual(mock_schema.load.call_count, 2)
        self.assertEqual(mock_session.add.call_count, 1)
        self.assertEqual(mock_session.flush.call_count, 1)
        self.assertTrue(mock_session.commit.called)
        
        mock_create_profile.assert_called_once_with(917918, session=mock_session)
        
class TestCreateCasinos(unittest.TestCase):

    @patch('app.services.create_db_per_casino')
    @patch('app.services.uppercase_dict')
    @patch('app.services.generate_unique_id')
    @patch('app.services.db')
    @patch('app.services.CasinoSchema')
    @patch('app.services.Casino')
    def test_create_casinos(self, MockCasino, MockCasinoSchema, mock_db, mock_generate_id, mock_uppercase_dict, 
                            mock_create_db):
        
        casino_data_list = [
        {
            'db_name': 'Casino8001201110466',
            'recommender_type': 'static',
            'recommendation_schema': {
                "user_id": {"type": "int", "source_field": "id"},
                "bet": {"type": "float", "source_field": "stake"},
                "time": {"type": "float", "source_field": "timestamp"},
                "events": {"type": "list", "source_field": "recommended_events"}
            },
            'timestamp': '2025-05-30T14:10:03.030059'
        },
        {
            'db_name': 'Casino8001209999999',
            'recommender_type': 'dynamic',
            'recommendation_schema': {
                "user_id": {"type": "int", "source_field": "player_id"},
                "bet": {"type": "float", "source_field": "bet_amount"},
                "events": {"type": "list", "source_field": "event_list"}
            },
            'timestamp': '2025-05-30T15:00:00.000000'
        }
    ]

        
        mock_session = MagicMock()
        mock_db.session = mock_session
        mock_session.begin.return_value.__enter__.return_value = None
        mock_session.begin.return_value.__exit__.return_value = None
        
        mock_generate_id.side_effect = [111, 222]
        casino_data_upper_1 = {
            'id': 111,
            'db_name': 'CASINO8001201110466',
            'recommender_type': 'STATIC',
            'recommendation_schema': {
                "user_id": {"type": "int", "source_field": "id"},
                "bet": {"type": "float", "source_field": "stake"},
                "time": {"type": "float", "source_field": "timestamp"},
                "events": {"type": "list", "source_field": "recommended_events"}
            },
            'timestamp': '2025-05-30T14:10:03.030059'
        }
        casino_data_upper_2 = {
            'id': 222,
            'db_name': 'CASINO8001209999999',
            'recommender_type': 'DYNAMIC',
            'recommendation_schema': {
                "user_id": {"type": "int", "source_field": "player_id"},
                "bet": {"type": "float", "source_field": "bet_amount"},
                "events": {"type": "list", "source_field": "event_list"}
            },
            'timestamp': '2025-05-30T15:00:00.000000'
        }
        
        mock_uppercase_dict.side_effect = [casino_data_upper_1, casino_data_upper_2]
        
        mock_schema = MagicMock()
        mock_schema.load.side_effect = [casino_data_upper_1, casino_data_upper_2]
        MockCasinoSchema.return_value = mock_schema
        
        mock_casino_1 = MagicMock(id=111)
        mock_casino_2 = MagicMock(id=222)
        MockCasino.side_effect = [mock_casino_1, mock_casino_2]
       
        casinos = create_casinos(casino_data_list)

        self.assertEqual(casinos, [mock_casino_1, mock_casino_2])
        self.assertEqual(mock_schema.load.call_count, 2)
        self.assertEqual(mock_session.add.call_count, 2)
        self.assertEqual(mock_session.flush.call_count, 2)
        self.assertEqual(mock_create_db.call_count, 2)
        mock_create_db.assert_any_call(111)
        mock_create_db.assert_any_call(222)
        self.assertTrue(mock_session.commit.called)

    @patch('app.services.create_db_per_casino')
    @patch('app.services.uppercase_dict')
    @patch('app.services.generate_unique_id')
    @patch('app.services.db')
    @patch('app.services.CasinoSchema')
    @patch('app.services.Casino')
    def test_create_casinos_with_validation_error(self, MockCasino, MockCasinoSchema, mock_db, mock_generate_id, 
                                                  mock_uppercase_dict, mock_create_db):
        casino_data_list = [
            {'db_name': 'Casino8001201110466', 'recommender_type': 'static', 'recommendation_schema': {'type': 'none'}, 'timestamp': '2025-05-30T12:00:00'},
            {'invalid_data': True}
        ]

        mock_session = MagicMock()
        mock_db.session = mock_session
        mock_session.begin.return_value.__enter__.return_value = None
        mock_session.begin.return_value.__exit__.return_value = None
        
        mock_generate_id.side_effect = [123, 456]

        casino_data_upper_1 = {'id': 123, 'db_name': 'CASINO8001201110466', 'recommender_type': 'STATIC', 'recommendation_schema': {'type': 'none'}, 'timestamp': '2025-05-30T12:00:00'}
        casino_data_upper_2 = {'invalid_data': True}
        mock_uppercase_dict.side_effect = [casino_data_upper_1, casino_data_upper_2]
    
        mock_schema = MagicMock()
        mock_schema.load.side_effect = [
            casino_data_upper_1,
            Exception("Invalid casino data")
        ]
        MockCasinoSchema.return_value = mock_schema
    
        mock_casino = MagicMock(id=123)
        MockCasino.return_value = mock_casino
    
        with patch('builtins.print') as mock_print:
            casinos = create_casinos(casino_data_list)
    
            mock_print.assert_any_call("Validation error: Invalid casino data")

        self.assertEqual(casinos, [mock_casino])
        self.assertEqual(mock_schema.load.call_count, 2)
        self.assertEqual(mock_session.add.call_count, 1)
        self.assertEqual(mock_session.flush.call_count, 1)
        self.assertEqual(mock_create_db.call_count, 1)
        mock_create_db.assert_called_once_with(123)
        self.assertTrue(mock_session.commit.called)

class TestCreateEvents(unittest.TestCase):

    @patch('app.services.uppercase_dict')
    @patch('app.services.generate_unique_id')
    @patch('app.services.get_casino_db_session')
    @patch('app.services.Event')
    @patch('app.services.EventSchema')
    @patch('app.services.Team')
    def test_create_events(self, MockTeam, MockEventSchema, MockEvent, mock_get_session, mock_generate_id,
                           mock_uppercase_dict):
        casino_id = 23341
        event_data_list = [
            {'home_team_id': 601225, 
             'away_team_id': 494044, 
             'sport': 'football',
             'begin_timestamp': '2025-03-28T08:11:11', 
             'end_timestamp': '2025-03-28T09:11:11',
             'country': 'USA', 
             'league': 'NBA', 
             'odd': 2.5}
        ]
        
        mock_generate_id.return_value = 12345
        
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session
        
        event_data_upper = {
          'id': 12345,
          'sport': 'FOOTBALL',
          'league': 'PREMIER LEAGUE',
          'home_team': 'ARSENAL',
          'away_team': 'CHELSEA',
          'country': 'ENGLAND',
          'timestamp': '2025-06-15T18:00:00',
          'odd': 2.5
        }
        mock_uppercase_dict.return_value = event_data_upper

        mock_schema = MagicMock()
        mock_schema.load.return_value = event_data_upper
        MockEventSchema.return_value = mock_schema
        
        mock_event = MagicMock()
        mock_event.home_team = 'ARSENAL'
        mock_event.away_team = 'CHELSEA'
        mock_event.teams = []
        MockEvent.return_value = mock_event

        mock_home_team = MagicMock()
        mock_away_team = MagicMock()
        
        mock_session.query.return_value.filter_by.side_effect = [
           MagicMock(first=MagicMock(return_value=mock_home_team)),
           MagicMock(first=MagicMock(return_value=mock_away_team))
       ]
        
        events = create_events(event_data_list, casino_id=casino_id)


        self.assertEqual(events, [mock_event])
        self.assertEqual(mock_generate_id.call_count, 1)
        self.assertEqual(mock_schema.load.call_count, 1)
        self.assertEqual(mock_session.add.call_count, 1)
        self.assertEqual(mock_event.teams, [mock_home_team, mock_away_team])
        self.assertTrue(mock_session.commit.called)
        self.assertTrue(mock_session.close.called)
        
        @patch('app.services.uppercase_dict')
        @patch('app.services.generate_unique_id')
        @patch('app.services.get_casino_db_session')
        @patch('app.services.Event')
        @patch('app.services.EventSchema')
        def test_create_events_validation_error(self, MockEventSchema, MockEvent, mock_get_session, 
                                                mock_generate_id, mock_uppercase_dict):
            event_data_list = [{'invalid': 'data'}]
    
            mock_generate_id.return_value = 54321
            mock_session = MagicMock()
            mock_get_session.return_value = mock_session
    
            mock_uppercase_dict.return_value = {'invalid': 'DATA'}
    
            mock_schema = MagicMock()
            mock_schema.load.side_effect = ValidationError("Invalid event data")
            MockEventSchema.return_value = mock_schema
    
            with patch('builtins.print') as mock_print:
                events = create_events(event_data_list, casino_id=222)
    
                mock_print.assert_called_once_with(
                    "Validation error for event {'invalid': 'data'}: Invalid event data"
                )
    
            self.assertEqual(events, [])
            self.assertTrue(mock_session.commit.called)
            self.assertTrue(mock_session.close.called)

class TestCreatePurchasedCoupons(unittest.TestCase):

    @patch("app.services.uppercase_dict")
    @patch("app.services.generate_unique_id")
    @patch("app.services.get_casino_db_session")
    @patch("app.services.PurchasedCouponSchema")
    @patch("app.services.PurchasedCoupon")
    @patch("app.services.UserProfile")
    def test_create_purchased_coupons(self, MockUserProfile, MockPurchasedCoupon, MockPurchasedCouponSchema,
                                      mock_get_session,mock_generate_id,mock_uppercase_dict,):
        
        coupon_data_list = [
            {
                'user_id': 917918,
                'stake': 37.81,
                'timestamp': '2025-04-25T12:49:15.399950',
                'recommended_events': [],
            },
            {
                'user_id': 836245,
                'stake': 20.46,
                'timestamp': '2025-04-25T12:49:15.399950',
                'recommended_events': [],
            }
        ]
        
        mock_generate_id.side_effect = [555111, 555222]
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session
        
        mock_profile_1 = MagicMock(purchases_at_last_update=5)
        mock_profile_2 = MagicMock(purchases_at_last_update=2)
        mock_session.query().filter_by().first.side_effect = [mock_profile_1, mock_profile_2]
        
        coupon_data_upper_1 = {
            "id": 555111,
            'user_id': 917918,
            'stake': 37.81,
            'timestamp': '2025-04-25T12:49:15.399950',
            'recommended_events': [],
        }
        coupon_data_upper_2 = {
            "id": 555222,
            'user_id': 836245,
            'stake': 20.46,
            'timestamp': '2025-04-25T12:49:15.399950',
            'recommended_events': [],
        }
        
        mock_uppercase_dict.side_effect = [coupon_data_upper_1, coupon_data_upper_2]

        mock_schema = MagicMock()
        mock_schema.load.side_effect = [coupon_data_upper_1, coupon_data_upper_2]
        MockPurchasedCouponSchema.return_value = mock_schema
    
        mock_coupon_1 = MagicMock(id=555111)
        mock_coupon_2 = MagicMock(id=555222)
        MockPurchasedCoupon.side_effect = [mock_coupon_1, mock_coupon_2]
    
        coupons = create_purchased_coupons(coupon_data_list, casino_id=123456)

        self.assertEqual(coupons, [mock_coupon_1, mock_coupon_2])
        self.assertEqual(mock_schema.load.call_count, 2)
        self.assertEqual(mock_session.add.call_count, 2)
        self.assertTrue(mock_session.commit.called)
        self.assertEqual(mock_profile_1.purchases_at_last_update, 6)
        self.assertEqual(mock_profile_2.purchases_at_last_update, 3)
        mock_session.close.assert_called_once()
        mock_generate_id.assert_any_call(mock_session, MockPurchasedCoupon)

    @patch("app.services.uppercase_dict")
    @patch("app.services.generate_unique_id")
    @patch("app.services.get_casino_db_session")
    @patch("app.services.PurchasedCouponSchema")
    @patch("app.services.PurchasedCoupon")
    @patch("app.services.UserProfile")
    def test_create_purchased_coupons_exception_handling(self, MockUserProfile, MockPurchasedCoupon, MockPurchasedCouponSchema,
                                                         mock_get_session,mock_generate_id,mock_uppercase_dict,):
        coupon_data_list = [
            {
                'user_id': 789,
                'stake': 20.0,
                'timestamp': '2025-12-31T23:59:59',
                'recommended_events': []
            }
        ]

        mock_session = MagicMock()
        mock_get_session.return_value = mock_session
        
        mock_session.query.return_value.filter_by.return_value.first.return_value = None
        
        mock_query = MagicMock()
        mock_query.filter_by.return_value.first.return_value = None
        mock_session.query.return_value = mock_query

        mock_schema = MagicMock()
        mock_schema.load.side_effect = Exception("Validation error")
        MockPurchasedCouponSchema.return_value = mock_schema

        with patch("builtins.print") as mock_print:
            create_purchased_coupons(coupon_data_list, casino_id=12345)
    
            printed_calls = [call.args[0] for call in mock_print.call_args_list]
            self.assertTrue(
                any("User profile not found for user_id 789" in msg for msg in printed_calls),
                f"Expected error message not found in: {printed_calls}"
            )

        mock_session.commit.assert_not_called()
        mock_session.rollback.assert_not_called()
        mock_session.close.assert_called_once()

class TestRegisterRecommendation(unittest.TestCase):

    def setUp(self):
       recommender_registry.clear()
    
    def test_register_recommendation_adds_function_to_registry(self):
       @register_recommendation("testrecommender")
       def dummy_recommender():
           return "recommended"
       
       self.assertIn("testrecommender", recommender_registry)
       self.assertEqual(recommender_registry["testrecommender"], dummy_recommender)
       
    
    def test_decorator_returns_original_function(self):
        @register_recommendation("Another")
        def sample_func():
            return 42

        self.assertEqual(sample_func(), 42)

class TestGetAllSportLeagueTuples(unittest.TestCase):
    @patch("app.services.get_casino_db_session")
    def test_get_all_sport_league_tuples_returns_expected_list(self, mock_get_session):
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_query.distinct.return_value.all.return_value = [
            ('football', 'premier league'),
            ('basketball', 'nba')
        ]
        mock_session.query.return_value = mock_query
        mock_get_session.return_value = mock_session

        result = get_all_sport_league_tuples(casino_id=123)

        self.assertEqual(result, [
            ('football', 'premier league'),
            ('basketball', 'nba')
        ])
        mock_session.close.assert_called_once()
 
class TestDynamicRecommendation(unittest.TestCase):
    
    @patch("app.services.get_casino_db_session")
    @patch("app.services.random.uniform", return_value=25.5)
    @patch("app.services.datetime")
    def test_dynamic_recommendation_success(self, mock_datetime, mock_uniform, mock_get_session):
        fixed_time = datetime(2025, 1, 1, 12, 0, 0)
        
        mock_datetime.utcnow.return_value = fixed_time
                
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session
        
        mock_user = MagicMock()
        mock_user.favorite_sport = "FOOTBALL"
        mock_session.query().get.return_value = mock_user
        
        
        mock_event1 = MagicMock(country="FRANCE", 
                                league="LA LIGA", 
                                home_team="TEAM49384", 
                                away_team="TEAM07890", 
                                sport="FOOTBALL", 
                                odd=2.0)
        mock_event2 = MagicMock(country="GERMANY", 
                                league="BUNDESLIGA", 
                                home_team="Team394809", 
                                away_team="Team987656", 
                                sport="FOOTBALL", 
                                odd=2.5)
        mock_session.query().filter_by().limit().all.return_value = [mock_event1, mock_event2]
        
        result = dynamic_recommendation(user_id = 123, casino_id = 123, event_limit=2)
        
        self.assertEqual(result["user_id"], 123)
        self.assertEqual(result["stake"], 25.5)
        self.assertEqual(result["timestamp"], fixed_time.isoformat())
        self.assertEqual(len(result["recommended_events"]), 2)
        self.assertEqual(result["recommended_events"][0], {
            "country": "FRANCE",
            "league": "LA LIGA",
            "home_team": "TEAM49384",
            "away_team": "TEAM07890",
            "sport": "FOOTBALL",
            "odd": 2.0
        })

        self.assertEqual(result["recommended_events"][1], {
            "country": "GERMANY",
            "league": "BUNDESLIGA",
            "home_team": "Team394809",
            "away_team": "Team987656",
            "sport": "FOOTBALL",
            "odd": 2.5
        })
        mock_session.close.assert_called_once()
        
    @patch("app.services.get_casino_db_session")
    def test_dynamic_recommendation_user_not_found(self, mock_get_session):
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session
        mock_session.query().get.return_value = None

        with self.assertRaises(ValueError) as context:
            dynamic_recommendation(user_id=123, casino_id=234)

        self.assertIn("User 123 not found", str(context.exception))
        mock_session.close.assert_called_once()
        
class TestInferenceScoreRecommendation(unittest.TestCase):

    @patch("app.services.random.uniform", return_value=25.5)
    @patch("app.services.datetime")
    @patch("app.services.get_casino_db_session")
    def test_inference_score_recommendation_success(self, mock_get_session, mock_datetime, mock_random_uniform):
        fixed_time = datetime(2025, 1, 1, 12, 0, 0)
        mock_datetime.utcnow.return_value = fixed_time

        mock_session = MagicMock()
        mock_get_session.return_value = mock_session

        mock_user = MagicMock()
        mock_user.id = 123
        mock_user.country = "FRANCE"
        mock_user.favorite_sport = "FOOTBALL"

        mock_coupon = MagicMock()
        mock_coupon.recommended_events = [
            {
                "country": "FRANCE",
                "league": "LA LIGA",
                "home_team": "TEAM49384",
                "away_team": "TEAM07890",
                "sport": "FOOTBALL",
                "odd": 2.0
            },
            {
                "country": "GERMANY",
                "league": "BUNDESLIGA",
                "home_team": "Team394809",
                "away_team": "Team987656",
                "sport": "FOOTBALL",
                "odd": 2.5
            }
        ]

        mock_event = MagicMock()
        mock_event.id = 1
        mock_event.country = "FRANCE"
        mock_event.begin_timestamp = "2025-01-10T12:00:00"
        mock_event.end_timestamp = "2025-01-10T14:00:00"
        mock_event.league = "LA LIGA"
        mock_event.sport = "FOOTBALL"
        mock_event.odd = 2.0
        mock_event.home_team = "TEAM49384"
        mock_event.away_team = "TEAM07890"

        def query_side_effect(model):
            if model.__name__ == "User":
                mock_query = MagicMock()
                mock_query.filter_by.return_value.first.return_value = mock_user
                return mock_query
            elif model.__name__ == "PurchasedCoupon":
                mock_query = MagicMock()
                mock_query.filter_by.return_value.options.return_value.all.return_value = [mock_coupon]
                return mock_query
            elif model.__name__ == "Event":
                mock_query = MagicMock()
                mock_query.all.return_value = [mock_event]
                return mock_query
            return MagicMock()

        mock_session.query.side_effect = query_side_effect

        result = inference_score_recommendation(user_id=123, casino_id=456, event_limit=1)

        self.assertEqual(result["user_id"], 123)
        self.assertEqual(result["stake"], 25.5)
        self.assertEqual(result["timestamp"], fixed_time.isoformat())
        self.assertEqual(len(result["recommended_events"]), 1)
        self.assertEqual(result["recommended_events"][0], {
            "country": "FRANCE",
            "league": "LA LIGA",
            "home_team": "TEAM49384",
            "away_team": "TEAM07890",
            "sport": "FOOTBALL",
            "odd": 2.0
        })

        mock_session.close.assert_called_once()  

class TestRecommendationGenerator(unittest.TestCase):

    @patch("app.services.recommender_registry", new_callable=dict)
    def test_recommendation_generator_valid_config(self, mock_registry):

        mock_func = MagicMock(return_value={"sport": "FOOTBALL"})
        mock_registry["mock_recommender"] = mock_func
     
        config = {
            "recommender_type": "mock_recommender",
            "recommendation_schema": {
                "sport": "FOOTBALL"
                }
            }
     
        recommendation = recommendation_generator(config=config, casino_id=1, user_id=42)
     
        self.assertIn("sport", recommendation)
        self.assertEqual(recommendation["sport"], "FOOTBALL")
        mock_func.assert_called_once_with(user_id=42, casino_id=1)
        
class TestPopulateDB(unittest.TestCase):

    @patch("app.services.create_events")
    @patch("app.services.create_teams")
    @patch("app.services.create_users")
    @patch("app.services.create_db_per_casino")
    @patch("app.services.create_casinos")
    @patch("app.services.generate_dummy_casinos")
    @patch("app.services.generate_dummy_events")
    @patch("app.services.generate_dummy_teams")
    @patch("app.services.generate_dummy_users")
    def test_populate_db_success(self, mock_gen_users, mock_gen_teams, mock_gen_events,mock_gen_casinos, 
                                 mock_create_casinos, mock_create_db, mock_create_users, mock_create_teams, 
                                 mock_create_events):
        

        dummy_users = []
        for i in range(3):
            mock_user = MagicMock()
            dummy_users.append(mock_user)
        
        dummy_teams = []
        for i in range(3):
            mock_team = MagicMock()
            dummy_teams.append(mock_team)
        
        dummy_events = []
        for i in range(5):
            mock_event = MagicMock()
            dummy_events.append(mock_event)
        
        dummy_casinos = []
        for i in range(2):
            mock_casino = MagicMock()
            dummy_casinos.append(mock_casino)
        dummy_casinos[0].id = 1
        dummy_casinos[1].id = 2

        mock_gen_users.return_value = dummy_users
        mock_gen_teams.return_value = dummy_teams
        mock_gen_events.return_value = dummy_events
        mock_gen_casinos.return_value = dummy_casinos
        mock_create_casinos.return_value = dummy_casinos

        mock_create_users.side_effect = lambda users, casino_id: users
        mock_create_teams.side_effect = lambda teams, casino_id: teams
        mock_create_events.side_effect = lambda events, casino_id: events

        populate_db()

        self.assertEqual(mock_create_users.call_count, 2)
        self.assertEqual(mock_create_teams.call_count, 2)
        self.assertEqual(mock_create_events.call_count, 2)
        self.assertEqual(mock_create_db.call_count, 2)
         
if __name__ == '__main__':
    unittest.main()
             