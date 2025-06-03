import time
import sys
import json
import os
from confluent_kafka import Producer
from app.utils import generate_dummy_events, generate_dummy_teams, generate_dummy_users, generate_dummy_purchased_coupons_with_dummy_events, \
get_random_casino_id, get_random_user_id
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
                casino_id = get_random_casino_id()
                if not casino_id:
                    print("No casino_id found in the database. Waiting before retrying...")
                    time.sleep(5)
                    continue
                user_id = get_random_user_id(casino_id)
                if not user_id:
                    print("No user_id found in the database. Waiting before retrying...")
                    time.sleep(5)
                    continue
                teams = generate_dummy_teams(n=10)
                if topic == "events":
                    data = generate_dummy_events(teams=teams,n=1)
                elif topic == "users":
                    data = generate_dummy_users(n=1)
                elif topic == "coupons":
                    data = generate_dummy_purchased_coupons_with_dummy_events(teams=teams, user_id=user_id, n=1)
                else:
                    print(f"Unknown topic: {topic}. Exiting.")
                    break
    
                if not data:
                    print(f"No data generated for topic {topic}. Skipping.")
                    continue
    
                for record in data:
                    value = json.dumps(record).encode('utf-8')
                    producer.produce(
                        topic=topic,
                        value=value,
                        headers=[("casino_id", str(casino_id).encode("utf-8"))],
                        callback=delivery_report
                    )
                    producer.poll(0)
    
                time.sleep(20) 
                
            except Exception as e:
                print(f"Error producing message: {e}", file=sys.stderr)
            
if __name__ == "__main__":
    print(f"Starting producer for topic: {topic}")
    
    produce_messages(topic)
