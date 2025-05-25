import sys
import json
import os
import threading
from confluent_kafka import Consumer, KafkaException
from app.services import create_events, create_purchased_coupons, create_users
from app import create_app
from collections import defaultdict

topic = os.getenv("TOPIC_NAME", "coupons") 

bootstrap_servers = os.getenv("BOOTSTRAP_SERVERS", "localhost:9092")
app = create_app()

def consume_topic(topic):
    with app.app_context():
        consumer = Consumer({'bootstrap.servers': bootstrap_servers,
                             'group.id': f'{topic}-group',
                             'auto.offset.reset': 'earliest',
                             'enable.auto.commit': False })
        
        consumer.subscribe([topic])
        
        try:
            while True:
                msgs = consumer.consume(num_messages=10, timeout=3.0)
                if not msgs:
                    continue
                
                batch_data = []
                casino_ids = []
                
                for msg in msgs:
                    
                    if msg.error():
                        print(f"Kafka message error: {msg.error()}", file=sys.stderr)
                        continue
                        
                    try:
                        data = json.loads(msg.value().decode("utf-8"))
                        headers = dict(msg.headers() or [])
                        casino_id = headers.get("casino_id")
                        
                        if isinstance(casino_id, bytes):
                            casino_id = casino_id.decode("utf-8")
                        
                        if not casino_id:
                            print("Missing casino_id header")
                            continue
                                            
                        print(f"Message consumed from topic {topic}: {data}")
                        
                        batch_data.append(data)
                        casino_ids.append(casino_id)
                        
                    except json.JSONDecodeError:
                        print("Failed to decode message. Skipping.")
                    
                    #groups batches of data based on casino_id like a hashmap
                grouped_data = defaultdict(list)
                for data, cid in zip(batch_data, casino_ids):
                    grouped_data[cid].append(data)
                        
                for cid, items in grouped_data.items():
                    if topic == "events":
                        create_events(items, cid)
                    elif topic == "coupons":
                        create_purchased_coupons(items, cid)
                    elif topic == "users":
                        create_users(items, cid)
    
                consumer.commit()
                        
        except Exception as e:
            print(f"Consumer error: {e}", file=sys.stderr)
        finally:
            consumer.close() 

if __name__ == "__main__":
    print(f"Starting consumer for topic: {topic}")
    
    consume_topic(topic)
    