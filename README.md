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
2. **Create a virtual environment (optional but recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
3. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    
## Usage
1. **Docker-compose**
   Start the PostgreSQL container database
   ```bash
   docker-compose up -d
3. **Run the Flask application:**
   ```bash
   python run.py
4. **API Endpoints:**
   - **POST /config:** sends a configuration for the recommendations
       
   Example request body:
   ```json
   {
      "recommender_type": "inference",
      "recommendation_schema": {
         "id": {"type": "int", "source_field": "user_id"},
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
            "event_id": 986012,
            "odd": 3.04
         },
         {
            "event_id": 821667,
            "odd": 2.12
         },
         {
            "event_id": 279548,
            "odd": 2.62
         }
      ],
      "id": 35326,
      "time": "2025-04-27T17:50:33.923432"
   }
   ```
6. **Docker-compose**
   ```bash
   docker-compose down
   ```
   **Important: once the container is down it wipes all data**

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

       
