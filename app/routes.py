from flask import Blueprint, request, jsonify
from app.schemas import UserRequestSchema, RecommendationSchema
from app.services import generate_dummy_recommendation, populate_db
from marshmallow import ValidationError

main = Blueprint("main", __name__)

user_request_schema = UserRequestSchema()
recommendation_schema = RecommendationSchema()

@main.route("/recommend", methods=["POST"])
def recommend():
    try:
        data = user_request_schema.load(request.json)
        user_id = data["user_id"]
        favorite_sport = data["favorite_sport"]

        recommendation = generate_dummy_recommendation(user_id, favorite_sport)
           
        recommendation_schema.load(recommendation)
        
        return jsonify(recommendation_schema.dump(recommendation)), 200
        
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400

@main.route('/populate', methods=['GET'])
def populate():
    populate_db()
    return jsonify({"message": "Database populated with dummy data" }), 200
