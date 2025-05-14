# RecommendationSystem
Assignment for my Systems Programming course

## Prerequisites
- Python 3.x
- pip (Python package manager)
- docker
- docker-compose

## Setup
1. **Clone the repository:**

   ```bash
   git clone https://github.com/PanayiotisPerdios/RecommendationSystem.git
   cd RecommendationSystem
2. **Build containers:**
   ```bash
   docker-compose build
3. **Create and Start containers:**
    ```bash
    docker-compose up -d
    
## Containers/Services used

   ```bash
   recommendation_db #postgres db
   recommendation_app #main app
   recommendation_kafka #Kafka broker
   recommendation_zookeeper #Kafka manager
   recommendation_kafka_ui #Kafka ui
   recommendation_producer_events #dummy producer for events
   recommendation_producer_coupons #dummy producer for coupons
   recommendation_producer_users #dummy producer for users
   recommendation_consumer_events #consumer for events
   recommendation_consumer_coupons #consumer for coupons
   recommendation_consumer_users #consumer for users
   ```
1. **API Endpoints:**
   - **POST /config:** sends a configuration for the recommendations schemas
       
   Example request body:
   ```json
   {
      "recommender_type": "inference",
      "recommendation_schema": {
         "user_id": {"type": "int", "source_field": "id"},
         "bet": {"type": "float", "source_field": "stake"},
         "time": {"type": "float", "source_field": "timestamp"},
         "events": {"type": "list", "source_field": "recommended_events"}
      },
      "timestamp": "2025-04-04T12:00:00"
   }
   ```
   - **GET /recommend/{int:user_id}:** returns a recommendation based on the config sent (configuration is required)
       
   Example response body:
   ```json
   {
      "bet": 31.45,
      "events": [
         {
            "id": 986012,
            "odd": 3.04
         },
         {
            "id": 821667,
            "odd": 2.12
         },
         {
            "id": 279548,
            "odd": 2.62
         }
      ],
      "id": 35326,
      "time": "2025-04-27T17:50:33.923432"
   }
   ```
## Kafka UI
   ```bash
   http://localhost:8080/
   ```
## Closing services
   1. **Stopping services:**
   ```bash
   docker-compose down
   ```
   **Important: once the recommendation_db is down it wipes all data**
   
   2. **Wiping services for rebuild**
   ```bash
   docker-compose down --volumes --remove-orphans
   ```

## Testing
The project includes basic unit tests

To run tests, run:
   ```bash
    python -m unittest discover
   ```
   or 
   ```bash
    coverage run -m unittest discover
   ```
To see test coverage percentege, run:
   ```bash
    coverage report
   ```

       
