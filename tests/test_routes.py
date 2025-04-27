import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
from app.routes import main, CONFIGS
from marshmallow import ValidationError
from app import create_app

class TestRoutes(unittest.TestCase):
    def setUp(self):
        self.client = create_app().test_client()
        self.headers = {
            "Content-Type": "application/json",
            "Casino-ID": "566550"
        }
        
    @patch('app.routes.db.session')
    @patch('app.routes.Casino')
    def test_config_success(self, mock_casino, mock_session):
        mock_casino_instance = MagicMock()
        mock_casino.query.get.return_value = mock_casino_instance

        payload = {
            "recommender_type": "Static",
            "recommendation_schema": {
                "id": {"type": "uuid", "source_field": "user_id"},
                "bet": {"type": "float", "source_field": "stake"},
                "time": {"type": "string", "source_field": "timestamp"},
                "events": {"type": "list", "source_field": "recommended_events"}
            },
            "timestamp": "2025-04-04T12:00:00"
        }

        response = self.client.post("/config", json = payload, headers = self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Configuration successfully saved!", response.get_json()["message"])
        
        mock_casino_instance.recommender_type = "Static"
        mock_casino_instance.recommendation_schema = payload["recommendation_schema"]
        mock_session.commit.assert_called_once()
    
    def test_config_missing_header(self):
       response = self.client.post("/config", json={})
       self.assertEqual(response.status_code, 400)
       self.assertIn("Casino-ID is required", response.get_json()["error"])
    
    @patch('app.routes.Casino')
    def test_config_missing_fields(self, mock_casino_class):
        
       mock_casino = MagicMock()
       mock_casino_class.query.get.return_value = mock_casino
       
       payload = {
           "recommender_type": "Static"
       }
              
       response = self.client.post("/config", json=payload, headers=self.headers)
       self.assertEqual(response.status_code, 400)
       self.assertIn("Both recommender_type and recommendation_schema are required", response.get_json()["error"])
       
           
    @patch('app.routes.Casino')
    @patch('app.routes.User')
    @patch('app.routes.recommendation_generator')
    def test_recommendation_success(self, mock_recommendation_generator, mock_user_class, mock_casino_class):
        user_id = 917918
        casino_id = 566550
        mock_casino = MagicMock()
        mock_casino.casino_id = casino_id
        mock_casino.recommender_type = "Static"
        mock_casino.recommendation_schema = {
            "id": {"type": "int", "source_field": "user_id"},
            "bet": {"type": "float", "source_field": "stake"},
            "time": {"type": "string", "source_field": "timestamp"},
            "events": {"type": "list", "source_field": "recommended_events"}
        }
        
        mock_user = MagicMock()
        mock_user.casinos = [mock_casino]
        
        mock_user_class.query.get.return_value = mock_user
        mock_casino_class.query.get.return_value = mock_casino
        
        CONFIGS[casino_id] = {
            "recommender_type": "Static",
            "recommendation_schema": mock_casino.recommendation_schema
        }

        
        recommendation_payload = {
            "id": 917918,
            "bet": 48.06,
            "time": "2025-04-25T14:55:17.463427",
            "events": [
                {"event_id": 717335, "odd": 2.81},
                {"event_id": 261453, "odd": 2.65},
                {"event_id": 16519, "odd": 2.54}
            ]
        }
        
        mock_recommendation_generator.return_value = recommendation_payload
        
        headers = {"Casino-ID": str(casino_id)}
        response = self.client.get(f"/recommend/{user_id}", headers=headers)

        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        self.assertIn("events", json_data)
        self.assertEqual(json_data["id"], user_id)
        self.assertEqual(json_data["bet"], 48.06)
        self.assertEqual(len(json_data["events"]), 3)

    @patch('app.routes.Casino')
    def test_recommend_missing_casino_header(self, mock_casino):
        response = self.client.get("/recommend/42496")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Casino-ID header is required", response.get_json()["error"])

    @patch('app.routes.Casino')
    @patch('app.routes.User')
    def test_recommend_casino_not_configured(self, mock_user_class, mock_casino_class):
        mock_casino = MagicMock()
        mock_casino.recommender_type = None
        mock_casino.recommendation_schema = None
        mock_casino_class.query.get.return_value = mock_casino
        
        mock_user = MagicMock()
        mock_user.casinos = [mock_casino]
        mock_user_class.query.get.return_value = mock_user

        headers = {"Casino-ID": "123"}
        response = self.client.get("/recommend/42496", headers=headers)
        
        self.assertEqual(response.status_code, 400)
        self.assertIn("Casino is not configured", response.get_json()["error"])

    @patch('app.routes.User')
    def test_recommend_user_not_found(self, mock_user):
        mock_user.query.get.return_value = None

        response = self.client.get("/recommend/42496", headers=self.headers)
        self.assertEqual(response.status_code, 404)
        self.assertIn("User not found", response.get_json()["error"])

    @patch('app.routes.User')
    @patch('app.routes.Casino')
    def test_recommend_user_not_in_casino(self, mock_casino, mock_user):
        mock_user_instance = MagicMock()
        mock_user_instance.casinos = []
        mock_user.query.get.return_value = mock_user_instance

        mock_casino_instance = MagicMock()
        mock_casino.query.get.return_value = mock_casino_instance

        response = self.client.get("/recommend/42496", headers=self.headers)
        self.assertEqual(response.status_code, 400)
        self.assertIn("User is not associated with this casino", response.get_json()["error"])
        
    '''
    @patch('app.routes.populate_db')
    
    def test_populate(self, mock_populate):
        mock_populate.return_value = None
        response = self.client.get('/populate')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"message": "Database populated with dummy data"})
        mock_populate.assert_called_once()
    '''