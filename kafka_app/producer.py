import time
import sys
import json
import os
from confluent_kafka import Producer
from app.utils import generate_dummy_events, generate_dummy_teams, generate_dummy_users, generate_dummy_purchased_coupons_random_user
from app import create_app

topic = os.getenv("TOPIC_NAME", "events")
bootstrap_servers = os.getenv("BOOTSTRAP_SERVERS", "localhost:9092")

producer = Producer({'bootstrap.servers': bootstrap_servers})

app = create_app()

def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}", file=sys.stderr)
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

def produce_messages(send_data):
    
    with app.app_context():
        while True:
            try:
                if topic == "events":
                    data = generate_dummy_events(n=1)
                elif topic == "users":
                    data = generate_dummy_users(n=1)
                elif topic == "coupons":
                    data = generate_dummy_purchased_coupons_random_user(event_limit=10,n=1)
                else:
                    print(f"Unknown topic: {topic}. Exiting.")
                    break
    
                if not data:
                    print(f"No data generated for topic {topic}. Skipping.")
                    continue
    
                for record in data:
                    value = json.dumps(record).encode('utf-8')
                    producer.produce(topic=topic, value=value, callback=delivery_report)
                    producer.poll(0)
    
                time.sleep(5) 
                
            except Exception as e:
                print(f"Error producing message: {e}", file=sys.stderr)
            
if __name__ == "__main__":
    print(f"Starting producer for topic: {topic}")
    
    produce_messages(topic)
