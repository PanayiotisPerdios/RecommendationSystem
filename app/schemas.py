from marshmallow import Schema, fields, validate
from datetime import datetime, timedelta
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.db_models import User, Participant, Event
from app.utils import validate_date_format


class ParticipantSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Participant
        
    participant_id = fields.UUID(required = True) 
    name = fields.String(required = True)
    sport = fields.String(required = True)
    
class EventSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Event
        
    begin_timestamp = fields.String(required = True, validate = validate_date_format)
    country =  fields.String(required = True, validate = validate.OneOf(["GREECE","USA"]))
    end_timestamp = fields.String(required = True, validate = validate_date_format) 
    event_id = fields.UUID(required = True) 
    league = fields.String(required = True)
    participants = fields.List(fields.Nested(ParticipantSchema),required=True)
    sport = fields.String(required = True, validate = validate.OneOf(["handball","football","basketball"]))
    odd = fields.Float(required = True)

class UserRequestSchema(Schema):
    user_id = fields.UUID(required = True)
    favorite_sport = fields.String(required = True, validate = validate.OneOf(["handball","football","basketball"]))

class UserResponseSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        
    birth_year = fields.Integer(required = True)
    currency = fields.String(required = True, validate = validate.OneOf(["EUR","USD","GBP"]))
    country = fields.String(required = True, validate = validate.OneOf(["GREECE","USA"]))
    gender = fields.String(required = True, validate = validate.OneOf(["MALE", "FEMALE", "OTHER"]))
    timestamp = fields.String(missing = None)
    user_id = fields.UUID(required = True) 
    favorite_sport = fields.String(required = True, validate = validate.OneOf(["handball","football","basketball"]))
    
class RecommendationSchema(Schema):
    user_id = fields.UUID(required = True) 
    stake = fields.Float(required = True)
    timestamp = fields.String(required = True)
    recommended_events = fields.List(fields.Nested(EventSchema), required = True)
    

