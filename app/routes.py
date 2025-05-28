from flask import Blueprint, request, jsonify
from app.schemas import UserRequestSchema, RecommendationSchema, ConfigSchema
from app.services import recommendation_generator, recommender_registry
from marshmallow import ValidationError
from app.db_models_shared import User
from app.db_models_master import Casino
from app import db 
from app.services import create_purchased_coupons, populate_db
from app.utils import generate_dummy_purchased_coupons, get_casino_db_session, generate_dummy_events, \
generate_dummy_teams


main = Blueprint("main", __name__)

CONFIGS = {}

user_request_schema = UserRequestSchema()
recommendation_schema = RecommendationSchema()
config_schema = ConfigSchema()

@main.route("/recommend/<int:user_id>", methods=["GET"])
def recommend(user_id):
    try:
                
        casino_id = request.headers.get("Casino-ID")
        
        if not casino_id:
           return jsonify({"error": "Casino-ID header is required"}), 400
        try:
            casino_id = int(casino_id)
        except ValueError:
            return jsonify({"error": "Casino-ID must be an integer"})
       
        if casino_id not in CONFIGS:
            casino = Casino.query.get(casino_id)
            if not casino:
                return jsonify({"error": "Casino not found"}), 404
            if not casino.recommender_type or not casino.recommendation_schema:
                return jsonify({"error": "Casino is not configured. Please set up the casino first."}), 400

            CONFIGS[casino_id] = {
                "recommender_type": casino.recommender_type,
                "recommendation_schema": casino.recommendation_schema
            }
            
        session = get_casino_db_session(casino_id)
        user = session.query(User).get(user_id)
        if not user:
           return jsonify({"error": "User not found"}), 404
        
        casino = db.session.query(Casino).get(casino_id)
        '''
        if casino not in user.casinos:
           return jsonify({"error": "User is not associated with this casino"}), 400
        '''
            
        config = CONFIGS[casino_id]
        
        recommendation = recommendation_generator(config, casino_id, user_id)
    

        '''   
        recommendation_schema.load(recommendation)
        
        return jsonify(recommendation_schema.dump(recommendation)), 200
        '''
        
        return jsonify(recommendation), 200

        
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400
    
@main.route("/config", methods=['POST'])
def config():
    casino_id = request.headers.get("Casino-ID")
    
    if not casino_id:
        return jsonify({"error": "Casino-ID is required"}), 400
    
    try:
        casino_id = int(casino_id)
    except ValueError:
        return jsonify({"error": "Casino-ID must be an integer"})
    
    casino = db.session.query(Casino).get(casino_id)
    if not casino:
        return jsonify({"error": "Casino not found"}), 404
    
    try:
        
        recommender_type = request.json.get('recommender_type')
        recommendation_schema = request.json.get("recommendation_schema")
        
        if recommender_type not in recommender_registry:
            return jsonify({"error": f"The {recommender_type} recomender_type isn't supported"}), 400
        if not recommender_type or not recommendation_schema:
            return jsonify({"error": "Both recommender_type and recommendation_schema are required"}), 400
        
        try:
            data = config_schema.load(request.json)
        except ValidationError as err:
            return jsonify({"error": err.messages}), 400
        
        CONFIGS[casino_id] = {
            "recommender_type": recommender_type,
            "recommendation_schema": recommendation_schema
        }
        
        casino.recommender_type = recommender_type
        casino.recommendation_schema = recommendation_schema
        db.session.commit()

        
        return jsonify({
            "message": "Configuration successfully saved!",
            "config": data,
            "recommender_type": recommender_type,
            "recommendation_schema": recommendation_schema
        }), 200
        
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400

@main.route('/populate', methods=['GET'])
def populate():
    populate_db()
    return jsonify({"message": "Database populated with dummy data" }), 200

'''
@main.route('/print_rec/<int:user_id>', methods=['GET'])
def print_rec(user_id):
    recommendations = get_frequent_sport_league_tuples(user_id, n=4)
    return jsonify(recommendations)
'''

@main.route('/purchase/<int:user_id>', methods=['GET'])
def create_coupons(user_id):
    try:
        casino_id = request.headers.get("Casino-ID")
        if not casino_id:
           return jsonify({"error": "Casino-ID header is required"}), 400
        try:
           casino_id = int(casino_id)
        except ValueError:
           return jsonify({"error": "Casino-ID must be an integer"}), 400
       
        session = get_casino_db_session(casino_id)
        teams = generate_dummy_teams(n=10)
        events = generate_dummy_events(teams=teams, n=4)
        coupon_data_list, user_id = generate_dummy_purchased_coupons(events=events, user_id=user_id, n=3)
        created_coupons = create_purchased_coupons(coupon_data_list, casino_id=casino_id, session=session, commit=True)
        
        coupon_ids = []
        for coupon in created_coupons:
            coupon_ids.append(coupon.id)
            
        session.close() 
        
        return jsonify({"message": "Coupons created successfully", "coupon_ids": coupon_ids}), 201

       
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    

