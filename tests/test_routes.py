import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
from app.routes import main, CONFIGS
from marshmallow import ValidationError
from app import create_app

class TestRoutes(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = create_app().test_client()
        self.headers = {
            "Content-Type": "application/json",
            "Casino-ID": "566550"
        }
        
    @patch('app.routes.db.session')
    def test_config_success(self, mock_db_session):
        mock_casino_instance = MagicMock()
        mock_db_session.get.return_value = mock_casino_instance

        payload = {
            "recommender_type": "static",
            "recommendation_schema": {
                "user_id": {"type": "int", "source_field": "id"},
                "bet": {"type": "float", "source_field": "stake"},
                "time": {"type": "string", "source_field": "timestamp"},
                "events": {"type": "list", "source_field": "recommended_events"}
            }
        }
        
        response = self.client.post("/config", json=payload, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Configuration successfully saved!", response.get_json()["message"])        
        mock_db_session.commit.assert_called_once()
    
    def test_config_casino_header_not_being_int(self):
        response = self.client.post(
                "/config",
                headers={"Casino-ID": "abc"}
        )        
        self.assertEqual(response.status_code, 400)
        self.assertIn("Casino-ID header must be an integer", response.get_json()["error"])
        
    def test_config_missing_header(self):
       response = self.client.post("/config", json={})
       self.assertEqual(response.status_code, 400)
       self.assertIn("Casino-ID header is required", response.get_json()["error"])
    
    @patch("app.routes.db.session")
    def test_config_missing_fields(self, mock_db_session):
        
       mock_db_session.get.return_value = MagicMock()
       
       payload = {
           "recommender_type": "static"
       }
              
       response = self.client.post("/config", json=payload, headers=self.headers)
       self.assertEqual(response.status_code, 400)
       self.assertIn("Both recommender_type and recommendation_schema are required", response.get_json()["error"])
       
           
    @patch('app.routes.db.session')
    @patch('app.routes.Casino')
    @patch('app.routes.User')
    @patch('app.routes.recommendation_generator')
    @patch('app.routes.get_casino_db_session')
    def test_recommendation_success(self, mock_get_session, mock_recommendation_generator, mock_user_class,
                                    mock_casino_class,mock_db_session):
        user_id = 917918
        casino_id = 566550
        
        mock_casino_instance = MagicMock()
        mock_casino_instance.recommender_type = "Static"
        mock_casino_instance.recommendation_schema = {
            "user_id": {"type": "int", "source_field": "id"},
            "bet": {"type": "float", "source_field": "stake"},
            "time": {"type": "string", "source_field": "timestamp"},
            "events": {"type": "list", "source_field": "recommended_events"}
        }
        
        mock_casino_class.query.get.return_value = mock_casino_instance

        mock_user_instance = MagicMock()
        mock_user_instance.casinos = [mock_casino_instance]
        mock_user_class.query.get.return_value = mock_user_instance
        
        mock_session = MagicMock()
        mock_session.query().get.return_value = mock_user_instance
        mock_get_session.return_value = mock_session
        
        CONFIGS[casino_id] = {
            "recommender_type": "static",
            "recommendation_schema": mock_casino_instance.recommendation_schema
        }

        
        recommendation_payload = {
            "bet": 48.06,
            "events": [
                {
                    "away_team": "TEAM1026664419810",
                    "country": "JAPAN",
                    "home_team": "TEAM1513708908357",
                    "league": "LIGA ACB",
                    "odd": 2.36,
                    "sport": "BASKETBALL"
                },
                {
                    "away_team": "TEAM1159047041804",
                    "country": "KENYA",
                    "home_team": "TEAM3751515438980",
                    "league": "NCAA BASKETBALL",
                    "odd": 3.04,
                    "sport": "BASKETBALL"
                },
                {
                    "away_team": "TEAM3751515438980",
                    "country": "USA",
                    "home_team": "TEAM1159047041804",
                    "league": "NCAA BASKETBALL",
                    "odd": 2.99,
                    "sport": "BASKETBALL"
                }
            ],
            "time": "2025-04-25T14:55:17.463427",
            "user_id": user_id
        }
        
        mock_recommendation_generator.return_value = recommendation_payload
        
        headers = {"Casino-ID": str(casino_id)}
        response = self.client.get(f"/recommend/{user_id}", headers=headers)

        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertIn("events", json_data)
        self.assertEqual(json_data["user_id"], user_id)
        self.assertEqual(json_data["bet"], 48.06)
        self.assertEqual(len(json_data["events"]), 3)
        
    def test_recommend_casino_header_not_being_int(self):
        response = self.client.get(
                "/recommend/42496",
                headers={"Casino-ID": "abc"}
        )        
        self.assertEqual(response.status_code, 400)
        self.assertIn("Casino-ID header must be an integer", response.get_json()["error"])
        
    def test_recommend_missing_casino_header(self):
        response = self.client.get("/recommend/42496")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Casino-ID header is required", response.get_json()["error"])

    @patch('app.routes.Casino')
    @patch('app.routes.User')
    def test_recommend_casino_not_configured(self, mock_user_class, mock_casino_class):
        mock_casino_instance = MagicMock()
        mock_casino_instance.recommender_type = None
        mock_casino_instance.recommendation_schema = None
        mock_casino_class.query.get.return_value = mock_casino_instance

        
        mock_user_instance = MagicMock()
        mock_user_instance.casinos = [mock_casino_instance]
        mock_user_class.query.get.return_value = mock_user_instance

        headers = {"Casino-ID": "123"}
        response = self.client.get("/recommend/42496", headers=headers)
        
        self.assertEqual(response.status_code, 400)
        self.assertIn("Casino is not configured", response.get_json()["error"])

    @patch('app.routes.get_casino_db_session')
    @patch('app.routes.db')
    def test_recommend_user_not_found(self, mock_db, mock_get_session):
        mock_session = MagicMock()
        mock_session.get.side_effect = lambda model, id: None if model.__name__ == 'User' else MagicMock()
        mock_get_session.return_value = mock_session
    
        mock_db.session.get.return_value = MagicMock(
            recommender_type="static", recommendation_schema={"some": "schema"}
        )
    
        response = self.client.get("/recommend/42496", headers=self.headers)
        self.assertEqual(response.status_code, 404)
        self.assertIn("User not found", response.get_json()["error"])

class TestCreateCouponsRoute(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.register_blueprint(main)
        self.client = self.app.test_client()

    @patch("app.routes.create_purchased_coupons")
    @patch("app.routes.generate_dummy_purchased_coupons")
    @patch("app.routes.generate_dummy_events")
    @patch("app.routes.generate_dummy_teams")
    @patch("app.routes.get_casino_db_session")
    def test_create_coupons_success(
        self, mock_get_session, mock_generate_teams,
        mock_generate_events, mock_generate_coupons, mock_create_coupons
    ):
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session

        mock_team = MagicMock()
        mock_generate_teams.return_value = [mock_team]

        mock_event = MagicMock()
        mock_generate_events.return_value = [mock_event]

        dummy_coupon_data = [{'some': 'data'}], 123
        mock_generate_coupons.return_value = dummy_coupon_data

        coupon1 = MagicMock(id=1)
        coupon2 = MagicMock(id=2)
        mock_create_coupons.return_value = [coupon1, coupon2]

        response = self.client.get(
            "/purchase/123",
            headers={"Casino-ID": "456"}
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json, {
            "message": "Coupons created successfully",
            "coupon_ids": [1, 2]
        })
        mock_session.close.assert_called_once()

    def test_create_coupons_missing_casino_id_header(self):
        response = self.client.get("/purchase/123")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"error": "Casino-ID header is required"})

    def test_create_coupons_invalid_casino_id_header(self):
        response = self.client.get("/purchase/123", headers={"Casino-ID": "abc"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"error": "Casino-ID must be an integer"})
        