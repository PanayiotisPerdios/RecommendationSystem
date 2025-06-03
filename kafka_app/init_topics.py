from confluent_kafka.admin import AdminClient, NewTopic
import os
import time

bootstrap_servers = os.getenv("BOOTSTRAP_SERVERS", "localhost:9092")

def create_topics():
    admin_client = AdminClient({'bootstrap.servers': bootstrap_servers})
    
    retries = 10
    delay = 3

    for attempt in range(retries):
        try:
            metadata = admin_client.list_topics(timeout=10)
            existing_topics = metadata.topics.keys()
            break
        except Exception as e:
            print(f"[Kafka] Attempt {attempt + 1}/{retries} failed: {e}")
            if attempt == retries - 1:
                raise RuntimeError("Kafka did not become ready in time")
            time.sleep(delay)
    
    topics_to_create = []

    existing_topics = admin_client.list_topics(timeout=10).topics.keys()
    
    required_topics = ["coupons", "events", "users"]
    for topic in required_topics:
        if topic not in existing_topics:
            topics_to_create.append(NewTopic(topic, num_partitions=3, replication_factor=1))
    """
    if "coupons" not in existing_topics:
       topics_to_create.append(NewTopic("coupons", num_partitions=3, replication_factor=1))
    if "events" not in existing_topics:
       topics_to_create.append(NewTopic("events", num_partitions=3, replication_factor=1))
    if "users" not in existing_topics:
       topics_to_create.append(NewTopic("users", num_partitions=3, replication_factor=1))
    """
    
    if topics_to_create:
        fs = admin_client.create_topics(topics_to_create)
        for topic, f in fs.items():
            try:
                f.result()
                print(f"Created topic: {topic}")
            except Exception as e:
                print(f"Failed to create topic {topic}: {e}")
    else:
        print("All topics already exist.")

if __name__ == "__main__":
    create_topics()