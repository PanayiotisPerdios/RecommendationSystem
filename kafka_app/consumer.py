import sys
import json
import os
import threading
from confluent_kafka import Consumer, KafkaException
from app.services import create_events, create_purchased_coupons, create_users
from app import create_app

topic = os.getenv("TOPIC_NAME", "coupons") 

bootstrap_servers = os.getenv("BOOTSTRAP_SERVERS", "localhost:9092")
app = create_app()

def consume_topic(topic):
    with app.app_context():
        consumer = Consumer({'bootstrap.servers': bootstrap_servers,
                             'group.id': f'{topic}-group',
                             'auto.offset.reset': 'earliest'})
        
        consumer.subscribe([topic])
        
        try:
            while True:
                msg = consumer.poll(timeout=3.0)
                if msg is None:
                    continue
                elif msg.error():
                    raise KafkaException(msg.error())
                    
                data = json.loads(msg.value().decode('utf-8'))
                print(f"Message consumed from topic {topic}: {data}")
                
                if topic == "events":
                   create_events([data])
                elif topic == "coupons":
                   create_purchased_coupons([data])
                elif topic == "users":
                   create_users([data])
                
                consumer.commit()
                    
        except Exception as e:
            print(f"Consumer error: {e}", file=sys.stderr)
        finally:
            consumer.close() 

if __name__ == "__main__":
    print(f"Starting consumer for topic: {topic}")
    
    consume_topic(topic)
    