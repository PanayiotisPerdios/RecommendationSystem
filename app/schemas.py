from marshmallow import Schema, fields, validate, post_load
from datetime import datetime, timedelta
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.db_models import User, Team, Event, Casino, PurchasedCoupon, UserProfile
from app.utils import validate_date_format
from app.config import Config
from sqlalchemy import Integer



class TeamSchema(SQLAlchemyAutoSchema):
    class Meta: 
        model = Team
        
    team_id = fields.Integer(required=True) 
    name = fields.String(required = True)
    sport = fields.String(required = True)
    
class EventSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Event
        
    begin_timestamp = fields.String(required = True, validate = validate_date_format)
    country =  fields.String(required = True)
    end_timestamp = fields.String(required = True, validate = validate_date_format) 
    event_id = fields.Integer(required=True)  
    league = fields.String(required = True)
    home_team_id = fields.Integer(required=True)  
    away_team_id = fields.Integer(required=True) 
    sport = fields.String(required = True, validate = validate.OneOf(["handball","football","basketball"]))
    odd = fields.Float(required = True)

class RecommendedEventSchema(Schema):
     event_id = fields.Integer(required=True) 
     odd = fields.Float(required = True)
     
    
class PurchasedCouponSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = PurchasedCoupon
        
    coupon_id = fields.Integer(required=True) 
    user_id = fields.Integer(required=True)  
    stake = fields.Float(required = True)
    timestamp = fields.String(required = True)
    recommended_events = fields.List(fields.Nested(RecommendedEventSchema), required=True)
    
class UserRequestSchema(Schema):
    user_id = fields.Integer(required = True)
    favorite_sport = fields.String(required = True, validate = validate.OneOf(["handball","football","basketball"]))

class UserResponseSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        
    birth_year = fields.Integer(required = True)
    currency = fields.String(required = True, validate = validate.OneOf(["EUR","USD","GBP"]))
    country = fields.String(required = True)
    gender = fields.String(required = True, validate = validate.OneOf(["MALE", "FEMALE", "OTHER"]))
    timestamp = fields.String(missing = None)
    user_id = fields.Integer(required = True) 
    favorite_sport = fields.String(validate = validate.OneOf(["handball","football","basketball"]))
    favorite_league = fields.String()
    
class UserProfileSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = UserProfile
        
    profile_id = fields.Int(required=True)
    user_id = fields.Int(required=True)
    favorite_sport_league_json = fields.List(fields.List(fields.String()), allow_none=True)
    purchases_at_last_update = fields.Int(required=True)
    last_updated = fields.Str(required=True)

    
    
class CasinoSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Casino
        
    casino_id = fields.Integer(required = True)
    name = fields.String(required = True)
    recommender_type = fields.String()
    recommendation_schema = fields.Dict() 
    timestamp = fields.String(required=True)
    
class RecommendationSchema(Schema):
    user_id = fields.Integer(required = True) 
    stake = fields.Float(required = True)
    timestamp = fields.String(required = True)
    recommended_events = fields.List(fields.Nested(RecommendedEventSchema), required=True)
    
class ConfigSchema(Schema):
    recommender_type = fields.String(required = True)
    recommendation_schema = fields.Dict(required=True) 
    timestamp = fields.String(required = True)
    
    def validate_user_schema(self, data, **kwargs):
        client_recommendation_schema = data["recommendation_schema"]
        
        schema_fields = Config.DEFAULT_FIELDS.copy()
        for key, field_type in client_recommendation_schema .items():
           if field_type == "uuid":
               schema_fields[key] = fields.UUID()
           elif field_type == "float":
               schema_fields[key] = fields.Float()
           elif field_type == "string":
               schema_fields[key] = fields.String()
           elif field_type == "list":
               schema_fields[key] = fields.List(fields.Raw())
           elif field_type == "int":
                 schema_fields[key] = fields.Int
           elif field_type is None:
               schema_fields.pop(key, None)
           else:
               raise ValueError(f"Unsupported field type: {field_type}")

        TransformedRecommendationSchema = type("TransformedRecommendationSchema", (Schema,), schema_fields)
       
       
        return TransformedRecommendationSchema()
  
