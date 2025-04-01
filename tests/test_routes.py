import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
from app.routes import main
from marshmallow import ValidationError

class TestRoutes(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.register_blueprint(main)
        self.client = self.app.test_client()

    @patch('app.routes.generate_dummy_recommendation')
    @patch('app.routes.user_request_schema')
    def test_recommendation_success(self, mock_schema, mock_recommendation):
        mock_schema.load.return_value = {"user_id": "550e8400-e29b-41d4-a716-446655440000", "favorite_sport": "football"}
        
        mock_recommendation.return_value = {
                "recommended_events": [
                    {
                        "begin_timestamp": "2025-03-20T12:23:59",
                        "country": "USA",
                        "end_timestamp": "2025-03-20T13:23:59",
                        "event_id": "6a75df6b-51f1-49f8-bcd5-02dff75a60bb",
                        "league": "EHF Champions League",
                        "odd": 2.72,
                        "participants": [
                            {
                                "name": "Team5549789962",
                                "participant_id": "3e785f23-1fb9-4c10-92ed-8d0deabbd2f2",
                                "sport": "handball"
                            }
                        ],
                        "sport": "handball"
                    },
                    {
                        "begin_timestamp": "2025-03-22T12:23:59",
                        "country": "USA",
                        "end_timestamp": "2025-03-22T13:23:59",
                        "event_id": "f9942de6-aa6e-440d-8fe8-81f25e05eed3",
                        "league": "EHF Champions League",
                        "odd": 2.65,
                        "participants": [
                            {
                                "name": "Team3904668074",
                                "participant_id": "d66725be-d0bc-4c69-a5df-dcdab9771290",
                                "sport": "handball"
                            }
                        ],
                        "sport": "handball"
                    },
                    {
                        "begin_timestamp": "2025-03-14T12:23:59",
                        "country": "USA",
                        "end_timestamp": "2025-03-14T13:23:59",
                        "event_id": "7cbeb3c5-2fdd-48c8-8147-2cdb74b0f6a8",
                        "league": "EHF Champions League",
                        "odd": 2.86,
                        "participants": [
                            {
                                "name": "Team1172902903",
                                "participant_id": "293038d0-27f6-4937-8789-b6336672113e",
                                "sport": "handball"
                            },
                            {
                                "name": "Team3904668074",
                                "participant_id": "d66725be-d0bc-4c69-a5df-dcdab9771290",
                                "sport": "handball"
                            },
                            {
                                "name": "Team2372932913",
                                "participant_id": "699e4ab0-516c-4370-b8dc-9adb4c8f7fb5",
                                "sport": "handball"
                            }
                            ],
                        "sport": "handball"
                        }
                    ],
                "stake": 31.21,
                "timestamp": "2025-04-01T13:27:00.247938",
                "user_id": "552e8400-e29b-41d4-a716-446655440000"
             }

        response = self.client.post(
            '/recommend',
            json={"user_id": "550e8400-e29b-41d4-a716-446655440000"},
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        mock_schema.load.assert_called_once()
        mock_recommendation.assert_called_once_with("550e8400-e29b-41d4-a716-446655440000", "football")

    @patch('app.routes.user_request_schema')
    def test_recommendation_validation_error(self, mock_schema):
        mock_schema.load.side_effect = ValidationError({"user_id": ["Not a valid UUID"]})
        
        response = self.client.post(
            '/recommend',
            json={"user_id": "invalid-uuid"},
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json)

    @patch('app.routes.populate_db')
    def test_populate(self, mock_populate):
        mock_populate.return_value = None
        response = self.client.get('/populate')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"message": "Database populated with dummy data"})
        mock_populate.assert_called_once()