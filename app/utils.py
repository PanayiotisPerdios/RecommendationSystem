import random
from datetime import datetime, timedelta
from marshmallow import ValidationError

def random_begin_timestamp():
    return (datetime.utcnow() - timedelta(days=random.randint(10, 30))).replace(microsecond=0).isoformat()

def random_end_timestamp(begin_time):
    begin_dt = datetime.fromisoformat(begin_time)
    return (begin_dt + timedelta(minutes=60)).replace(microsecond=0).isoformat()

def validate_date_format(value):
    try:
        datetime.fromisoformat(value)
    except ValueError:
        raise ValidationError("Invalid date format. Expected format: (YYYY-MM-DDTHH:MM:SS)")
        
        
        