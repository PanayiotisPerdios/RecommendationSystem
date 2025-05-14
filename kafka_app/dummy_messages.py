import json
import argparse
from confluent_kafka import Producer
from datetime import datetime, timedelta
from app.utils import generate_dummy_events, generate_dummy_teams
import random

def generate_random_coupon():
    events = [generate_dummy_events() for _ in range(3)]
    recommended_events = [
        {"event_id": e["event_id"], "odd": e["odd"]}
        for e in events
    ]

    coupon = {
        "coupon_id": random.randint(100000, 999999),
        "user_id": random.randint(1000, 999999),
        "stake": round(random.uniform(10, 100), 2),
        "timestamp": datetime.utcnow().replace(microsecond=0).isoformat(),
        "recommended_events": recommended_events,
        "topic": "coupons"
    }
    return coupon

def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")
        
def send_data(data_type):
    producer = Producer({'bootstrap.servers': 'localhost:9092'})

    if data_type == "event":
        dummy_teams = generate_dummy_teams(n=10)
        data = generate_dummy_events(n=1,teams=dummy_teams)
    elif data_type == "coupon":
        data = generate_random_coupon()
    else:
        print("Invalid data type. Please choose 'event' or 'coupon'.")
        return

    value = json.dumps(data).encode('utf-8')
    producer.produce(data['topic'], value=value, callback=delivery_report)
    producer.flush()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--data-type', required=True, choices=['event', 'coupon'], help="Type of data to send")
    args = parser.parse_args()

    send_data(args.data_type)

    